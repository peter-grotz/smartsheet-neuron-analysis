"""
Configuration module for Smartsheet Analysis Tool

Centralized configuration management with validation and defaults.
"""

import os
import logging
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class ConfigError(Exception):
    """Custom exception for configuration errors"""
    pass

class Config:
    """Configuration settings for the Smartsheet API Visualizer"""
    
    # Smartsheet API settings
    SMARTSHEET_ACCESS_TOKEN = os.getenv('SMARTSHEET_ACCESS_TOKEN')
    DEFAULT_SHEET_ID = os.getenv('DEFAULT_SHEET_ID')
    
    # Visualization settings
    DEFAULT_CHART_WIDTH = int(os.getenv('CHART_WIDTH', '12'))
    DEFAULT_CHART_HEIGHT = int(os.getenv('CHART_HEIGHT', '8'))
    DEFAULT_DPI = int(os.getenv('DPI', '300'))
    
    # Output settings - Code Ocean expects /results directory
    OUTPUT_DIR = os.getenv('OUTPUT_DIR', '/results')
    
    # Analysis settings
    DEFAULT_PLOT_FORMAT = os.getenv('DEFAULT_PLOT_FORMAT', 'svg')
    MAX_SAMPLES_TO_DISPLAY = int(os.getenv('MAX_SAMPLES_DISPLAY', '50'))
    
    # Sheet settings
    DEFAULT_SHEET_NAME = os.getenv('DEFAULT_SHEET_NAME', 'Neuron Reconstructions')
    
    @classmethod
    def validate_config(cls) -> bool:
        """
        Validate that required configuration is present and valid
        
        Returns:
            True if configuration is valid
            
        Raises:
            ConfigError: If required configuration is missing or invalid
        """
        errors = []
        
        # Required settings
        if not cls.SMARTSHEET_ACCESS_TOKEN:
            errors.append("SMARTSHEET_ACCESS_TOKEN is required. Please set it in your environment variables.")
        
        # Validate numeric settings
        try:
            if cls.DEFAULT_CHART_WIDTH <= 0:
                errors.append("CHART_WIDTH must be positive")
        except (ValueError, TypeError):
            errors.append("CHART_WIDTH must be a valid number")
            
        try:
            if cls.DEFAULT_CHART_HEIGHT <= 0:
                errors.append("CHART_HEIGHT must be positive")
        except (ValueError, TypeError):
            errors.append("CHART_HEIGHT must be a valid number")
            
        try:
            if cls.DEFAULT_DPI <= 0:
                errors.append("DPI must be positive")
        except (ValueError, TypeError):
            errors.append("DPI must be a valid number")
        
        # Validate plot format
        valid_formats = {'svg', 'png', 'html', 'pdf', 'jpeg'}
        if cls.DEFAULT_PLOT_FORMAT not in valid_formats:
            errors.append(f"DEFAULT_PLOT_FORMAT must be one of: {valid_formats}")
        
        if errors:
            raise ConfigError("Configuration validation failed:\n" + "\n".join(f"- {error}" for error in errors))
        
        # Create output directory if it doesn't exist
        cls._ensure_output_directory()
        
        return True
    
    @classmethod
    def _ensure_output_directory(cls) -> None:
        """Create output directory if it doesn't exist"""
        try:
            Path(cls.OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
        except Exception as e:
            raise ConfigError(f"Failed to create output directory '{cls.OUTPUT_DIR}': {e}")
    
    @classmethod
    def get_logger(cls, name: str = 'smartsheet_analysis', level: int = logging.INFO) -> logging.Logger:
        """
        Get a configured logger instance
        
        Args:
            name: Logger name
            level: Logging level
            
        Returns:
            Configured logger
        """
        logger = logging.getLogger(name)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(level)
        
        return logger
    
    @classmethod
    def print_config_summary(cls) -> None:
        """Print a summary of current configuration"""
        print("Configuration Summary:")
        print(f"  Output Directory: {cls.OUTPUT_DIR}")
        print(f"  Default Plot Format: {cls.DEFAULT_PLOT_FORMAT}")
        print(f"  Chart Dimensions: {cls.DEFAULT_CHART_WIDTH}x{cls.DEFAULT_CHART_HEIGHT}")
        print(f"  DPI: {cls.DEFAULT_DPI}")
        print(f"  Default Sheet: {cls.DEFAULT_SHEET_NAME}")
        print(f"  API Token: {'Set' if cls.SMARTSHEET_ACCESS_TOKEN else 'Not Set'}") 