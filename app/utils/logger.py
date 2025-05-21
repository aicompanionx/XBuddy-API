import logging
import sys
import time
from logging.handlers import RotatingFileHandler
from pathlib import Path

from colorama import Fore, Style, init

# Initialize colorama
init()

# Create logs directory
logs_dir = Path(__file__).parent.parent.parent / "logs"
logs_dir.mkdir(exist_ok=True)

# Mapping of log levels to colors
COLORS = {
    "DEBUG": Fore.BLUE,
    "INFO": Fore.GREEN,
    "WARNING": Fore.YELLOW,
    "ERROR": Fore.RED,
    "CRITICAL": Fore.RED + Style.BRIGHT,
}

# Mapping of log levels to emojis
EMOJIS = {"DEBUG": "🔍", "INFO": "✅", "WARNING": "⚠️", "ERROR": "❌", "CRITICAL": "🔥"}

# List of WebSocket connections
web_sockets = []

# List of module names to filter out
FILTERED_MODULES = [
    "uvicorn.error",
    "asyncio",
    "urllib3",
    "httpx",
    "websockets",
    "httpcore",
    "openai",
]


class LogFilter(logging.Filter):
    """Filter out unwanted log modules"""

    def filter(self, record):
        # If the log record's name starts with any of the filtered modules, filter it out
        for module in FILTERED_MODULES:
            if record.name.startswith(module):
                return False
        return True


class ColoredFormatter(logging.Formatter):
    """Custom console log formatter with colors and emojis"""

    def format(self, record):
        # Get the log level
        level_name = record.levelname
        # Add timestamp
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

        # Add color
        colored_level = (
            f"{COLORS.get(level_name, '')}{level_name.ljust(8)}{Style.RESET_ALL}"
        )
        emoji = EMOJIS.get(level_name, "")

        # Construct the formatted log message
        message = f"{Fore.CYAN}{timestamp}{Style.RESET_ALL} {emoji} {colored_level} {Fore.MAGENTA}[{record.name}]{Style.RESET_ALL} - {record.getMessage()}"

        # If there is exception information, add it to the log
        if record.exc_info:
            exception_text = self.formatException(record.exc_info)
            message += f"\n{Fore.RED}Exception:{Style.RESET_ALL}\n{exception_text}"

        return message


class FileFormatter(logging.Formatter):
    """Custom file log formatter without colors"""

    def format(self, record):
        # Add timestamp
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

        # Add emoji
        emoji = EMOJIS.get(record.levelname, "")

        # Construct the formatted log message
        message = f"{timestamp} {emoji} {record.levelname.ljust(8)} [{record.name}] - {record.getMessage()}"

        # If there is exception information, add it to the log
        if record.exc_info:
            exception_text = self.formatException(record.exc_info)
            message += f"\nException:\n{exception_text}"

        return message


def setup_logger():
    """Configure the global logging system"""
    # Create a log filter
    log_filter = LogFilter()

    # Create a console handler
    console_handler = logging.StreamHandler(stream=sys.stdout)
    console_formatter = ColoredFormatter()
    console_handler.setFormatter(console_formatter)
    console_handler.setLevel(logging.DEBUG)
    console_handler.addFilter(log_filter)

    # Create a file handler
    file_handler = RotatingFileHandler(
        logs_dir / "app.log",
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,  # Keep 5 backup files
        encoding="utf-8",
    )
    file_formatter = FileFormatter()
    file_handler.setFormatter(file_formatter)
    file_handler.setLevel(logging.DEBUG)
    file_handler.addFilter(log_filter)

    # Create an error file handler
    error_file_handler = RotatingFileHandler(
        logs_dir / "error.log",
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,  # Keep 5 backup files
        encoding="utf-8",
    )
    error_file_handler.setFormatter(file_formatter)
    error_file_handler.setLevel(logging.ERROR)
    error_file_handler.addFilter(log_filter)

    # Configure the root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)

    # Clear existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Add the new handlers
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(error_file_handler)

    # Set the log level for third-party libraries
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)

    # Disable unwanted log modules
    for module in FILTERED_MODULES:
        logging.getLogger(module).setLevel(logging.CRITICAL)

    # Use a custom logger for FastAPI and Uvicorn
    for logger_name in ["uvicorn", "uvicorn.access", "fastapi"]:
        logger = logging.getLogger(logger_name)
        for h in logger.handlers[:]:
            logger.removeHandler(h)
        logger.propagate = True

    return root_logger


def get_logger(name):
    """Get a logger with the specified name"""
    return logging.getLogger(name)


def register_websocket(websocket):
    """Register a WebSocket connection to receive log messages"""
    if websocket not in web_sockets:
        web_sockets.append(websocket)


def unregister_websocket(websocket):
    """Unregister a WebSocket connection"""
    if websocket in web_sockets:
        web_sockets.remove(websocket)
