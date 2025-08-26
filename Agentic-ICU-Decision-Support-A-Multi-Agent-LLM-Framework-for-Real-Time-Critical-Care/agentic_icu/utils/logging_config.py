"""
Logging configuration for the ICU system
"""

import logging
import sys
from pathlib import Path
from datetime import datetime


def setup_logging(log_level: str = "INFO", log_dir: str = "./logs"):
    """Setup logging configuration"""

    # Create logs directory
    Path(log_dir).mkdir(exist_ok=True)

    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(f"{log_dir}/icu_system_{datetime.now().strftime('%Y%m%d')}.log")
        ]
    )

    logger = logging.getLogger("agentic_icu")
    logger.info("Logging system initialized")

    return logger


def get_logger(name: str):
    """Get a logger for a specific module"""
    return logging.getLogger(f"agentic_icu.{name}")
