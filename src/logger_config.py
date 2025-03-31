import logging
import logging.handlers
import json
import os
import threading
from datetime import datetime


class JsonFormatter(logging.Formatter):
    """Custom formatter to output log records as JSON."""
    def format(self, record):
        log_record = {
            "timestamp": datetime.utcfromtimestamp(record.created).isoformat() + "Z",
            "level": record.levelname,
            "message": record.getMessage(),
            "logger_name": record.name,
            "thread_name": record.threadName,
            "thread_id": record.thread,
            "filename": record.filename,
            "func_name": record.funcName,
            "line_no": record.lineno,
        }
        # Include exception info if available
        if record.exc_info:
            log_record['exc_info'] = self.formatException(record.exc_info)
        if record.stack_info:
            log_record['stack_info'] = self.formatStack(record.stack_info)

        # Add any extra attributes passed to the logger
        extra_attrs = record.__dict__.get('__extra__', {})
        log_record.update(extra_attrs)

        return json.dumps(log_record)


def setup_logging(log_dir="logs", log_file="app.log", level=logging.INFO):
    """
    Configures logging for the application.

    Sets up logging to output to both the console and a rotating file.
    File logs are written in JSON format.

    Args:
        log_dir (str): The directory to store log files. Defaults to "logs".
        log_file (str): The name of the log file. Defaults to "app.log".
        level (int): The minimum logging level to capture. Defaults to logging.INFO.
    """
    # Ensure the log directory exists
    if not os.path.exists(log_dir):
        try:
            os.makedirs(log_dir)
        except OSError as e:
            # Handle potential race condition if directory is created between
            #  check and makedirs
            if not os.path.isdir(log_dir):
                print(f"Error creating log directory {log_dir}: {e}")
                # Fallback or raise error depending on desired behavior
                return

    log_file_path = os.path.join(log_dir, log_file)

    # Get the root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)  # Set the minimum level for the root logger

    # Prevent adding handlers multiple times if setup_logging is called again
    if root_logger.hasHandlers():
        root_logger.handlers.clear()

    # Console Handler (Standard Format)
    console_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - [%(threadName)s] - %(name)s - %(message)s'
    )
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(console_formatter)
    console_handler.setLevel(level)
    # Console handler respects the overall level
    root_logger.addHandler(console_handler)

    # Rotating File Handler (JSON Format)
    # Rotate logs at 5MB, keep 5 backup files
    file_handler = logging.handlers.RotatingFileHandler(
        log_file_path, maxBytes=5*1024*1024, backupCount=5, encoding='utf-8'
    )
    json_formatter = JsonFormatter()
    file_handler.setFormatter(json_formatter)
    file_handler.setLevel(level) # File handler also respects the overall level
    root_logger.addHandler(file_handler)

    logging.info(
        "Logging configured: Console and Rotating File Handler (JSON)."
    )


# Example usage (optional, can be removed or kept for testing)
if __name__ == '__main__':
    setup_logging()
    logging.info("This is an info message.")
    logging.warning("This is a warning message.")
    try:
        1 / 0
    except ZeroDivisionError:
        logging.error(
            "This is an error message with exception info.",
            exc_info=True
        )

    # Example with extra data
    logger = logging.getLogger("MyModule")
    extra_data = {"user_id": 123, "request_id": "abc"}
    # Pass extra data using the 'extra' dictionary
    # Note: To make this work seamlessly with JsonFormatter, we might need
    # to adjust how 'extra' is handled or use LogRecord attributes directly.
    # A simpler way for JsonFormatter is to pass structured data in the
    #  message:
    logger.info({"message": "Processing user request", **extra_data})

    # Example in a thread
    def worker():
        thread_logger = logging.getLogger("WorkerThread")
        thread_logger.info("Message from worker thread.")

    thread = threading.Thread(target=worker, name="MyWorker")
    thread.start()
    thread.join()

    logging.info("Logging setup example finished.")
