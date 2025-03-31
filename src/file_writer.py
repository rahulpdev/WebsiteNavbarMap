import os
import logging
import tempfile
import time

# Assuming utils.py is in the same directory or src is in PYTHONPATH
try:
    from .utils import get_website_name
except ImportError:
    # Fallback for standalone execution or different project structure
    from utils import get_website_name

logger = logging.getLogger(__name__)

OUTPUT_DIR = "output_maps"
LOCK_SUFFIX = ".lock"
STALE_LOCK_THRESHOLD_SECONDS = 300  # 5 minutes


def generate_filename(url):
    """
    Generates the full path for the output markdown file based on the URL.

    Args:
        url (str): The URL of the website.

    Returns:
        str: The full file path (e.g., "output_maps/example_com_nav_map.md").
    """
    website_name = get_website_name(url)
    filename = f"{website_name}_nav_map.md"
    return os.path.join(OUTPUT_DIR, filename)


def _cleanup_stale_lock(lock_file_path):
    """Checks if a lock file is stale and removes it."""
    try:
        lock_mtime = os.path.getmtime(lock_file_path)
        if (time.time() - lock_mtime) > STALE_LOCK_THRESHOLD_SECONDS:
            logger.warning(f"Removing stale lock file: {lock_file_path}")
            os.remove(lock_file_path)
            return True  # Indicate stale lock was removed
    except FileNotFoundError:
        # Lock file doesn't exist, which is fine
        pass
    except OSError as e:
        logger.error(
            f"Error checking/removing stale lock file {lock_file_path}: {e}"
        )
    return False  # Lock not stale or couldn't be removed


def write_map_file(filepath, content):
    """
    Writes the markdown content to the specified file path atomically
    using a temporary file and os.rename, with basic locking.

    Includes stale lock file cleanup.

    Args:
        filepath (str): The target path for the markdown file in OUTPUT_DIR.
        content (str): The markdown content to write.

    Returns:
        bool: True if the write was successful, False otherwise.
    """
    lock_file_path = filepath + LOCK_SUFFIX
    temp_file_path = None  # Initialize to ensure it's defined in finally block

    # 1. Ensure output directory exists
    try:
        os.makedirs(OUTPUT_DIR, exist_ok=True)
    except OSError as e:
        logger.error(f"Failed to create output directory {OUTPUT_DIR}: {e}")
        return False

    # 2. Check for and potentially clean up stale lock
    if os.path.exists(lock_file_path):
        if not _cleanup_stale_lock(lock_file_path):
            logger.warning(
                f"Lock file {lock_file_path} exists and is not stale. Skipping write for {filepath}."
            )
            return False  # Another process might be actively writing

    # 3. Attempt to acquire the lock (create lock file)
    try:
        # Use 'x' mode to create file exclusively, fails if it exists
        with open(lock_file_path, 'x') as lock_file:
            lock_file.write(f"Locked at {time.time()}")
        logger.debug(f"Acquired lock: {lock_file_path}")
    except FileExistsError:
        logger.warning(
            f"Failed to acquire lock (already exists): {lock_file_path}. Skipping write for {filepath}."
        )
        return False
    except IOError as e:
        logger.error(f"Failed to create lock file {lock_file_path}: {e}")
        return False

    # 4. Write to temporary file and rename (Atomic Write)
    try:
        # Create a temporary file in the same directory to ensure rename works
        #  across filesystems
        with tempfile.NamedTemporaryFile(
            mode='w',
            encoding='utf-8',
            delete=False,
            dir=OUTPUT_DIR,
            suffix=".tmp"
        ) as temp_file:
            temp_file_path = temp_file.name
            temp_file.write(content)
            logger.debug(
                f"Content written to temporary file: {temp_file_path}"
            )

        # Atomically rename the temporary file to the target file path
        os.rename(temp_file_path, filepath)
        logger.info(f"Successfully wrote map file: {filepath}")
        return True

    except (IOError, OSError) as e:
        logger.error(
            f"Error writing or renaming file for {filepath}: {e}",
            exc_info=True
        )
        # Clean up temporary file if it still exists
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.remove(temp_file_path)
                logger.debug(
                    f"Removed temporary file after error: {temp_file_path}"
                )
            except OSError as rm_err:
                logger.error(
                    f"Failed to remove temporary file {temp_file_path} after error: {rm_err}"
                )
        return False

    finally:
        # 5. Release the lock (remove lock file)
        if os.path.exists(lock_file_path):
            try:
                os.remove(lock_file_path)
                logger.debug(f"Released lock: {lock_file_path}")
            except OSError as e:
                logger.error(
                    f"Failed to remove lock file {lock_file_path}: {e}"
                )


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

    print("\n--- Testing generate_filename ---")
    test_url = "https://www.example-site.co.uk/path"
    filename = generate_filename(test_url)
    print(f"Generated filename for '{test_url}': {filename}")
    # Expected: output_maps/example_site_co_uk_nav_map.md (or similar based on
    #  get_website_name)

    print("\n--- Testing write_map_file ---")
    test_content = """
https://www.example-site.co.uk/path
├── https://www.example-site.co.uk/path/page1
└── https://www.example-site.co.uk/path/page2
    └── https://www.example-site.co.uk/path/page2/subpage
"""
    if filename:
        success = write_map_file(filename, test_content)
        print(f"Write successful for {filename}: {success}")
        if success and os.path.exists(filename):
            print(f"File content of {filename}:")
            try:
                with open(filename, 'r') as f:
                    print(f.read())
            except IOError as e:
                print(f"Error reading back file: {e}")
            # Clean up the created file
            # os.remove(filename)
            print(
                f"(Note: Test file '{filename}' created. Remove manually if"
                " needed.)"
            )
        else:
            print("File write failed or file not found.")

    print("\n--- Testing Stale Lock Cleanup (Manual Check Required) ---")
    stale_lock_path = os.path.join(OUTPUT_DIR, "stale_test.md.lock")
    try:
        # Create a dummy old lock file
        with open(stale_lock_path, 'w') as f:
            f.write("dummy lock")
        # Set its modification time to be old
        old_time = time.time() - STALE_LOCK_THRESHOLD_SECONDS - 60
        os.utime(stale_lock_path, (old_time, old_time))
        print(f"Created dummy stale lock file: {stale_lock_path}")
        print("Running write_map_file again should clean it up...")
        write_map_file(
            os.path.join(OUTPUT_DIR, "stale_test.md"),
            "test content"
        )
        if not os.path.exists(stale_lock_path):
            print("Stale lock file appears to have been removed.")
        else:
            print("Stale lock file still exists.")
        # Clean up test file if created
        if os.path.exists(os.path.join(OUTPUT_DIR, "stale_test.md")):
            os.remove(os.path.join(OUTPUT_DIR, "stale_test.md"))
        if os.path.exists(stale_lock_path):
            # Clean up lock if somehow not removed
            os.remove(stale_lock_path)

    except Exception as e:
        print(f"Error during stale lock test: {e}")
        # Ensure cleanup even on error
        if os.path.exists(os.path.join(OUTPUT_DIR, "stale_test.md")):
            os.remove(os.path.join(OUTPUT_DIR, "stale_test.md"))
        if os.path.exists(stale_lock_path):
            os.remove(stale_lock_path)
