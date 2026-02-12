"""
Unit tests for TerminalExecutor.

Tests cover:
- Whitelist validation
- Command execution with success/failure
- Timeout handling
- Error handling
"""

import pytest
import time
from unittest.mock import Mock, patch
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from terminal_executor import TerminalExecutor
from data_models import ExecutionResult


class TestTerminalExecutorInitialization:
    """Test TerminalExecutor initialization."""
    
    def test_init_with_valid_whitelist(self):
        """Test initialization with valid whitelist."""
        whitelist = ['wmic', 'tasklist', 'netstat']
        executor = TerminalExecutor(whitelist, timeout=30)
        
        assert executor.whitelist == whitelist
        assert executor.timeout == 30
    
    def test_init_with_empty_whitelist_raises_error(self):
        """Test that empty whitelist raises ValueError."""
        with pytest.raises(ValueError, match="Whitelist cannot be empty"):
            TerminalExecutor([], timeout=30)
    
    def test_init_with_zero_timeout_raises_error(self):
        """Test that zero timeout raises ValueError."""
        with pytest.raises(ValueError, match="Timeout must be positive"):
            TerminalExecutor(['wmic'], timeout=0)
    
    def test_init_with_negative_timeout_raises_error(self):
        """Test that negative timeout raises ValueError."""
        with pytest.raises(ValueError, match="Timeout must be positive"):
            TerminalExecutor(['wmic'], timeout=-5)


class TestWhitelistValidation:
    """Test whitelist validation logic."""
    
    def test_is_whitelisted_with_exact_match(self):
        """Test whitelisted command returns True."""
        executor = TerminalExecutor(['wmic', 'tasklist'])
        assert executor.is_whitelisted('wmic') is True
    
    def test_is_whitelisted_with_arguments(self):
        """Test whitelisted command with arguments returns True."""
        executor = TerminalExecutor(['wmic', 'tasklist'])
        assert executor.is_whitelisted('wmic cpu get loadpercentage') is True
    
    def test_is_whitelisted_with_non_whitelisted_command(self):
        """Test non-whitelisted command returns False."""
        executor = TerminalExecutor(['wmic', 'tasklist'])
        assert executor.is_whitelisted('rm -rf /') is False
    
    def test_is_whitelisted_with_empty_command(self):
        """Test empty command returns False."""
        executor = TerminalExecutor(['wmic'])
        assert executor.is_whitelisted('') is False
    
    def test_is_whitelisted_with_whitespace_only(self):
        """Test whitespace-only command returns False."""
        executor = TerminalExecutor(['wmic'])
        assert executor.is_whitelisted('   ') is False
    
    def test_is_whitelisted_case_sensitive(self):
        """Test that whitelist matching is case-sensitive."""
        executor = TerminalExecutor(['wmic'])
        assert executor.is_whitelisted('WMIC cpu get loadpercentage') is False


class TestCommandExecution:
    """Test command execution functionality."""
    
    @patch('subprocess.run')
    def test_execute_successful_command(self, mock_run):
        """Test successful command execution."""
        # Mock successful execution
        mock_run.return_value = Mock(
            returncode=0,
            stdout='LoadPercentage\n45\n',
            stderr=''
        )
        
        executor = TerminalExecutor(['echo'])
        result = executor.execute('echo test')
        
        assert result.success is True
        assert result.return_code == 0
        assert 'LoadPercentage' in result.stdout
        assert result.stderr == ''
        assert result.error_message is None
        assert result.execution_time >= 0
    
    @patch('subprocess.run')
    def test_execute_failed_command(self, mock_run):
        """Test failed command execution."""
        # Mock failed execution
        mock_run.return_value = Mock(
            returncode=1,
            stdout='',
            stderr='Command not found'
        )
        
        executor = TerminalExecutor(['test'])
        result = executor.execute('test')
        
        assert result.success is False
        assert result.return_code == 1
        assert result.stderr == 'Command not found'
        assert result.error_message is not None
        assert 'failed with return code 1' in result.error_message
    
    def test_execute_non_whitelisted_command(self):
        """Test execution of non-whitelisted command is rejected."""
        executor = TerminalExecutor(['wmic'])
        result = executor.execute('rm -rf /')
        
        assert result.success is False
        assert result.return_code == -1
        assert 'not whitelisted' in result.error_message
        assert result.execution_time == 0.0
    
    @patch('subprocess.run')
    def test_execute_command_timeout(self, mock_run):
        """Test command timeout handling."""
        import subprocess
        
        # Mock timeout exception
        mock_run.side_effect = subprocess.TimeoutExpired('test', 30)
        
        executor = TerminalExecutor(['sleep'], timeout=1)
        result = executor.execute('sleep 10')
        
        assert result.success is False
        assert result.return_code == -1
        assert 'timeout' in result.error_message.lower()
        assert result.execution_time >= 0
    
    @patch('subprocess.run')
    def test_execute_unexpected_error(self, mock_run):
        """Test handling of unexpected errors during execution."""
        # Mock unexpected exception
        mock_run.side_effect = RuntimeError("Unexpected error")
        
        executor = TerminalExecutor(['test'])
        result = executor.execute('test')
        
        assert result.success is False
        assert result.return_code == -1
        assert 'Unexpected error' in result.error_message
        assert result.execution_time >= 0


class TestExecutionResult:
    """Test ExecutionResult structure."""
    
    @patch('subprocess.run')
    def test_execution_result_contains_all_fields(self, mock_run):
        """Test that ExecutionResult contains all required fields."""
        mock_run.return_value = Mock(
            returncode=0,
            stdout='output',
            stderr=''
        )
        
        executor = TerminalExecutor(['echo'])
        result = executor.execute('echo test')
        
        assert hasattr(result, 'success')
        assert hasattr(result, 'stdout')
        assert hasattr(result, 'stderr')
        assert hasattr(result, 'return_code')
        assert hasattr(result, 'execution_time')
        assert hasattr(result, 'error_message')


class TestEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def test_execute_empty_command(self):
        """Test execution of empty command."""
        executor = TerminalExecutor(['test'])
        result = executor.execute('')
        
        assert result.success is False
        assert 'not whitelisted' in result.error_message
    
    @patch('subprocess.run')
    def test_execute_command_with_special_characters(self, mock_run):
        """Test command with special characters."""
        mock_run.return_value = Mock(
            returncode=0,
            stdout='output',
            stderr=''
        )
        
        executor = TerminalExecutor(['echo'])
        result = executor.execute('echo "test with spaces"')
        
        assert result.success is True
    
    def test_whitelist_with_multiple_commands(self):
        """Test whitelist with multiple commands."""
        whitelist = ['wmic', 'tasklist', 'netstat', 'ps', 'top']
        executor = TerminalExecutor(whitelist)
        
        assert executor.is_whitelisted('wmic cpu') is True
        assert executor.is_whitelisted('tasklist') is True
        assert executor.is_whitelisted('netstat -an') is True
        assert executor.is_whitelisted('ps aux') is True
        assert executor.is_whitelisted('top -bn1') is True
        assert executor.is_whitelisted('rm -rf') is False


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
