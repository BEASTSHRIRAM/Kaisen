"""
Centralized error handling for the Kaisen Log Collection Backend.

This module provides error categorization, logging utilities, and
standardized error handling patterns for all components.

Requirements validated:
- 10.1: Log errors with timestamp, component name, and error message
- 10.2: Continue operation after non-critical errors
- 10.3: Terminate gracefully for critical errors
"""

import logging
import sys
from enum import Enum
from typing import Optional, Callable, Any
from functools import wraps


logger = logging.getLogger(__name__)


class ErrorCategory(Enum):
    """
    Error categories for the log collection system.
    
    CRITICAL: System-terminating errors (model loading failure, unsupported OS)
    RECOVERABLE: System continues with degraded functionality (metric collection failure)
    WARNING: System continues normally (command not whitelisted, invalid config value)
    """
    CRITICAL = "critical"
    RECOVERABLE = "recoverable"
    WARNING = "warning"


class LogCollectionError(Exception):
    """Base exception for log collection system."""
    
    def __init__(self, message: str, category: ErrorCategory, component: str):
        """
        Initialize a log collection error.
        
        Args:
            message: Error description
            category: Error category (CRITICAL, RECOVERABLE, WARNING)
            component: Name of the component where error occurred
        """
        self.message = message
        self.category = category
        self.component = component
        super().__init__(self.message)


class CriticalError(LogCollectionError):
    """Critical error that requires system termination."""
    
    def __init__(self, message: str, component: str):
        super().__init__(message, ErrorCategory.CRITICAL, component)


class RecoverableError(LogCollectionError):
    """Recoverable error that allows system to continue with degraded functionality."""
    
    def __init__(self, message: str, component: str):
        super().__init__(message, ErrorCategory.RECOVERABLE, component)


def log_error(category: ErrorCategory, component: str, message: str, 
              exception: Optional[Exception] = None) -> None:
    """
    Log an error with standardized format including timestamp, component, and message.
    
    Args:
        category: Error category (CRITICAL, RECOVERABLE, WARNING)
        component: Name of the component where error occurred
        message: Error description
        exception: Optional exception object for stack trace
    
    Requirements:
        - 10.1: Log errors with timestamp, component name, and error message
    """
    log_message = f"[{component}] {message}"
    
    if category == ErrorCategory.CRITICAL:
        logger.critical(log_message, exc_info=exception)
    elif category == ErrorCategory.RECOVERABLE:
        logger.error(log_message, exc_info=exception)
    else:  # WARNING
        logger.warning(log_message, exc_info=exception)


def handle_critical_error(component: str, message: str, 
                         exception: Optional[Exception] = None) -> None:
    """
    Handle a critical error by logging and terminating the system gracefully.
    
    Args:
        component: Name of the component where error occurred
        message: Error description
        exception: Optional exception object
    
    Requirements:
        - 10.3: Terminate gracefully for critical errors
    """
    log_error(ErrorCategory.CRITICAL, component, message, exception)
    logger.critical(f"[{component}] System terminating due to critical error")
    sys.exit(1)


def handle_recoverable_error(component: str, message: str, 
                            exception: Optional[Exception] = None,
                            default_value: Any = None) -> Any:
    """
    Handle a recoverable error by logging and returning a default value.
    
    Args:
        component: Name of the component where error occurred
        message: Error description
        exception: Optional exception object
        default_value: Value to return for recovery
    
    Returns:
        The default_value to allow system to continue
    
    Requirements:
        - 10.2: Continue operation after non-critical errors
    """
    log_error(ErrorCategory.RECOVERABLE, component, message, exception)
    logger.info(f"[{component}] Continuing with default value: {default_value}")
    return default_value


def handle_warning(component: str, message: str, 
                  exception: Optional[Exception] = None) -> None:
    """
    Handle a warning by logging without interrupting operation.
    
    Args:
        component: Name of the component where error occurred
        message: Error description
        exception: Optional exception object
    """
    log_error(ErrorCategory.WARNING, component, message, exception)


def with_error_handling(component: str, critical: bool = False, 
                       default_value: Any = None):
    """
    Decorator for adding standardized error handling to functions.
    
    Args:
        component: Name of the component
        critical: If True, errors are treated as critical and terminate system
        default_value: Value to return on recoverable errors
    
    Example:
        @with_error_handling(component="LogCollector", critical=False, default_value=None)
        def collect_metrics(self):
            # Function implementation
            pass
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if critical:
                    handle_critical_error(
                        component,
                        f"Critical error in {func.__name__}: {str(e)}",
                        e
                    )
                else:
                    return handle_recoverable_error(
                        component,
                        f"Recoverable error in {func.__name__}: {str(e)}",
                        e,
                        default_value
                    )
        return wrapper
    return decorator


def safe_execute(component: str, operation: Callable, 
                default_value: Any = None, critical: bool = False) -> Any:
    """
    Execute an operation with error handling.
    
    Args:
        component: Name of the component
        operation: Callable to execute
        default_value: Value to return on error
        critical: If True, errors terminate the system
    
    Returns:
        Result of operation or default_value on error
    
    Example:
        result = safe_execute(
            "DataProcessor",
            lambda: parse_cpu_usage(output),
            default_value=0.0
        )
    """
    try:
        return operation()
    except Exception as e:
        if critical:
            handle_critical_error(component, f"Critical error: {str(e)}", e)
        else:
            return handle_recoverable_error(
                component,
                f"Error during operation: {str(e)}",
                e,
                default_value
            )
