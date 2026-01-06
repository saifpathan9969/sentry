"""
Unit tests for error handling and logging system
"""

import unittest
import time
import logging
import os
from unittest.mock import Mock, patch, MagicMock
from error_handler import (
    StructuredLogger, ErrorCategory, PentestError, NetworkError, APIError,
    ConfigurationError, ValidationError, retry_with_backoff, handle_errors,
    ErrorRecovery, RateLimiter, rate_limited, get_logger
)


class TestStructuredLogger(unittest.TestCase):
    """Test structured logging functionality"""
    
    def setUp(self):
        """Set up test logger"""
        self.test_log_file = "test_error_handler.log"
        self.logger = StructuredLogger("test", self.test_log_file)
    
    def tearDown(self):
        """Clean up test log file"""
        # Close all handlers to release file lock
        for handler in self.logger.logger.handlers[:]:
            handler.close()
            self.logger.logger.removeHandler(handler)
        
        # Small delay to ensure file is released
        time.sleep(0.1)
        
        if os.path.exists(self.test_log_file):
            try:
                os.remove(self.test_log_file)
            except PermissionError:
                pass  # File still locked, skip cleanup
    
    def test_logger_initialization(self):
        """Test logger is properly initialized"""
        self.assertIsNotNone(self.logger.logger)
        self.assertEqual(len(self.logger.logger.handlers), 2)  # File + Console
    
    def test_debug_logging(self):
        """Test debug level logging"""
        self.logger.debug("Debug message", key="value")
        # Should not raise exception
        self.assertTrue(True)
    
    def test_info_logging(self):
        """Test info level logging"""
        self.logger.info("Info message", status="ok")
        self.assertTrue(True)
    
    def test_warning_logging(self):
        """Test warning level logging"""
        self.logger.warning("Warning message", reason="test")
        self.assertTrue(True)
    
    def test_error_logging(self):
        """Test error level logging"""
        self.logger.error("Error message", code=500)
        self.assertTrue(True)
    
    def test_critical_logging(self):
        """Test critical level logging"""
        self.logger.critical("Critical message", severity="high")
        self.assertTrue(True)
    
    def test_logging_with_context(self):
        """Test logging with multiple context values"""
        self.logger.info("Message", key1="value1", key2="value2", key3=123)
        self.assertTrue(True)
    
    def test_logging_without_context(self):
        """Test logging without context"""
        self.logger.info("Simple message")
        self.assertTrue(True)
    
    def test_log_exception(self):
        """Test exception logging"""
        try:
            raise ValueError("Test exception")
        except Exception as e:
            self.logger.log_exception(e, "Exception occurred", module="test")
        
        self.assertTrue(True)
    
    def test_log_file_created(self):
        """Test log file is created"""
        self.logger.info("Test message")
        self.assertTrue(os.path.exists(self.test_log_file))


class TestCustomExceptions(unittest.TestCase):
    """Test custom exception classes"""
    
    def test_pentest_error(self):
        """Test base PentestError"""
        error = PentestError("Test error", ErrorCategory.NETWORK, {"key": "value"})
        self.assertEqual(error.message, "Test error")
        self.assertEqual(error.category, ErrorCategory.NETWORK)
        self.assertEqual(error.details, {"key": "value"})
    
    def test_network_error(self):
        """Test NetworkError"""
        error = NetworkError("Network failed", {"host": "example.com"})
        self.assertEqual(error.category, ErrorCategory.NETWORK)
        self.assertIn("host", error.details)
    
    def test_api_error(self):
        """Test APIError"""
        error = APIError("API failed", {"status": 500})
        self.assertEqual(error.category, ErrorCategory.API)
    
    def test_configuration_error(self):
        """Test ConfigurationError"""
        error = ConfigurationError("Config invalid")
        self.assertEqual(error.category, ErrorCategory.CONFIGURATION)
    
    def test_validation_error(self):
        """Test ValidationError"""
        error = ValidationError("Validation failed")
        self.assertEqual(error.category, ErrorCategory.VALIDATION)


class TestRetryDecorator(unittest.TestCase):
    """Test retry with backoff decorator"""
    
    def test_retry_success_first_attempt(self):
        """Test function succeeds on first attempt"""
        call_count = [0]
        
        @retry_with_backoff(max_retries=3, initial_delay=0.01)
        def success_function():
            call_count[0] += 1
            return "success"
        
        result = success_function()
        self.assertEqual(result, "success")
        self.assertEqual(call_count[0], 1)
    
    def test_retry_success_after_failures(self):
        """Test function succeeds after retries"""
        call_count = [0]
        
        @retry_with_backoff(max_retries=3, initial_delay=0.01)
        def flaky_function():
            call_count[0] += 1
            if call_count[0] < 3:
                raise NetworkError("Temporary failure")
            return "success"
        
        result = flaky_function()
        self.assertEqual(result, "success")
        self.assertEqual(call_count[0], 3)
    
    def test_retry_all_attempts_fail(self):
        """Test all retry attempts fail"""
        call_count = [0]
        
        @retry_with_backoff(max_retries=2, initial_delay=0.01)
        def always_fails():
            call_count[0] += 1
            raise NetworkError("Always fails")
        
        with self.assertRaises(NetworkError):
            always_fails()
        
        self.assertEqual(call_count[0], 3)  # Initial + 2 retries
    
    def test_retry_with_specific_exceptions(self):
        """Test retry only catches specific exceptions"""
        @retry_with_backoff(max_retries=2, initial_delay=0.01, 
                           exceptions=(NetworkError,))
        def specific_exception():
            raise ValueError("Different exception")
        
        with self.assertRaises(ValueError):
            specific_exception()
    
    def test_retry_backoff_timing(self):
        """Test exponential backoff timing"""
        call_times = []
        
        @retry_with_backoff(max_retries=2, initial_delay=0.1, backoff_factor=2.0)
        def timed_function():
            call_times.append(time.time())
            if len(call_times) < 3:
                raise NetworkError("Retry")
            return "success"
        
        timed_function()
        
        # Check delays are approximately correct
        self.assertGreaterEqual(call_times[1] - call_times[0], 0.09)  # ~0.1s
        self.assertGreaterEqual(call_times[2] - call_times[1], 0.18)  # ~0.2s


class TestErrorHandlingDecorator(unittest.TestCase):
    """Test error handling decorator"""
    
    def test_handle_errors_returns_default(self):
        """Test decorator returns default value on error"""
        @handle_errors(default_return="default")
        def failing_function():
            raise ValueError("Error")
        
        result = failing_function()
        self.assertEqual(result, "default")
    
    def test_handle_errors_success(self):
        """Test decorator allows success"""
        @handle_errors(default_return="default")
        def success_function():
            return "success"
        
        result = success_function()
        self.assertEqual(result, "success")
    
    def test_handle_errors_with_logging(self):
        """Test decorator logs errors"""
        logger = Mock()
        
        @handle_errors(default_return=None, logger=logger)
        def failing_function():
            raise ValueError("Test error")
        
        result = failing_function()
        self.assertIsNone(result)
        logger.log_exception.assert_called_once()
    
    def test_handle_errors_raise_on_error(self):
        """Test decorator can re-raise exceptions"""
        @handle_errors(raise_on_error=True)
        def failing_function():
            raise ValueError("Error")
        
        with self.assertRaises(ValueError):
            failing_function()
    
    def test_handle_errors_no_logging(self):
        """Test decorator without logging"""
        @handle_errors(default_return="default", log_errors=False)
        def failing_function():
            raise ValueError("Error")
        
        result = failing_function()
        self.assertEqual(result, "default")


class TestErrorRecovery(unittest.TestCase):
    """Test error recovery strategies"""
    
    def test_with_fallback_primary_success(self):
        """Test fallback when primary succeeds"""
        primary = Mock(return_value="primary")
        fallback = Mock(return_value="fallback")
        
        result = ErrorRecovery.with_fallback(primary, fallback)
        
        self.assertEqual(result, "primary")
        primary.assert_called_once()
        fallback.assert_not_called()
    
    def test_with_fallback_primary_fails(self):
        """Test fallback when primary fails"""
        primary = Mock(side_effect=ValueError("Error"))
        fallback = Mock(return_value="fallback")
        
        result = ErrorRecovery.with_fallback(primary, fallback)
        
        self.assertEqual(result, "fallback")
        primary.assert_called_once()
        fallback.assert_called_once()
    
    def test_graceful_degradation_success(self):
        """Test graceful degradation on success"""
        func = Mock(return_value="success")
        
        result = ErrorRecovery.graceful_degradation(func, "default")
        
        self.assertEqual(result, "success")
    
    def test_graceful_degradation_failure(self):
        """Test graceful degradation on failure"""
        func = Mock(side_effect=ValueError("Error"))
        
        result = ErrorRecovery.graceful_degradation(func, "default")
        
        self.assertEqual(result, "default")


class TestRateLimiter(unittest.TestCase):
    """Test rate limiting functionality"""
    
    def test_rate_limiter_initialization(self):
        """Test rate limiter initialization"""
        limiter = RateLimiter(max_calls=5, time_window=1.0)
        self.assertEqual(limiter.max_calls, 5)
        self.assertEqual(limiter.time_window, 1.0)
        self.assertEqual(len(limiter.calls), 0)
    
    def test_rate_limiter_allows_calls_within_limit(self):
        """Test rate limiter allows calls within limit"""
        limiter = RateLimiter(max_calls=3, time_window=1.0)
        
        start = time.time()
        for _ in range(3):
            limiter.wait_if_needed()
        elapsed = time.time() - start
        
        # Should complete quickly (no waiting)
        self.assertLess(elapsed, 0.1)
    
    def test_rate_limiter_enforces_limit(self):
        """Test rate limiter enforces limit"""
        limiter = RateLimiter(max_calls=2, time_window=0.5)
        
        start = time.time()
        for _ in range(3):
            limiter.wait_if_needed()
        elapsed = time.time() - start
        
        # Third call should wait ~0.5 seconds
        self.assertGreaterEqual(elapsed, 0.4)
    
    def test_rate_limited_decorator(self):
        """Test rate limited decorator"""
        call_times = []
        
        @rate_limited(max_calls=2, time_window=0.5)
        def limited_function():
            call_times.append(time.time())
            return "called"
        
        for _ in range(3):
            limited_function()
        
        # First two calls should be fast, third should wait
        self.assertLess(call_times[1] - call_times[0], 0.1)
        self.assertGreaterEqual(call_times[2] - call_times[0], 0.4)


class TestGlobalLogger(unittest.TestCase):
    """Test global logger functionality"""
    
    def test_get_logger_creates_instance(self):
        """Test get_logger creates logger instance"""
        logger = get_logger("test")
        self.assertIsInstance(logger, StructuredLogger)
    
    def test_get_logger_returns_same_instance(self):
        """Test get_logger returns same instance"""
        logger1 = get_logger("test1")
        logger2 = get_logger("test2")
        # Both should return the same global instance
        self.assertEqual(id(logger1), id(logger2))


class TestErrorCategories(unittest.TestCase):
    """Test error category enum"""
    
    def test_error_categories_exist(self):
        """Test all error categories are defined"""
        categories = [
            ErrorCategory.NETWORK,
            ErrorCategory.API,
            ErrorCategory.CONFIGURATION,
            ErrorCategory.VALIDATION,
            ErrorCategory.FILESYSTEM,
            ErrorCategory.DATABASE,
            ErrorCategory.AUTHENTICATION,
            ErrorCategory.TIMEOUT,
            ErrorCategory.UNKNOWN
        ]
        
        for category in categories:
            self.assertIsInstance(category, ErrorCategory)
    
    def test_error_category_values(self):
        """Test error category values"""
        self.assertEqual(ErrorCategory.NETWORK.value, "network")
        self.assertEqual(ErrorCategory.API.value, "api")
        self.assertEqual(ErrorCategory.CONFIGURATION.value, "configuration")


if __name__ == '__main__':
    unittest.main()
