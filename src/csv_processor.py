import csv
import logging
import os
from urllib.parse import urlparse

# Get a logger instance for this module
logger = logging.getLogger(__name__)


def find_csv_files(directory):
    """
    Finds all CSV files in the specified directory.

    Args:
        directory (str): The path to the directory to search.

    Returns:
        list: A list of full file paths for CSV files found.
    """
    csv_files = []
    if not os.path.isdir(directory):
        logger.error(
            f"Input directory not found or is not a directory: {directory}"
            )
        return csv_files

    try:
        for filename in os.listdir(directory):
            if filename.lower().endswith(".csv"):
                full_path = os.path.join(directory, filename)
                if os.path.isfile(full_path):
                    csv_files.append(full_path)
                    logger.debug(f"Found CSV file: {full_path}")
    except OSError as e:
        logger.error(f"Error listing directory {directory}: {e}")

    if not csv_files:
        logger.warning(f"No CSV files found in directory: {directory}")

    return csv_files


def validate_url(url_string):
    """
    Validates if a string is a well-formed HTTP/HTTPS URL.

    Args:
        url_string (str): The string to validate.

    Returns:
        bool: True if the URL is valid, False otherwise.
    """
    if not isinstance(url_string, str) or not url_string:
        return False
    try:
        result = urlparse(url_string)
        # Check for scheme (http/https) and netloc (domain name)
        return all([result.scheme in ['http', 'https'], result.netloc])
    except ValueError:
        # urlparse can raise ValueError for malformed URLs (though less common
        #  now)
        logger.debug(
            f"URL validation failed due to ValueError for: {url_string}"
        )
        return False


def process_csv_file(filepath):
    """
    Reads a single CSV file, validates URLs, and extracts valid ones.
    Assumes CSV format: url,css_selector (header optional, only 'url' column
      used).

    Args:
        filepath (str): The path to the CSV file.

    Returns:
        list: A list of tuples `(url, css_selector)` for valid rows.
    """
    valid_rows = []
    try:
        with open(filepath, mode='r', newline='', encoding='utf-8') as csvfile:
            # Sniff to detect dialect and header presence
            try:
                has_header = csv.Sniffer().has_header(csvfile.read(1024))
                csvfile.seek(0)  # Rewind after sniffing
                reader = csv.reader(csvfile)
                if has_header:
                    next(reader)  # Skip header row
            except csv.Error:
                # Could not determine header, assume no header and reset
                logger.warning(
                    f"Could not determine CSV header presence in {filepath}. "
                    "Assuming no header."
                )
                csvfile.seek(0)
                reader = csv.reader(csvfile)

            for i, row in enumerate(reader, start=2 if has_header else 1):
                # Adjust line number based on header
                if not row:  # Skip empty rows
                    continue
                url_cell = row[0].strip() if len(row) > 0 else ""
                selector_cell = row[1].strip() if len(row) > 1 else ""
                # Get selector

                if not selector_cell:
                    logger.warning(
                         f"Missing CSS selector in {os.path.basename(filepath)}"
                         ":{i} for URL '{url_cell}'. Skipping row."
                    )
                    continue  # Skip row if selector is missing

                if validate_url(url_cell):
                    valid_rows.append((url_cell, selector_cell))
                    logger.debug(
                        f"Validated row: ('{url_cell}', '{selector_cell}') "
                        "from {os.path.basename(filepath)}:{i}"
                    )
                else:
                    logger.warning(
                        f"Invalid URL format found in {os.path.basename(filepath)}:{i}: '{row[0]}'. Skipping row."
                    )  # Log original value

    except FileNotFoundError:
        logger.error(f"CSV file not found: {filepath}")
    except IOError as e:
        logger.error(f"Error reading CSV file {filepath}: {e}")
    except csv.Error as e:
        logger.error(f"CSV parsing error in file {filepath}: {e}")
    except Exception as e:
        logger.error(
            f"Unexpected error processing CSV file {filepath}: {e}",
            exc_info=True
        )

    return valid_rows


def load_all_valid_urls(directory="input_csvs"):
    """
    Loads and validates URLs from all CSV files in the specified directory.

    Args:
        directory (str): The directory containing CSV files. Defaults to
          "input_csvs".

    Returns:
        list: A consolidated list of unique (by URL) tuples `(url,
         css_selector)`.
            If a URL appears multiple times with different selectors,
             only the first encountered pair is kept.
    """
    all_valid_data = {}
    # Use dict to store url -> selector, ensuring URL uniqueness
    csv_files = find_csv_files(directory)

    if not csv_files:
        logger.warning(
            f"No CSV files found or accessible in {directory}. "
            "Cannot load URLs."
        )
        return []

    for filepath in csv_files:
        logger.info(f"Processing CSV file: {filepath}")
        rows_from_file = process_csv_file(filepath)
        for url, selector in rows_from_file:
            if url not in all_valid_data:
                # Keep first encountered selector for a unique URL
                all_valid_data[url] = selector
            else:
                logger.debug(
                    f"Duplicate URL '{url}' found in {os.path.basename(filepath)}. Keeping first encountered selector '{all_valid_data[url]}'."
                )

    # Convert dict back to list of tuples
    result_list = list(all_valid_data.items())
    logger.info(
        f"Loaded {len(result_list)} unique valid URL/selector pairs from {len(csv_files)} CSV file(s)."
    )
    return result_list


# Example usage (optional)
if __name__ == '__main__':
    # Configure logging for standalone testing
    from logger_config import setup_logging
    setup_logging(level=logging.DEBUG)

    # Create dummy CSV files for testing
    DUMMY_DIR = "temp_input_csvs"
    if not os.path.exists(DUMMY_DIR):
        os.makedirs(DUMMY_DIR)
    with open(os.path.join(DUMMY_DIR, "test1.csv"), "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["url", "css_selector"])
        writer.writerow(["https://example.com", ".nav"])
        writer.writerow(["http://test.org/path", "#menu"])
        writer.writerow(["invalid-url", ""])
        writer.writerow(["https://anotherexample.net", ".main-nav"])
    with open(os.path.join(DUMMY_DIR, "test2.csv"), "w", newline="") as f:
        writer = csv.writer(f)
        # No header
        writer.writerow(["https://example.com", ".nav"])  # Duplicate URL
        writer.writerow(["ftp://badscheme.com", ""])
        writer.writerow(["https://yetanotherexample.com", "nav ul"])

    # Test the functions
    print("\n--- Testing find_csv_files ---")
    found_files = find_csv_files(DUMMY_DIR)
    print(f"Found files: {found_files}")

    print("\n--- Testing validate_url ---")
    print(
        f"validate_url('https://good.com'): {validate_url('https://good.com')}"
    )
    print(
        f"validate_url('http://good.com'): {validate_url('http://good.com')}"
    )
    print(f"validate_url('ftp://bad.com'): {validate_url('ftp://bad.com')}")
    print(f"validate_url('just-text'): {validate_url('just-text')}")
    print(f"validate_url(''): {validate_url('')}")
    print(f"validate_url(None): {validate_url(None)}")

    print("\n--- Testing process_csv_file ---")
    if found_files:
        rows1 = process_csv_file(found_files[0])
        print(f"Valid rows from {os.path.basename(found_files[0])}: {rows1}")
        rows2 = process_csv_file(found_files[1])
        print(f"Valid rows from {os.path.basename(found_files[1])}: {rows2}")

    print("\n--- Testing load_all_valid_urls ---")
    all_data = load_all_valid_urls(DUMMY_DIR)
    print(f"All unique valid URL/selector pairs: {all_data}")

    # Clean up dummy files/dir
    # import shutil
    # shutil.rmtree(DUMMY_DIR)
    print(
        f"\n(Note: Dummy files/dir '{DUMMY_DIR}' were created for testing. "
        "Remove manually if needed.)"
    )
