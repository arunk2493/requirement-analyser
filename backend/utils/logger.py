"""Logging utilities for structured and consistent logging"""
import logging
import json
from typing import Any, Dict, Optional
from datetime import datetime


class StructuredLogger:
    """Wrapper for structured logging with context"""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.context: Dict[str, Any] = {}
    
    def set_context(self, **kwargs) -> None:
        """Set logging context"""
        self.context.update(kwargs)
    
    def clear_context(self) -> None:
        """Clear logging context"""
        self.context.clear()
    
    def _format_message(self, level: str, message: str, extra: Optional[Dict] = None) -> str:
        """Format log message with context"""
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "message": message,
            **self.context,
            **(extra or {})
        }
        return json.dumps(log_data, default=str)
    
    def info(self, message: str, extra: Optional[Dict] = None) -> None:
        """Log info level message"""
        self.logger.info(self._format_message("INFO", message, extra))
    
    def debug(self, message: str, extra: Optional[Dict] = None) -> None:
        """Log debug level message"""
        self.logger.debug(self._format_message("DEBUG", message, extra))
    
    def warning(self, message: str, extra: Optional[Dict] = None) -> None:
        """Log warning level message"""
        self.logger.warning(self._format_message("WARNING", message, extra))
    
    def error(self, message: str, extra: Optional[Dict] = None, exc_info: bool = False) -> None:
        """Log error level message"""
        self.logger.error(
            self._format_message("ERROR", message, extra),
            exc_info=exc_info
        )
    
    def critical(self, message: str, extra: Optional[Dict] = None) -> None:
        """Log critical level message"""
        self.logger.critical(self._format_message("CRITICAL", message, extra))


def get_structured_logger(name: str) -> StructuredLogger:
    """Get structured logger instance"""
    return StructuredLogger(name)


def configure_logging(level: str = "INFO", json_format: bool = False) -> None:
    """
    Configure root logger settings.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        json_format: Whether to use JSON formatting
    """
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Add console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
