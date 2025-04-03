import re
import time
import random
import logging
import functools
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


def get_website_name(url):
    """
    Generates a filesystem-safe name from a URL, including the first path segment.

    Removes scheme, combines domain and first path segment, replaces common
    separators with underscores, and removes potentially problematic characters.

    Args:
        url (str): The URL to process.

    Returns:
        str: A filesystem-safe string derived from the URL's domain and first path,
             or "invalid_url" if the URL is malformed.
    """
    if not url:
        return "invalid_url"
    try:
        parsed_url = urlparse(url)
        domain = parsed_url.netloc
        path = parsed_url.path.strip('/') # Get path and remove leading/trailing slashes

        if not domain:
            # Fallback if netloc is empty (less common for http/https)
            # Attempt to use the first part of the path as domain if path exists
            path_parts = path.split('/')
            domain = path_parts[0] if path else ''
            if not domain:
                return "invalid_url" # Still no usable part
            # Adjust path if the first part was used as domain
            path = '/'.join(path_parts[1:])

        # Sanitize domain
        if domain.startswith("www."):
            domain = domain[4:]
        sanitized_domain = domain.replace('.', '_').replace('-', '_')
        sanitized_domain = re.sub(r'[^\w_]+', '', sanitized_domain).lower()

        if not sanitized_domain:
             # If domain sanitization results in empty, return error
             # Example: URL like "http://.../" might lead here if path fallback fails
             return "sanitized_domain_empty"

        # Process first path segment
        sanitized_segment = ""
        if path:
            path_segments = path.split('/')
            # Ensure path_segments is not empty and the first segment is not empty
            if path_segments and path_segments[0]:
                first_segment = path_segments[0]
                # Sanitize the first segment
                sanitized_segment = first_segment.replace('.', '_').replace('-', '_')
                sanitized_segment = re.sub(r'[^\w_]+', '', sanitized_segment).lower()

        # Combine domain and segment if segment exists and is not empty
        if sanitized_segment:
            safe_name = f"{sanitized_domain}_{sanitized_segment}"
        else:
            safe_name = sanitized_domain

        # Final check for empty result after potential segment processing
        if not safe_name:
            # This case should be rare if sanitized_domain was valid
            return "sanitized_name_empty"

        return safe_name

    except Exception as e:
        logger.error(f"Error parsing URL '{url}' for website name: {e}")
        return "invalid_url_parsing_error"


def retry_with_backoff(
        retries=3,
        initial_delay: float = 1.0,
        backoff_factor: float = 2.0,
        jitter: float = 0.1,
        retry_exceptions=(Exception,)
        ):
    """
    Decorator for retrying a function with exponential backoff and jitter.

    Args:
        retries (int): Maximum number of retries.
        initial_delay (float): Initial delay in seconds.
        backoff_factor (float): Factor to multiply delay by for each retry.
        jitter (float): Factor to add random jitter to delay (delay * jitter).
        retry_exceptions (tuple): Tuple of exception types to retry on.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            delay = initial_delay
            for i in range(retries + 1):  # Try once + number of retries
                try:
                    return func(*args, **kwargs)
                except retry_exceptions as e:
                    if i == retries:
                        logger.error(
                            f"Function '{func.__name__}' failed after {retries} retries. Last error: {e}",
                            exc_info=True
                            # Include stack trace for the final failure
                        )
                        raise  # Re-raise the last exception
                    else:
                        # Calculate delay with backoff and jitter
                        current_jitter = random.uniform(
                            -jitter * delay,
                            jitter * delay
                        )
                        wait_time = delay + current_jitter
                        # Ensure wait_time is not negative
                        wait_time = max(0, wait_time)

                        logger.warning(
                            f"Function '{func.__name__}' failed with {type(e).__name__}: {e}. "
                            f"Retrying in {wait_time:.2f} seconds... (Attempt {i + 1}/{retries})"
                        )
                        time.sleep(wait_time)
                        delay *= backoff_factor
        return wrapper
    return decorator


# Example usage (optional)
if __name__ == '__main__':
    # Configure logging for standalone testing
    from logger_config import setup_logging
    setup_logging(level=logging.DEBUG)

    print("\n--- Testing get_website_name ---")
    urls_to_test = [
        "https://www.example.com/path?query=1",
        "http://test-site.org",
        "https://sub.domain.co.uk:8080/another/page/",
        "invalid-url",
        "",
        None,
        "http://192.168.1.1/admin",
        "https://xn--bcher-kva.example/"  # Punycode
    ]
    for test_url in urls_to_test:
        print(
            f"get_website_name('{test_url}') -> '{get_website_name(test_url)}'"
        )

    print("\n--- Testing retry_with_backoff ---")
    fail_count = 0

    @retry_with_backoff(
            retries=3,
            initial_delay=0.1,
            retry_exceptions=(ValueError, IOError)
            )
    def potentially_failing_function(succeed_after):
        global fail_count  # Use global for module-level scope in __main__
        print(
            f"Calling potentially_failing_function (attempt {fail_count + 1})..."
        )
        if fail_count < succeed_after:
            fail_count += 1
            raise ValueError(f"Simulated failure #{fail_count}")
        else:
            print("Function succeeded!")
            return "Success"

    print("\nTest 1: Should succeed after 2 failures")
    fail_count = 0
    try:
        result = potentially_failing_function(succeed_after=2)
        print(f"Result: {result}")
    except Exception as e:
        print(f"Caught exception: {e}")

    print("\nTest 2: Should fail after 4 attempts (1 initial + 3 retries)")
    fail_count = 0
    try:
        result = potentially_failing_function(succeed_after=5)
        # Will always fail
        print(f"Result: {result}")
    except Exception as e:
        print(f"Caught expected exception: {type(e).__name__}: {e}")

    print("\nTest 3: Should not retry on TypeError")
    fail_count = 0

    @retry_with_backoff(
            retries=2,
            initial_delay=0.1,
            retry_exceptions=(ValueError,)
            )
    def raises_type_error():

        print("Calling raises_type_error...")
        raise TypeError("This should not be retried")

    try:
        raises_type_error()
    except Exception as e:
        print(f"Caught expected exception: {type(e).__name__}: {e}")
