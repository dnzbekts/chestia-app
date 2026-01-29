"""
Logging configuration for Chestia backend.

Provides structured logging with different configurations for development vs production.
"""

import logging
import sys
from typing import Optional


def setup_logging(level: Optional[str] = None) -> None:
    """
    Configure application-wide logging.
    
    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
              If None, uses INFO for production, DEBUG for development
    """
    if level is None:
        level = "INFO"
    
    # Create formatter
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper()))
    
    # Remove existing handlers
    root_logger.handlers.clear()
    
    # Add console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # Set third-party loggers to WARNING to reduce noise
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("langchain").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)


# Initialize logging on module import
setup_logging()
