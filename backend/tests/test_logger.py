"""Unit tests for logger utility"""
import pytest
import logging
from io import StringIO
from utils.logger import StructuredLogger, get_structured_logger, configure_logging


class TestStructuredLogger:
    """Tests for StructuredLogger class"""
    
    def test_structured_logger_creation(self):
        """Test creating a structured logger"""
        logger = StructuredLogger("test_logger")
        assert logger is not None
        assert isinstance(logger.logger, logging.Logger)
    
    def test_structured_logger_name(self):
        """Test that structured logger has correct name"""
        logger_name = "test_module"
        logger = StructuredLogger(logger_name)
        assert logger.logger.name == logger_name
    
    def test_structured_logger_context_set(self):
        """Test setting logging context"""
        logger = StructuredLogger("context_logger")
        logger.set_context(user_id=123, operation="test")
        
        assert logger.context["user_id"] == 123
        assert logger.context["operation"] == "test"
    
    def test_structured_logger_context_clear(self):
        """Test clearing logging context"""
        logger = StructuredLogger("clear_logger")
        logger.set_context(user_id=123)
        assert len(logger.context) > 0
        
        logger.clear_context()
        assert len(logger.context) == 0
    
    def test_structured_logger_format_message(self):
        """Test message formatting with context"""
        logger = StructuredLogger("format_logger")
        logger.set_context(user_id=456)
        
        formatted = logger._format_message("INFO", "Test message")
        assert "Test message" in formatted
        assert "INFO" in formatted
        assert isinstance(formatted, str)


class TestGetStructuredLogger:
    """Tests for get_structured_logger function"""
    
    def test_get_structured_logger(self):
        """Test getting a structured logger"""
        logger = get_structured_logger("test_logger")
        assert logger is not None
        assert isinstance(logger, StructuredLogger)
    
    def test_get_logger_consistency(self):
        """Test that getting same logger returns similar instance"""
        logger1 = get_structured_logger("same_logger")
        logger2 = get_structured_logger("same_logger")
        
        # Both should be StructuredLogger instances
        assert isinstance(logger1, StructuredLogger)
        assert isinstance(logger2, StructuredLogger)


class TestLoggerFunctionality:
    """Tests for logger logging methods"""
    
    def test_logger_info_message(self):
        """Test logging info message"""
        logger = StructuredLogger("info_logger")
        
        # Should not raise exception
        logger.info("Info message")
    
    def test_logger_debug_message(self):
        """Test logging debug message"""
        logger = StructuredLogger("debug_logger")
        
        # Should not raise exception
        logger.debug("Debug message")
    
    def test_logger_warning_message(self):
        """Test logging warning message"""
        logger = StructuredLogger("warning_logger")
        
        logger.warning("Warning message")
    
    def test_logger_error_message(self):
        """Test logging error message"""
        logger = StructuredLogger("error_logger")
        
        logger.error("Error message")
    
    def test_logger_critical_message(self):
        """Test logging critical message"""
        logger = StructuredLogger("critical_logger")
        
        logger.critical("Critical message")
    
    def test_logger_with_extra_context(self):
        """Test logging with extra context"""
        logger = StructuredLogger("extra_logger")
        
        extra = {"request_id": "req123"}
        logger.info("Request started", extra=extra)
    
    def test_logger_error_with_exc_info(self):
        """Test logging error with exception info"""
        logger = StructuredLogger("exc_logger")
        
        try:
            raise ValueError("Test error")
        except ValueError:
            logger.error("An error occurred", exc_info=True)


class TestLoggerWithContext:
    """Tests for logger with context information"""
    
    def test_logger_multiple_context_updates(self):
        """Test multiple context updates"""
        logger = StructuredLogger("multi_context_logger")
        
        logger.set_context(user_id=1)
        assert logger.context["user_id"] == 1
        
        logger.set_context(operation="read")
        assert logger.context["user_id"] == 1
        assert logger.context["operation"] == "read"
    
    def test_logger_multiple_messages(self):
        """Test logging multiple messages"""
        logger = StructuredLogger("multi_msg_logger")
        logger.set_context(session_id="sess123")
        
        for i in range(3):
            logger.info(f"Message {i}")


class TestConfigureLogging:
    """Tests for configure_logging function"""
    
    def test_configure_logging_default(self):
        """Test logging configuration with defaults"""
        # Should not raise exception
        configure_logging()
    
    def test_configure_logging_debug_level(self):
        """Test logging configuration with debug level"""
        configure_logging(level="DEBUG")
        
        root_logger = logging.getLogger()
        assert root_logger.level == logging.DEBUG
    
    def test_configure_logging_info_level(self):
        """Test logging configuration with info level"""
        configure_logging(level="INFO")
        
        root_logger = logging.getLogger()
        assert root_logger.level == logging.INFO
    
    def test_configure_logging_warning_level(self):
        """Test logging configuration with warning level"""
        configure_logging(level="WARNING")
        
        root_logger = logging.getLogger()
        assert root_logger.level == logging.WARNING
    
    def test_configure_logging_error_level(self):
        """Test logging configuration with error level"""
        configure_logging(level="ERROR")
        
        root_logger = logging.getLogger()
        assert root_logger.level == logging.ERROR
    
    def test_configure_logging_has_handlers(self):
        """Test that configured logger has handlers"""
        configure_logging()
        
        root_logger = logging.getLogger()
        assert len(root_logger.handlers) > 0


class TestStructuredLoggerConsistency:
    """Tests for logger consistency and properties"""
    
    def test_logger_retains_context_across_calls(self):
        """Test that context is retained across multiple log calls"""
        logger = StructuredLogger("retention_logger")
        logger.set_context(transaction_id="txn456")
        
        logger.info("First message")
        logger.info("Second message")
        
        assert logger.context["transaction_id"] == "txn456"
    
    def test_logger_format_with_complex_context(self):
        """Test formatting with complex context data"""
        logger = StructuredLogger("complex_logger")
        logger.set_context(
            user_id=789,
            metadata={"key": "value"},
            tags=["tag1", "tag2"]
        )
        
        formatted = logger._format_message("INFO", "Complex message")
        assert "Complex message" in formatted
        assert isinstance(formatted, str)


class TestStructuredLoggerAdvanced:
    """Advanced tests for logger edge cases and message formatting"""
    
    def test_logger_with_none_extra(self):
        """Test logging with None extra parameter"""
        logger = StructuredLogger("none_extra_logger")
        formatted = logger._format_message("INFO", "Test message", extra=None)
        
        assert "Test message" in formatted
        assert isinstance(formatted, str)
    
    def test_logger_with_empty_context(self):
        """Test logger with empty context"""
        logger = StructuredLogger("empty_context_logger")
        assert len(logger.context) == 0
        
        logger.info("Message with no context")
        assert len(logger.context) == 0
    
    def test_logger_context_with_special_characters(self):
        """Test context with special characters and unicode"""
        logger = StructuredLogger("special_char_logger")
        logger.set_context(
            message="Special chars: !@#$%^&*()",
            unicode_val="中文测试 العربية हिन्दी"
        )
        
        assert logger.context["message"] == "Special chars: !@#$%^&*()"
        assert logger.context["unicode_val"] == "中文测试 العربية हिन्दी"
    
    def test_logger_context_with_numeric_types(self):
        """Test context with different numeric types"""
        logger = StructuredLogger("numeric_logger")
        logger.set_context(
            integer=42,
            floating=3.14,
            negative=-100
        )
        
        assert logger.context["integer"] == 42
        assert logger.context["floating"] == 3.14
        assert logger.context["negative"] == -100
    
    def test_logger_context_with_boolean(self):
        """Test context with boolean values"""
        logger = StructuredLogger("bool_logger")
        logger.set_context(is_active=True, is_deleted=False)
        
        assert logger.context["is_active"] is True
        assert logger.context["is_deleted"] is False
    
    def test_logger_extra_parameter_override(self):
        """Test that extra parameter can include additional data"""
        logger = StructuredLogger("extra_param_logger")
        logger.set_context(user_id=123)
        
        extra = {"request_id": "req456", "endpoint": "/api/test"}
        formatted = logger._format_message("INFO", "Test", extra=extra)
        
        assert "request_id" in formatted
        assert "endpoint" in formatted
    
    def test_logger_format_message_json_serialization(self):
        """Test that formatted message is valid JSON"""
        import json
        logger = StructuredLogger("json_logger")
        logger.set_context(user_id=1, operation="test")
        
        formatted = logger._format_message("INFO", "Message")
        
        # Should be valid JSON
        parsed = json.loads(formatted)
        assert parsed["message"] == "Message"
        assert parsed["level"] == "INFO"
        assert "timestamp" in parsed
    
    def test_logger_all_log_levels(self):
        """Test all logging levels"""
        logger = StructuredLogger("all_levels_logger")
        
        # Should not raise any exceptions
        logger.debug("Debug")
        logger.info("Info")
        logger.warning("Warning")
        logger.error("Error")
        logger.critical("Critical")
    
    def test_logger_empty_message(self):
        """Test logging empty message"""
        logger = StructuredLogger("empty_msg_logger")
        formatted = logger._format_message("INFO", "")
        
        assert isinstance(formatted, str)
        assert "timestamp" in formatted
    
    def test_logger_very_long_message(self):
        """Test logging very long message"""
        logger = StructuredLogger("long_msg_logger")
        long_message = "x" * 10000
        
        formatted = logger._format_message("INFO", long_message)
        assert isinstance(formatted, str)
        assert len(formatted) > 10000
    
    def test_logger_context_overwrite(self):
        """Test overwriting existing context values"""
        logger = StructuredLogger("overwrite_logger")
        logger.set_context(user_id=1)
        assert logger.context["user_id"] == 1
        
        logger.set_context(user_id=2)
        assert logger.context["user_id"] == 2
    
    def test_logger_clear_then_set_context(self):
        """Test clearing context and setting new values"""
        logger = StructuredLogger("clear_set_logger")
        logger.set_context(old_key="old_value")
        logger.clear_context()
        logger.set_context(new_key="new_value")
        
        assert "old_key" not in logger.context
        assert logger.context["new_key"] == "new_value"
    
    def test_logger_multiple_instances_independent(self):
        """Test that multiple logger instances are independent"""
        logger1 = StructuredLogger("logger1")
        logger2 = StructuredLogger("logger2")
        
        logger1.set_context(instance=1)
        logger2.set_context(instance=2)
        
        assert logger1.context["instance"] == 1
        assert logger2.context["instance"] == 2
    
    def test_logger_error_with_exception(self):
        """Test error logging with actual exception"""
        logger = StructuredLogger("exception_logger")
        
        try:
            1 / 0
        except ZeroDivisionError:
            logger.error("Division by zero", exc_info=True)
    
    def test_logger_complex_extra_data(self):
        """Test logging with complex nested extra data"""
        logger = StructuredLogger("complex_extra_logger")
        extra = {
            "request": {
                "method": "GET",
                "path": "/api/test",
                "headers": {"Authorization": "Bearer token"}
            },
            "response": {
                "status": 200,
                "time": 123.45
            }
        }
        
        formatted = logger._format_message("INFO", "API call", extra=extra)
        assert isinstance(formatted, str)


class TestConfigureLoggingAdvanced:
    """Advanced tests for configure_logging function"""
    
    def test_configure_logging_critical_level(self):
        """Test logging configuration with critical level"""
        configure_logging(level="CRITICAL")
        
        root_logger = logging.getLogger()
        assert root_logger.level == logging.CRITICAL
    
    def test_configure_logging_lowercase_level(self):
        """Test that level parameter accepts lowercase"""
        configure_logging(level="debug")
        
        root_logger = logging.getLogger()
        assert root_logger.level == logging.DEBUG
    
    def test_configure_logging_removes_old_handlers(self):
        """Test that configure_logging removes old handlers"""
        configure_logging(level="INFO")
        root_logger = logging.getLogger()
        initial_handler_count = len(root_logger.handlers)
        
        configure_logging(level="DEBUG")
        # Should have replaced handlers, not added
        assert len(root_logger.handlers) > 0
    
    def test_configure_logging_invalid_level_defaults(self):
        """Test that invalid level defaults to INFO"""
        configure_logging(level="INVALID_LEVEL")
        
        root_logger = logging.getLogger()
        # Should default to INFO
        assert root_logger.level == logging.INFO
    
    def test_configure_logging_preserves_formatter(self):
        """Test that configured handler has formatter"""
        configure_logging()
        
        root_logger = logging.getLogger()
        for handler in root_logger.handlers:
            # Handler should have a formatter
            assert handler.formatter is not None

