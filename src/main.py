import logging
import sys
from urllib.parse import urlparse

# Assuming src is in PYTHONPATH or running from project root
try:
    from logger_config import setup_logging
    from csv_processor import load_all_valid_urls
    from concurrency_manager import ConcurrencyManager
except ImportError as e:
    print(
        f"Error importing modules: {e}. Ensure src is in PYTHONPATH or run from project root.", 
        file=sys.stderr
    )
    sys.exit(1)

# Setup logging as early as possible
# Using default log level INFO, adjust if needed
setup_logging()
logger = logging.getLogger(__name__)


def display_url_options(url_selector_list):
    """Displays a numbered list of website domains for user selection."""
    print("\nPlease select a website to generate the navigation map for:")
    print("-" * 60)
    for i, (url, _) in enumerate(url_selector_list):
        try:
            # Display domain name for clarity
            domain = urlparse(url).netloc or url
            # Fallback to full URL if parse fails
            print(f"{i + 1}: {domain}")
        except Exception:
            print(f"{i + 1}: {url} (Error parsing domain)")
            # Display full URL on error
    print("-" * 60)
    print(
        "Enter the number corresponding to the website, or type 'exit' to quit:"
    )


def get_user_selection(num_options):
    """Prompts the user for selection and validates input."""
    while True:
        user_input = input("> ").strip().lower()
        if user_input == 'exit':
            return None  # Signal to exit
        try:
            selection = int(user_input)
            if 1 <= selection <= num_options:
                return selection - 1  # Return 0-based index
            else:
                print(
                    f"Invalid number. Please enter a number between 1 and {num_options}."
                    )
        except ValueError:
            print("Invalid input. Please enter a number or 'exit'.")


def main():
    """Main execution function."""
    logger.info("Application started.")

    # Load valid URL and selector pairs from CSVs in the input directory
    # The load function now returns list of (url, selector) tuples
    url_selector_pairs = load_all_valid_urls(directory="input_csvs")

    if not url_selector_pairs:
        print(
            "No valid URLs found in the 'input_csvs' directory. Please check your CSV files."
        )
        logger.warning("Exiting: No valid URLs found.")
        sys.exit(0)

    # Display options to the user
    display_url_options(url_selector_pairs)

    # Get user selection
    selected_index = get_user_selection(len(url_selector_pairs))

    if selected_index is None:
        print("Exiting application.")
        logger.info("User requested exit.")
        sys.exit(0)

    # Get the selected URL and selector
    selected_url, selected_selector = url_selector_pairs[selected_index]
    logger.info(
        f"User selected: {selected_index + 1} ({selected_url}) with selector '{selected_selector}'"
        )

    # Initialize the concurrency manager
    # For processing a single selected URL, concurrency might seem overkill,
    # but the manager handles the worker task logic nicely.
    # We could potentially adapt this later to process multiple selections or
    #  all URLs.
    manager = ConcurrencyManager(max_workers=1)
    # Use 1 worker for single selection

    print(f"\nProcessing selected website: {selected_url}")
    logger.info(f"Submitting task for {selected_url} to ConcurrencyManager.")

    # Submit the single selected task
    # process_tasks expects a list
    results = manager.process_tasks([(selected_url, selected_selector)])

    # Process and display results (should be only one result)
    if results:
        result = results[0]
        status = result.get('status', 'error')
        url = result.get('url', selected_url) # Fallback to selected URL
        if status == 'success':
            filepath = result.get('filepath', 'N/A')
            print(f"\nSuccessfully generated navigation map for {url}")
            print(f"Output file: {filepath}")
            logger.info(
                f"Task completed successfully for {url}. Output: {filepath}"
            )
        elif status == 'dlq':
            error_msg = result.get('error', 'Unknown error')
            print(
                f"\nProcessing failed for {url} after retries. Error logged to DLQ."
            )
            print(f"Error details: {error_msg}")
            logger.error(
                f"Task failed and moved to DLQ for {url}. Error: {error_msg}"
            )
        else:  # status == 'error' or unknown
            error_msg = result.get('error', 'Unknown processing error')
            print(f"\nAn unexpected error occurred while processing {url}.")
            print(f"Error details: {error_msg}")
            logger.error(
                f"Task failed with unexpected error for {url}. Error: {error_msg}"
            )
    else:
        print("\nNo results returned from processing.")
        logger.error(
            "ConcurrencyManager returned no results for the submitted task."
        )

    # Shutdown the concurrency manager
    manager.shutdown()
    logger.info("Application finished.")


if __name__ == '__main__':
    main()
