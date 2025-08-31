 # src/utils/logging_config.py
import logging
import sys
from typing import Optional
from src.config.settings import settings

def setup_logging(name: str, log_level: Optional[str] = None) -> logging.Logger:
    """
    Set up logging with a consistent format.
    
    Args:
        name: Name of the logger
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    
    Returns:
        Configured logger instance
    """
    if log_level is None:
        log_level = settings.LOG_LEVEL
    
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Create console handler if not already configured
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    return logger
