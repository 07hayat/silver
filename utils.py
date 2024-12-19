import logging
import os
from logging.handlers import RotatingFileHandler
import datetime

# Ensure the logs directory exists
log_dir = "logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# Configure logging with rotation
log_file = os.path.join(log_dir, "bot_activity.log")
handler = RotatingFileHandler(log_file, maxBytes=5 * 1024 * 1024, backupCount=5)  # 5 MB max size, 5 backups
formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
handler.setFormatter(formatter)

logger = logging.getLogger("bot_logger")
logger.setLevel(logging.INFO)
logger.addHandler(handler)

def log(message, max_length=200):
    """
    Logs a message to both the console and the log file.
    Truncates messages longer than `max_length` for cleanliness.
    """
    # Truncate the message if it's too long
    if len(message) > max_length:
        message = message[:max_length] + "..."

    # Format the message with a timestamp
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted_message = f"[{timestamp}] {message}"

    # Log to console and file
    print(formatted_message)
    logger.info(message)  # Log message to the file using the logger

def get_logs(level=None, recent_lines=20):
    """
    Retrieves logs with optional filtering by level and limits to recent lines.
    """
    if not os.path.exists(log_file):
        return ["No logs available."]

    with open(log_file, "r") as f:
        lines = f.readlines()

    # Optional: Filter logs by level
    if level:
        lines = [line for line in lines if f"| {level.upper()} |" in line]

    # Return only the most recent lines
    return lines[-recent_lines:] if lines else ["No logs available."]
