import sys

from loguru import logger

# Configure the logger
logger.remove()
logger.add(sys.stderr, level="INFO")  # You can set the desired log level here
logger.add("/app/logs/app.log", rotation="50 MB", level="WARNING")  # Log to a file with rotation

# Export the logger for use in other modules
__all__ = ["logger"]
