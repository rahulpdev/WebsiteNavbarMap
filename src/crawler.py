import logging
import requests
import time  # Add missing import for test block
# Removed duplicate logging, requests imports
from bs4 import BeautifulSoup  # Removed unused SoupStrainer
from urllib.parse import urljoin, urlparse
from collections import deque
from tqdm import tqdm  # Import tqdm for progress bar

# Assuming utils.py is in the same directory or src is in PYTHONPATH
try:
    from .utils import retry_with_backoff, get_website_name
except ImportError:
    # Fallback for standalone execution or different project structure
    from utils import retry_with_backoff  # Removed unused get_website_name


logger = logging.getLogger(__name__)


# Define specific exceptions to retry on for network requests

# Define specific exceptions to retry on for network requests
NETWORK_RETRY_EXCEPTIONS = (
    requests.exceptions.Timeout,
    requests.exceptions.ConnectionError,
    requests.exceptions.ChunkedEncodingError,
    requests.exceptions.RequestException  # Catch broader RequestExceptions too
)


@retry_with_backoff(retries=3, initial_delay=1, backoff_factor=2, jitter=0.1,
                    retry_exceptions=NETWORK_RETRY_EXCEPTIONS)
def fetch_html(url):
    """
    Fetches HTML content from a URL with retry logic.

    Args:
        url (str): The URL to fetch.

    Returns:
        str: The HTML content as text, or None if fetching fails after retries.
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        # Allow redirects, set a reasonable timeout
        response = requests.get(
            url, headers=headers,
            timeout=15,
            allow_redirects=True
        )
        response.raise_for_status()
        # Raise HTTPError for bad responses (4xx or 5xx)
        # Ensure content type is HTML before returning
        content_type = response.headers.get('content-type', '').lower()
        if 'html' in content_type:
            logger.debug(f"Successfully fetched HTML from {url}")
            return response.text
        else:
            logger.warning(f"Content type for {url} is not HTML ({content_type}). Skipping.")
            return None
    except requests.exceptions.HTTPError as e:
        logger.error(
            f"HTTP error fetching {url}: {e.response.status_code} {e.response.reason}"
        )
        return None
    except requests.exceptions.RequestException as e:
        # This exception is caught by the decorator for retries,
        # but we log it here if it persists after retries or if it's not in
        #  RETRY_EXCEPTIONS
        logger.error(f"Request exception fetching {url}: {e}")
        # The decorator will raise the exception if retries are exhausted
        raise  # Re-raise for the decorator to handle retries


def find_nav_links(html_content, base_url, css_selector):
    """
    Finds navigation links within the specified CSS selector in HTML content.

    Args:
        html_content (str): The HTML content to parse.
        base_url (str): The base URL for resolving relative links.
        css_selector (str): The CSS selector for the main navigation container.

    Returns:
        list: A list of tuples, where each tuple is (link_text, absolute_url).
            Returns an empty list if the selector is not found or parsing
             fails.
    """
    links = []
    if not html_content or not css_selector:
        return links

    try:
        # Use SoupStrainer for potentially faster parsing if only targeting
        #  one area
        # strainer = SoupStrainer(css_select=css_selector) # Requires newer
        #  bs4? Using select instead.
        soup = BeautifulSoup(html_content, 'html.parser')

        # Find the navigation container(s)
        nav_elements = soup.select(css_selector)
        if not nav_elements:
            logger.warning(
                f"CSS selector '{css_selector}' not found in the page: {base_url}"
            )
            return links

        # Extract links from all found navigation elements
        for nav_element in nav_elements:
            for a_tag in nav_element.find_all('a', href=True):
                href = a_tag['href'].strip()
                link_text = a_tag.get_text(strip=True) or href
                # Use href if text is empty

                if href and not href.startswith(('#', 'javascript:', 'mailto:')):
                    absolute_url = urljoin(base_url, href)
                    # Basic validation to ensure it's still within the same
                    #  site (optional, can be strict)
                    # if urlparse(absolute_url).netloc ==
                    #  urlparse(base_url).netloc:
                    links.append((link_text, absolute_url))

        logger.debug(
            f"Found {len(links)} potential nav links using selector '{css_selector}' on {base_url}"
        )

    except Exception as e:
        logger.error(
            f"Error parsing HTML or finding links with selector '{css_selector}' on {base_url}: {e}", exc_info=True
        )

    # Simple deduplication based on URL
    unique_links = []
    seen_urls = set()
    for text, url in links:
        if url not in seen_urls:
            unique_links.append((text, url))
            seen_urls.add(url)

    return unique_links


def crawl_navigation(start_url, css_selector):
    """
    Crawls the navigation menu starting from a URL.

    Args:
        start_url (str): The initial URL to crawl.
        css_selector (str): The CSS selector for the navigation container.

    Returns:
        dict: A nested dictionary representing the navigation tree,
            e.g., {url: {'name': link_text, 'children': {}}}, or None if
             crawling fails.
    """
    logger.info(f"Starting navigation crawl for {start_url} using selector '{css_selector}'")
    nav_tree = {}
    queue = deque([(start_url, nav_tree)])
    # Queue stores (url_to_crawl, parent_node_in_tree)
    visited = {start_url}
    start_domain = urlparse(start_url).netloc
    initial_queue_size = len(queue) # For tqdm total, though queue size changes

    # Wrap the loop with tqdm for progress visualization
    # Note: Total might be inaccurate as queue grows, but gives an indication.
    # Using unit='URL' for clarity. Leave=False cleans up bar on completion.
    with tqdm(
        total=initial_queue_size,
        desc=f"Crawling {start_domain}",
        unit="URL",
        leave=False
    ) as pbar:
        while queue:
            current_url, parent_node = queue.popleft()
            pbar.set_description(f"Processing {current_url[-50:]}")
            # Show current URL (truncated)
            logger.debug(f"Processing URL: {current_url}")

            # --- Start of indented block ---
            html = fetch_html(current_url)
            if not html:
                logger.warning(
                    f"Failed to fetch HTML for {current_url}, skipping."
                )
                continue  # Skip this URL if fetching failed

            links = find_nav_links(html, current_url, css_selector)
            if not links:
                logger.debug(
                    f"No navigation links found on {current_url} with selector '{css_selector}'."
                )
                # Even if no links found here, the page itself might be a valid
                #  node
                # We need to ensure the start_url gets added if it wasn't already
                #  a child
                if current_url == start_url and not parent_node:
                    # This logic needs refinement - how do we get the 'name' for
                    #  the start_url itself?
                    # For now, we assume the start_url is the root and its
                    #  children are added below.
                    # The structure might need a dedicated root node.
                    pass
                    # Root is implicitly handled by the initial nav_tree structure

            for link_text, link_url in links:
                # Basic check to stay on the same domain
                if urlparse(link_url).netloc != start_domain:
                    logger.debug(f"Skipping off-domain link: {link_url}")
                    continue

                if link_url not in visited:
                    visited.add(link_url)
                    logger.debug(
                        f"Adding new link to queue: {link_url} (from {current_url})"
                    )
                    # Add the new node to the parent's children
                    new_node = {'name': link_text, 'children': {}}
                    parent_node[link_url] = new_node
                    # Add the new URL to the queue to crawl its children
                    queue.append((link_url, new_node['children']))
                    pbar.total += 1
                    # Increment total as we add new URLs to the queue
                # else: # If already visited, do not add it again to enforce a
                #  strict tree structure.
                #     logger.debug(f"Skipping already visited link: {link_url}
                #  (found under {current_url})")
                pbar.update(1)
            # --- End of indented block ---
            # Update progress bar after processing one URL from the queue

    # The initial nav_tree might be empty if the start_url fetch failed.
    # We need a way to represent the root node itself. Let's wrap the result.
    # root_name = get_website_name(start_url) # Unused variable
    final_tree = {start_url: {'name': start_url, 'children': nav_tree}}

    if not final_tree[start_url]['children']:
        logger.warning(
            f"Crawl finished for {start_url}, but no navigation links were successfully processed."
        )
        # Return the root node even if empty, or None? Let's return the root.

    logger.info(
        f"Finished navigation crawl for {start_url}. Visited {len(visited)} unique URLs."
    )
    return final_tree


def _format_tree_recursive(node_dict, indent=""):
    """Helper function to recursively format the navigation tree."""
    output = ""
    children = list(node_dict.items())
    for i, (url, node_data) in enumerate(children):
        is_last = (i == len(children) - 1)
        prefix = indent + ("└── " if is_last else "├── ")
        # Use URL as the primary identifier in the tree as per brief example
        output += f"{prefix}{url}\n"
        if node_data.get('children'):
            new_indent = indent + ("    " if is_last else "│   ")
            output += _format_tree_recursive(node_data['children'], new_indent)
    return output


def format_tree(nav_data):
    """
    Formats the crawled navigation data into a markdown tree string.

    Args:
        nav_data (dict): The nested dictionary from crawl_navigation.

    Returns:
        str: A string representing the navigation tree in markdown format.
    """
    if not nav_data:
        return "Navigation tree data is empty."

    # Expecting the structure {start_url: {'name': ..., 'children': {...}}}
    root_url = list(nav_data.keys())[0]
    root_node = nav_data[root_url]

    # Start with the root URL
    output = f"{root_url}\n"
    # Recursively format its children
    output += _format_tree_recursive(root_node.get('children', {}))

    return output.strip()  # Remove trailing newline if any


# Example usage (optional)
if __name__ == '__main__':
    # Configure logging for standalone testing
    try:
        from logger_config import setup_logging
        setup_logging(level=logging.DEBUG)
    except ImportError:
        logging.basicConfig(
            level=logging.DEBUG, format='%(asctime)s - %(levelname)s - [%(threadName)s] - %(name)s - %(message)s'
        )
        logging.warning("logger_config not found, using basicConfig.")

    # --- Mocking for testing ---
    MOCK_HTML = {
        "https://example.com": """
            <html><head><title>Example</title></head><body>
            <nav id="main-nav">
                <ul>
                    <li><a href="/about">About Us</a></li>
                    <li><a href="/services">Services</a>
                        <ul>
                            <li><a href="/services/web">Web Dev</a></li>
                            <li><a href="/services/mobile">Mobile Dev</a></li>
                        </ul>
                    </li>
                    <li><a href="https://offsite.com">Offsite</a></li>
                    <li><a href="/contact">Contact</a></li>
                    <li><a href="/about">About Us Duplicate</a></li>
                </ul>
            </nav>
            </body></html>
        """,
        "https://example.com/about": """
            <html><body><h1>About Page</h1><nav id="main-nav">...</nav></body></html>
        """,
        "https://example.com/services": """
            <html><body><h1>Services Page</h1>
            <nav id="main-nav">
                 <ul><li><a href="/services/web">Web Dev</a></li></ul>
            </nav></body></html>
        """,
         "https://example.com/services/web": """
            <html><body><h1>Web Dev Page</h1></body></html>
        """,
         "https://example.com/services/mobile": """
             <html><body><h1>Mobile Dev Page</h1></body></html>
         """,
         "https://example.com/contact": """
             <html><body><h1>Contact Page</h1></body></html>
         """
    }

    original_fetch_html = fetch_html

    def mock_fetch_html(url):
        logger.debug(f"[MOCK] Fetching {url}")
        time.sleep(0.05)  # Simulate network delay
        if url in MOCK_HTML:
            return MOCK_HTML[url]
        else:
            logger.warning(f"[MOCK] URL not found in mock data: {url}")
            # Simulate a 404 by returning None or raising an exception the
            #  decorator handles
            # raise requests.exceptions.HTTPError(response=requests.Response())
            # Needs more setup
            return None

    # Replace the real fetch_html with the mock version for testing
    globals()['fetch_html'] = mock_fetch_html
    # --- End Mocking ---

    print("\n--- Testing find_nav_links ---")
    test_html = MOCK_HTML["https://example.com"]
    test_base_url = "https://example.com"
    test_selector = "#main-nav"
    found_links = find_nav_links(test_html, test_base_url, test_selector)
    print(f"Links found for selector '{test_selector}':")
    for text, url in found_links:
        print(f"  - '{text}' -> {url}")

    print("\n--- Testing crawl_navigation ---")
    start_url_test = "https://example.com"
    nav_structure = crawl_navigation(start_url_test, test_selector)
    # print("Crawled Structure (raw dict):")
    # import json
    # print(json.dumps(nav_structure, indent=2))

    print("\n--- Testing format_tree ---")
    markdown_tree = format_tree(nav_structure)
    print("Formatted Markdown Tree:")
    print(markdown_tree)

    # Restore original function if needed (though not critical in __main__)
    globals()['fetch_html'] = original_fetch_html
    print(
        "\n(Note: Used mock data for testing crawl_navigation and format_tree)"
    )
