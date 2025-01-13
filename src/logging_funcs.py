# Function to set up a logger for a specific channel, saving logs in streamer_logs folder
import logging
import os


def setup_channel_logger(channel_name: str):
    # Log file in streamer_logs folder
    log_filename = os.path.join("streamer_logs", f"{channel_name}.log")
    logger = logging.getLogger(channel_name)

    # Check if the logger already has handlers to avoid duplicates
    if not logger.hasHandlers():
        # You can adjust the level (e.g., INFO, WARNING, etc.)
        logger.setLevel(logging.DEBUG)

        # Create a file handler to write to the channel's log file
        file_handler = logging.FileHandler(log_filename, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)

        # Create a log formatter and attach it to the file handler
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        file_handler.setFormatter(formatter)

        # Add the handler to the logger
        logger.addHandler(file_handler)

    return logger


# This function will return a logger for the specific channel
def get_logger_for_channel(channel_name: str):
    return setup_channel_logger(channel_name)
