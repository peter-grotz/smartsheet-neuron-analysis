"""
Utilities module for common functions and logging configuration
"""

import logging
import os
from typing import Optional

# Constants
DEFAULT_LOG_LEVEL = logging.INFO
DEFAULT_LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# Status constants for neuron reconstruction
NEURON_STATUSES = {
    'COMPLETED': 'Completed',
    'PENDING_REVIEW': 'Pending Review',
    'HOLD': 'Hold',
    'UNTRACEABLE': 'Untraceable',
    'IN_PROGRESS': 'In Progress',
    'INCOMPLETE': 'Incomplete'
}

# Plot color scheme
PLOT_COLORS = {
    'Completed': '#2E8B57',      # Sea green
    'Pending_Review': '#FFD700',  # Gold  
    'Hold': '#FF6347',           # Tomato
    'Untraceable': '#696969',    # Dim gray
    'In_Progress': '#4169E1',    # Royal blue
    'Incomplete': '#FFA500',     # Orange
    'Other': '#DDA0DD'           # Plum
}

def setup_logging(level: int = DEFAULT_LOG_LEVEL, log_file: Optional[str] = None) -> logging.Logger:
    """
    Set up logging configuration
    
    Args:
        level: Logging level (default: INFO)
        log_file: Optional file to write logs to
    
    Returns:
        Configured logger
    """
    # Create logger
    logger = logging.getLogger('smartsheet_analysis')
    logger.setLevel(level)
    
    # Avoid adding multiple handlers if already configured
    if logger.handlers:
        return logger
    
    # Create formatter
    formatter = logging.Formatter(DEFAULT_LOG_FORMAT)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler (optional)
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger

def validate_required_columns(df, required_columns: list, logger: Optional[logging.Logger] = None) -> list:
    """
    Validate that required columns exist in DataFrame
    
    Args:
        df: DataFrame to validate
        required_columns: List of required column names
        logger: Optional logger for warnings
    
    Returns:
        List of missing columns
    """
    missing_cols = [col for col in required_columns if col not in df.columns]
    
    if missing_cols and logger:
        logger.warning(f"Missing columns: {missing_cols}")
        logger.info(f"Available columns: {list(df.columns)}")
    
    return missing_cols

def create_output_directory(output_dir: str, logger: Optional[logging.Logger] = None) -> None:
    """
    Create output directory if it doesn't exist
    
    Args:
        output_dir: Directory path to create
        logger: Optional logger for info messages
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        if logger:
            logger.info(f"Created output directory: {output_dir}") 