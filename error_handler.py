"""
Comprehensive Error Handling and Logging System for AI Pentest Brain
Provides structured logging, retry logic, and error recovery
"""

import logging
import time
import functools
from typing import Callable, Any, Optional, Type, Tuple
from enum import Enum
import sys
import traceback


class LogLevel(Enum):
    """Logging levels"""
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL


class ErrorCategory(Enum):
    """Error categories for classification"""
    NETWORK = "network"
    API = "api"
    CONFIGURATION = "configuration"
    VALIDATION = "validation"
    FILESYSTEM = "filesystem"
    DATABASE = "database"
    AUTHENTICATION = "authentication"
    TIMEOUT = "timeout"
    UNKNOWN = "unknown"


class PentestError(Exception):
    """Base exception for pentest errors"""
    def __init__(self, message: str, category: ErrorCategory = ErrorCategory.UNKNOWN, 
                 details: Optional[dict] = None):
        self.message = message
        self.category = category
        self.details = details or {}
        super().__init__(self.message)


class NetworkError(PentestError):
    """Network-related errors"""
    def __init__(self, message: str, details: Optional[dict] = None):
        super().__init__(message, ErrorCategory.NETWORK, details)


class APIError(PentestError):
    """API-related errors"""
    def __init__(self, message: str, details: Optional[dict] = None):
        super().__init__(message, ErrorCategory.API, details)


class ConfigurationError(PentestError):
    """Configuration-related errors"""
    def __init__(self, message: str, details: Optional[dict] = None):
        super().__init__(message, ErrorCategory.CONFIGURATION, details)


class ValidationError(PentestError):
    """Validation-related errors"""
    def __init__(self, message: str, details: Optional[dict] = None):
        super().__init__(message, ErrorCategory.VALIDATION, details)


class StructuredLogger:
    """Structured logging with context and formatting"""
    
    def __init__(self, name: str, log_file: str = "ai_pentest_brain.log"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        
        # Remove existing handlers
        self.logger.handlers = []
        
        # File handler with detailed formatting
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        
        # Console handler with simpler formatting
        # Use UTF-8 encoding on Windows to support emoji/special chars
        if sys.platform == 'win32':
            import io
            console_stream = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
            console_handler = logging.StreamHandler(console_stream)
        else:
            console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter(
            '%(levelname)s: %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def debug(self, message: str, **context):
        """Log debug message with context"""
        self._log(logging.DEBUG, message, context)
    
    def info(self, message: str, **context):
        """Log info message with context"""
        self._log(logging.INFO, message, context)
    
    def warning(self, message: str, **context):
        """Log warning message with context"""
        self._log(logging.WARNING, message, context)
    
    def error(self, message: str, **context):
        """Log error message with context"""
        self._log(logging.ERROR, message, context)
    
    def critical(self, message: str, **context):
        """Log critical message with context"""
        self._log(logging.CRITICAL, message, context)
    
    def _log(self, level: int, message: str, context: dict):
        """Internal logging with context"""
        if context:
            context_str = " | ".join(f"{k}={v}" for k, v in context.items())
            full_message = f"{message} | {context_str}"
        else:
            full_message = message
        
        # Protect against Windows console encoding issues (cp1252 vs UTF-8)
        try:
            self.logger.log(level, full_message)
        except UnicodeEncodeError:
            # Fallback: strip/replace non-ASCII characters for console,
            # but keep full message in file handler (which is UTF-8 safe).
            safe_message = full_message.encode("ascii", errors="replace").decode("ascii")
            self.logger.log(level, safe_message)
    
    def log_exception(self, exc: Exception, message: str = "Exception occurred", **context):
        """Log exception with full traceback"""
        context['exception_type'] = type(exc).__name__
        context['exception_message'] = str(exc)
        
        self.error(message, **context)
        
        # Log full traceback to file only
        tb = traceback.format_exc()
        self.logger.debug(f"Traceback:\n{tb}")


def retry_with_backoff(
    max_retries: int = 3,
    initial_delay: float = 1.0,
    backoff_factor: float = 2.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
    logger: Optional[StructuredLogger] = None
) -> Callable:
    """
    Decorator for retrying functions with exponential backoff
    
    Args:
        max_retries: Maximum number of retry attempts
        initial_delay: Initial delay in seconds
        backoff_factor: Multiplier for delay after each retry
        exceptions: Tuple of exception types to catch
        logger: Optional logger for logging retry attempts
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            delay = initial_delay
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    
                    if attempt < max_retries:
                        if logger:
                            logger.warning(
                                f"Retry attempt {attempt + 1}/{max_retries} for {func.__name__}",
                                error=str(e),
                                delay=delay
                            )
                        time.sleep(delay)
                        delay *= backoff_factor
                    else:
                        if logger:
                            logger.error(
                                f"All {max_retries} retry attempts failed for {func.__name__}",
                                error=str(e)
                            )
            
            # All retries exhausted
            raise last_exception
        
        return wrapper
    return decorator


def handle_errors(
    default_return: Any = None,
    log_errors: bool = True,
    raise_on_error: bool = False,
    error_category: ErrorCategory = ErrorCategory.UNKNOWN,
    logger: Optional[StructuredLogger] = None
) -> Callable:
    """
    Decorator for handling errors gracefully
    
    Args:
        default_return: Value to return on error
        log_errors: Whether to log errors
        raise_on_error: Whether to re-raise exceptions
        error_category: Category of error for classification
        logger: Optional logger for logging errors
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if log_errors and logger:
                    logger.log_exception(
                        e,
                        f"Error in {func.__name__}",
                        category=error_category.value,
                        args=str(args)[:100],
                        kwargs=str(kwargs)[:100]
                    )
                
                if raise_on_error:
                    raise
                
                return default_return
        
        return wrapper
    return decorator


class ErrorRecovery:
    """Error recovery strategies"""
    
    @staticmethod
    def with_fallback(primary_func: Callable, fallback_func: Callable, 
                      logger: Optional[StructuredLogger] = None) -> Any:
        """
        Try primary function, fall back to secondary on error
        
        Args:
            primary_func: Primary function to try
            fallback_func: Fallback function if primary fails
            logger: Optional logger
        """
        try:
            return primary_func()
        except Exception as e:
            if logger:
                logger.warning(
                    f"Primary function failed, using fallback",
                    primary=primary_func.__name__,
                    fallback=fallback_func.__name__,
                    error=str(e)
                )
            return fallback_func()
    
    @staticmethod
    def graceful_degradation(func: Callable, default_value: Any,
                            logger: Optional[StructuredLogger] = None) -> Any:
        """
        Execute function with graceful degradation
        
        Args:
            func: Function to execute
            default_value: Default value on failure
            logger: Optional logger
        """
        try:
            return func()
        except Exception as e:
            if logger:
                logger.warning(
                    f"Function failed, using default value",
                    function=func.__name__,
                    default=str(default_value),
                    error=str(e)
                )
            return default_value


class RateLimiter:
    """Rate limiting for API calls"""
    
    def __init__(self, max_calls: int, time_window: float):
        """
        Initialize rate limiter
        
        Args:
            max_calls: Maximum number of calls allowed
            time_window: Time window in seconds
        """
        self.max_calls = max_calls
        self.time_window = time_window
        self.calls = []
    
    def wait_if_needed(self):
        """Wait if rate limit would be exceeded"""
        now = time.time()
        
        # Remove old calls outside time window
        self.calls = [call_time for call_time in self.calls 
                     if now - call_time < self.time_window]
        
        if len(self.calls) >= self.max_calls:
            # Calculate wait time
            oldest_call = min(self.calls)
            wait_time = self.time_window - (now - oldest_call)
            
            if wait_time > 0:
                time.sleep(wait_time)
                # Clean up again after waiting
                now = time.time()
                self.calls = [call_time for call_time in self.calls 
                             if now - call_time < self.time_window]
        
        # Record this call
        self.calls.append(time.time())


def rate_limited(max_calls: int, time_window: float) -> Callable:
    """
    Decorator for rate limiting function calls
    
    Args:
        max_calls: Maximum number of calls allowed
        time_window: Time window in seconds
    """
    limiter = RateLimiter(max_calls, time_window)
    
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            limiter.wait_if_needed()
            return func(*args, **kwargs)
        
        return wrapper
    return decorator


# Global logger instance
_global_logger = None


def get_logger(name: str = "pentest") -> StructuredLogger:
    """Get or create global logger instance"""
    global _global_logger
    if _global_logger is None:
        _global_logger = StructuredLogger(name)
    return _global_logger


# Example usage and testing
if __name__ == "__main__":
    # Test structured logging
    logger = get_logger("test")
    
    logger.info("Starting test", module="error_handler", test="logging")
    logger.debug("Debug information", value=42, status="ok")
    logger.warning("Warning message", reason="test")
    logger.error("Error message", code=500, details="test error")
    
    # Test retry decorator
    @retry_with_backoff(max_retries=3, initial_delay=0.1, logger=logger)
    def flaky_function(fail_count: int = 2):
        """Function that fails first N times"""
        if not hasattr(flaky_function, 'attempts'):
            flaky_function.attempts = 0
        
        flaky_function.attempts += 1
        
        if flaky_function.attempts <= fail_count:
            raise NetworkError("Simulated network error")
        
        return "Success!"
    
    try:
        result = flaky_function(fail_count=2)
        logger.info("Retry test passed", result=result)
    except Exception as e:
        logger.error("Retry test failed", error=str(e))
    
    # Test error handling decorator
    @handle_errors(default_return="default", logger=logger)
    def error_prone_function():
        raise ValueError("Test error")
    
    result = error_prone_function()
    logger.info("Error handling test", result=result)
    
    # Test rate limiter
    @rate_limited(max_calls=3, time_window=1.0)
    def rate_limited_function():
        return time.time()
    
    logger.info("Testing rate limiter (3 calls per second)")
    for i in range(5):
        start = time.time()
        rate_limited_function()
        elapsed = time.time() - start
        logger.info(f"Call {i+1}", elapsed=f"{elapsed:.3f}s")
    
    logger.info("All tests completed")
