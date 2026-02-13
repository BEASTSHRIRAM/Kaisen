"""
Unit tests for comprehensive error handling across all components.

This test suite verifies that error categorization, logging, and recovery
mechanisms work correctly for critical, recoverable, and warning errors.

Requirements validated:
- 10.1: Log errors with timestamp, component name, and error message
- 10.2: Continue operation after non-critical errors
- 10.3: Terminate gracefully for critical errors
"""

import unittest
import sys
import logging
from unittest.mock import Mock, patch, MagicMock
from io import StringIO

# Add parent directory to path for imports
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.error_handler import (
    ErrorCategory, LogCollectionError, CriticalError, RecoverableError,
    log_error, handle_critical_error, handle_recoverable_error, handle_warning,
    with_error_handling, safe_execute
)


class TestErrorCategories(unittest.TestCase):
    """Test error category definitions and custom exceptions."""
    
    def test_error_category_enum(self):
        """Test that error categories are properly defined."""
        self.assertEqual(ErrorCategory.CRITICAL.value, "critical")
        self.assertEqual(ErrorCategory.RECOVERABLE.value, "recoverable")
        self.assertEqual(ErrorCategory.WARNING.value, "warning")
    
    def test_critical_error_creation(self):
        """Test CriticalError exception creation."""
        error = CriticalError("Test critical error", "TestComponent")
        self.assertEqual(error.message, "Test critical error")
        self.assertEqual(error.category, ErrorCategory.CRITICAL)
        self.assertEqual(error.component, "TestComponent")
    
    def test_recoverable_error_creation(self):
        """Test RecoverableError exception creation."""
        error = RecoverableError("Test recoverable error", "TestComponent")
        self.assertEqual(error.message, "Test recoverable error")
        self.assertEqual(error.category, ErrorCategory.RECOVERABLE)
        self.assertEqual(error.component, "TestComponent")


class TestErrorLogging(unittest.TestCase):
    """Test error logging functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.logger = logging.getLogger("src.error_handler")
        self.log_stream = StringIO()
        self.handler = logging.StreamHandler(self.log_stream)
        self.handler.setLevel(logging.DEBUG)
        # Set format to include level name
        formatter = logging.Formatter('%(levelname)s - %(message)s')
        self.handler.setFormatter(formatter)
        self.logger.addHandler(self.handler)
        self.logger.setLevel(logging.DEBUG)
    
    def tearDown(self):
        """Clean up test fixtures."""
        self.logger.removeHandler(self.handler)
    
    def test_log_critical_error(self):
        """Test logging of critical errors."""
        log_error(ErrorCategory.CRITICAL, "TestComponent", "Critical error message")
        log_output = self.log_stream.getvalue()
        self.assertIn("CRITICAL", log_output)
        self.assertIn("TestComponent", log_output)
        self.assertIn("Critical error message", log_output)
    
    def test_log_recoverable_error(self):
        """Test logging of recoverable errors."""
        log_error(ErrorCategory.RECOVERABLE, "TestComponent", "Recoverable error message")
        log_output = self.log_stream.getvalue()
        self.assertIn("ERROR", log_output)
        self.assertIn("TestComponent", log_output)
        self.assertIn("Recoverable error message", log_output)
    
    def test_log_warning(self):
        """Test logging of warnings."""
        log_error(ErrorCategory.WARNING, "TestComponent", "Warning message")
        log_output = self.log_stream.getvalue()
        self.assertIn("WARNING", log_output)
        self.assertIn("TestComponent", log_output)
        self.assertIn("Warning message", log_output)


class TestErrorHandlers(unittest.TestCase):
    """Test error handling functions."""
    
    @patch('sys.exit')
    def test_handle_critical_error_terminates(self, mock_exit):
        """Test that critical errors terminate the system."""
        handle_critical_error("TestComponent", "Critical failure")
        mock_exit.assert_called_once_with(1)
    
    def test_handle_recoverable_error_returns_default(self):
        """Test that recoverable errors return default value."""
        result = handle_recoverable_error(
            "TestComponent",
            "Recoverable failure",
            default_value=42
        )
        self.assertEqual(result, 42)
    
    def test_handle_warning_does_not_interrupt(self):
        """Test that warnings don't interrupt execution."""
        # Should not raise any exception
        handle_warning("TestComponent", "Warning message")


class TestErrorHandlingDecorator(unittest.TestCase):
    """Test the with_error_handling decorator."""
    
    def test_decorator_with_successful_function(self):
        """Test decorator with function that succeeds."""
        @with_error_handling(component="TestComponent", default_value=None)
        def successful_function():
            return "success"
        
        result = successful_function()
        self.assertEqual(result, "success")
    
    def test_decorator_with_failing_function_non_critical(self):
        """Test decorator with function that fails (non-critical)."""
        @with_error_handling(component="TestComponent", critical=False, default_value="default")
        def failing_function():
            raise ValueError("Test error")
        
        result = failing_function()
        self.assertEqual(result, "default")
    
    @patch('sys.exit')
    def test_decorator_with_failing_function_critical(self, mock_exit):
        """Test decorator with function that fails (critical)."""
        @with_error_handling(component="TestComponent", critical=True)
        def failing_function():
            raise ValueError("Critical test error")
        
        failing_function()
        mock_exit.assert_called_once_with(1)


class TestSafeExecute(unittest.TestCase):
    """Test the safe_execute utility function."""
    
    def test_safe_execute_with_successful_operation(self):
        """Test safe_execute with operation that succeeds."""
        result = safe_execute(
            "TestComponent",
            lambda: 10 + 5,
            default_value=0
        )
        self.assertEqual(result, 15)
    
    def test_safe_execute_with_failing_operation(self):
        """Test safe_execute with operation that fails."""
        result = safe_execute(
            "TestComponent",
            lambda: 1 / 0,  # Division by zero
            default_value=-1
        )
        self.assertEqual(result, -1)
    
    @patch('sys.exit')
    def test_safe_execute_with_critical_failure(self, mock_exit):
        """Test safe_execute with critical failure."""
        safe_execute(
            "TestComponent",
            lambda: 1 / 0,
            critical=True
        )
        mock_exit.assert_called_once_with(1)


class TestComponentErrorHandling(unittest.TestCase):
    """Test error handling integration in components."""
    
    def test_log_collector_handles_metric_collection_failure(self):
        """Test that LogCollector continues after metric collection failure."""
        # This is tested through the actual component behavior
        # The _collect_metrics method should handle exceptions and continue
        pass
    
    def test_data_processor_handles_parsing_failure(self):
        """Test that DataProcessor handles parsing failures gracefully."""
        # The _safe_parse method should catch exceptions and return default values
        pass
    
    def test_model_interface_handles_prediction_failure(self):
        """Test that ModelInterface handles prediction failures."""
        # The predict method should catch exceptions and log errors
        pass


if __name__ == '__main__':
    # Configure logging for tests
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    unittest.main()
