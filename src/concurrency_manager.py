import concurrent.futures
import logging
import os
import json
import time
import random  # Add missing import for test block
from functools import partial

# Assuming other modules are importable
try:
    from .crawler import crawl_navigation, format_tree
    from .file_writer import generate_filename, write_map_file
    from .utils import retry_with_backoff
    # Although worker might handle retries internally
except ImportError:
    # Fallback for potential standalone testing or structure issues
    from crawler import crawl_navigation, format_tree
    from file_writer import generate_filename, write_map_file
    from utils import retry_with_backoff

logger = logging.getLogger(__name__)

DEFAULT_MAX_WORKERS = min(32, (os.cpu_count() or 1) + 4)
DLQ_FILE = "dlq.log"  # Dead Letter Queue file


def log_to_dlq(failed_task_info):
    """Logs persistently failed task information to the DLQ file."""
    try:
        with open(DLQ_FILE, 'a', encoding='utf-8') as f:
            f.write(json.dumps(failed_task_info) + '\n')
        logger.error(
            f"Task failed permanently and logged to DLQ: {failed_task_info.get('url','N/A')}"
        )
    except IOError as e:
        logger.error(
            f"Failed to write to Dead Letter Queue file {DLQ_FILE}: {e}"
        )


def process_single_url_task(url, css_selector):
    """
    Worker function to process a single URL: crawl, format, write.
    Includes retry logic implicitly via crawler's fetch_html.
    Handles exceptions and determines if task succeeded, failed, or needs DLQ.

    Args:
        url (str): The URL to process.
        css_selector (str): The CSS selector for navigation.

    Returns:
        dict: A result dictionary containing status, url, and message/filepath.
              Example: {'status': 'success', 'url': url, 'filepath': filepath}
                       {'status': 'failed', 'url': url, 'error': str(e)}
                       {'status': 'dlq', 'url': url, 'error': str(e)}
    """
    task_info = {
        'url': url, 'css_selector': css_selector, 'timestamp': time.time()
    }
    logger.info(f"Starting processing for URL: {url}")

    try:
        # 1. Crawl navigation
        # Note: fetch_html within crawl_navigation already has retries
        nav_data = crawl_navigation(url, css_selector)
        if nav_data is None:
            # Crawling itself might fail definitively (e.g., invalid start URL
            #  after retries)
            # Or it might return an empty structure if no links found, which
            #  isn't necessarily a failure
            # Let's assume None return means definitive failure for now.
            raise ValueError(
                "Crawl navigation returned None, indicating failure."
            )
        if not list(nav_data.values())[0]['children']:
            logger.warning(f"Crawl for {url} completed but found no links.")
            # Decide if this is success or failure - let's treat as success
            #  with empty map for now.

        # 2. Format tree
        markdown_content = format_tree(nav_data)
        if markdown_content == "Navigation tree data is empty.":
            logger.warning(f"Formatted tree is empty for {url}.")
            # Still treat as success, write empty file? Or skip write?
            #  Let's write.

        # 3. Generate filename
        filepath = generate_filename(url)

        # 4. Write map file (includes atomic write & locking)
        write_success = write_map_file(filepath, markdown_content)

        if write_success:
            logger.info(
                f"Successfully processed and wrote map for URL: {url} to {filepath}"
            )
            return {'status': 'success', 'url': url, 'filepath': filepath}
        else:
            # File writing failed despite crawl success (e.g., lock contention,
            #  permissions)
            # This might be transient or persistent. Let's treat as failure
            #  for now.
            raise IOError(f"Failed to write map file for {url} to {filepath}")

    except Exception as e:
        # Catch any exception during the process
        logger.error(f"Processing failed for URL {url}: {e}", exc_info=True)
        # Decide if this error warrants DLQ or just failure
        # For now, let's log all persistent errors to DLQ after retries fail
        #  (retries are in fetch_html)
        task_info['error'] = str(e)
        log_to_dlq(task_info)
        return {'status': 'dlq', 'url': url, 'error': str(e)}


class ConcurrencyManager:
    """Manages concurrent execution of URL processing tasks."""

    def __init__(self, max_workers=DEFAULT_MAX_WORKERS):
        self.max_workers = max_workers
        # Using ThreadPoolExecutor as tasks are I/O bound (network,
        #  file writes)
        self.executor = concurrent.futures.ThreadPoolExecutor(
            max_workers=self.max_workers
        )
        self.futures = []
        logger.info(
            f"ConcurrencyManager initialized with max_workers={self.max_workers}"
        )

    def submit_task(self, url, css_selector):
        """Submits a single URL processing task to the executor."""
        if not url or not css_selector:
            logger.warning(
                "Attempted to submit task with empty URL or selector."
            )
            return

        logger.debug(f"Submitting task for URL: {url}")
        # Use partial to pass arguments to the worker function
        # task_func = partial(process_single_url_task, url=url,
        #  css_selector=css_selector)
        # Or submit directly:
        future = self.executor.submit(
            process_single_url_task, url,
            css_selector
        )
        self.futures.append(future)

    def process_tasks(self, url_selector_list):
        """
        Submits multiple tasks and waits for their completion.

        Args:
            url_selector_list (list): A list of tuples, where each tuple is 
            (url, css_selector).

        Returns:
            list: A list of result dictionaries from each completed task.
        """
        results = []
        self.futures = []  # Clear previous futures if any

        for url, css_selector in url_selector_list:
            self.submit_task(url, css_selector)

        # Wait for all submitted futures to complete and collect results
        for future in concurrent.futures.as_completed(self.futures):
            try:
                result = future.result() # Get the result dict from the worker
                results.append(result)
                logger.debug(f"Task completed: {result}")
            except Exception as e:
                # This shouldn't ideally happen if worker catches exceptions,
                # but catch it just in case.
                logger.error(
                    f"Exception retrieving future result: {e}",
                    exc_info=True
                )
                # How to associate this error back to a URL? Difficult here.
                results.append(
                    {'status': 'error', 'url': 'unknown', 'error': str(e)}
                )

        logger.info(
            f"Finished processing all submitted tasks. Results count: {len(results)}"
        )
        return results

    def shutdown(self, wait=True):
        """Shuts down the thread pool executor."""
        logger.info(
            f"Shutting down ConcurrencyManager executor (wait={wait})..."
        )
        self.executor.shutdown(wait=wait)
        logger.info("ConcurrencyManager executor shut down.")


# Example usage (optional)
if __name__ == '__main__':
    # Configure logging for standalone testing
    try:
        from logger_config import setup_logging
        setup_logging(level=logging.DEBUG)
    except ImportError:
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s - %(levelname)s - [%(threadName)s] - %(name)s - %(message)s'
        )
        logging.warning("logger_config not found, using basicConfig.")

    # Mock dependencies for testing
    def mock_crawl_navigation(url, css_selector):
        logger.info(f"[MOCK CM] Crawling {url} with {css_selector}")
        time.sleep(random.uniform(0.1, 0.5))  # Simulate work
        if "failcrawl" in url:
            raise ValueError("Simulated crawl failure")
        if "emptylinks" in url:
            return {url: {'name': url, 'children': {}}}
        # Simulate no links found
        # Simulate successful crawl with some data
        return {url: {'name': url, 'children': {f"{url}/page1": {'name': 'Page 1', 'children': {}}}}}

    def mock_format_tree(nav_data):
        logger.info(f"[MOCK CM] Formatting tree...")
        if not list(nav_data.values())[0]['children']:
            return "Empty Tree"
        return f"{list(nav_data.keys())[0]}\n└── {list(list(nav_data.values())[0]['children'].keys())[0]}"

    def mock_generate_filename(url):
        name = url.split('//')[1].replace('/', '_').replace('.', '_')
        return os.path.join("output_maps", f"{name}_map.md")

    def mock_write_map_file(filepath, content):
        logger.info(f"[MOCK CM] Writing to {filepath}")
        time.sleep(0.05) # Simulate write
        if "failwrite" in filepath:
            logger.error(f"[MOCK CM] Simulated write failure for {filepath}")
            return False
        print(
            f"--- MOCK WRITE to {filepath} ---\n{content}\n----------------------------"
        )
        return True

    # Replace real functions with mocks for this test run
    crawl_navigation = mock_crawl_navigation
    format_tree = mock_format_tree
    generate_filename = mock_generate_filename
    write_map_file = mock_write_map_file

    print("\n--- Testing ConcurrencyManager ---")
    manager = ConcurrencyManager(max_workers=3)

    tasks_to_run = [
        ("https://site1.com", "#nav1"),
        ("https://site2.com/emptylinks", ".menu"),
        ("https://site3.com/failcrawl", "nav"),  # Should fail crawl -> DLQ
        ("https://site4.com", "#main"),
        ("https://site5.com/failwrite", ".nav"),  # Should fail write -> DLQ
        ("https://site6.com", "ul.nav"),
    ]

    print(f"Submitting {len(tasks_to_run)} tasks...")
    results = manager.process_tasks(tasks_to_run)

    print("\n--- Task Results ---")
    success_count = 0
    fail_count = 0
    dlq_count = 0
    for res in results:
        print(
            f"  URL: {res.get('url', 'N/A')}, Status: {res.get('status', 'error')}, Info: {res.get('filepath') or res.get('error')}"
        )
        if res.get('status') == 'success':
            success_count += 1
        elif res.get('status') == 'dlq':
            dlq_count += 1
        else:
            fail_count += 1  # Includes 'error' status

    print(
        f"\nSummary: Success={success_count}, Failed(DLQ)={dlq_count}, Errors={fail_count}"
    )

    # Check if DLQ file was created (optional)
    if os.path.exists(DLQ_FILE):
        print(f"\nDLQ file '{DLQ_FILE}' created. Contents:")
        try:
            with open(DLQ_FILE, 'r') as f:
                for line in f:
                    print(f"  - {line.strip()}")
            # Clean up DLQ file after test
            # os.remove(DLQ_FILE)
            print(
                f"(Note: DLQ file '{DLQ_FILE}' created. "
                "Remove manually if needed.)"
            )
        except IOError as e:
            print(f"Error reading DLQ file: {e}")

    manager.shutdown()
    print("\nConcurrencyManager test finished.")
