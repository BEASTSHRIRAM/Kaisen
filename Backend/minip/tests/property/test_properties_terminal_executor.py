"""
Property-based tests for TerminalExecutor.

These tests verify universal properties that should hold across all inputs.
Uses Hypothesis for property-based testing.

Properties tested:
- Property 3: Whitelist Enforcement
- Property 4: Command Execution Error Handling
"""

import pytest
from hypothesis import given, settings, strategies as st
from unittest.mock import Mock, patch
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from terminal_executor import TerminalExecutor
from data_models import ExecutionResult


# Strategy for generating command strings
command_strategy = st.text(
    alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'P', 'Zs')),
    min_size=1,
    max_size=100
)

# Strategy for generating whitelist
whitelist_strategy = st.lists(
    st.text(
        alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd')),
        min_size=1,
        max_size=20
    ),
    min_size=1,
    max_size=10,
    unique=True
)


class TestProperty3WhitelistEnforcement:
    """
    **Validates: Requirements 2.1, 2.2**
    
    Property 3: Whitelist Enforcement
    For any command submitted to Terminal_Executor, it should only execute
    if the base command is in the whitelist, otherwise it should be rejected.
    """
    
    @settings(max_examples=100)
    @given(
        whitelist=whitelist_strategy,
        command=command_strategy
    )
    def test_whitelist_enforcement_property(self, whitelist, command):
        """
        Property test: Commands not in whitelist are always rejected.
        
        For any whitelist and any command, if the base command is not in the
        whitelist, execution should be rejected with success=False.
        """
        executor = TerminalExecutor(whitelist)
        
        # Extract base command
        base_command = command.strip().split()[0] if command.strip() else ""
        
        # Check if command should be whitelisted
        should_be_whitelisted = base_command in whitelist
        
        # Verify is_whitelisted returns correct result
        is_whitelisted = executor.is_whitelisted(command)
        assert is_whitelisted == should_be_whitelisted
        
        # If not whitelisted, execute should reject
        if not should_be_whitelisted:
            result = executor.execute(command)
            assert result.success is False
            assert result.return_code == -1
            assert result.error_message is not None
            assert 'not whitelisted' in result.error_message.lower()
    
    @settings(max_examples=50)
    @given(
        whitelist=whitelist_strategy,
        whitelisted_cmd=st.text(
            alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd')),
            min_size=1,
            max_size=20
        ),
        args=st.text(min_size=0, max_size=50)
    )
    def test_whitelisted_command_with_args_accepted(self, whitelist, whitelisted_cmd, args):
        """
        Property test: Whitelisted commands with any arguments are accepted.
        
        For any whitelisted command with any arguments, is_whitelisted should
        return True.
        """
        # Add the command to whitelist
        full_whitelist = whitelist + [whitelisted_cmd]
        executor = TerminalExecutor(full_whitelist)
        
        # Build command with arguments
        full_command = f"{whitelisted_cmd} {args}".strip()
        
        # Should be whitelisted
        assert executor.is_whitelisted(full_command) is True


class TestProperty4CommandExecutionErrorHandling:
    """
    **Validates: Requirements 2.4**
    
    Property 4: Command Execution Error Handling
    For any command that fails during execution, the Terminal_Executor should
    return an ExecutionResult with success=False and a descriptive error message.
    """
    
    @settings(max_examples=50)
    @given(
        return_code=st.integers(min_value=1, max_value=255),
        stderr_msg=st.text(min_size=0, max_size=100)
    )
    @patch('subprocess.run')
    def test_failed_command_returns_error_result(self, mock_run, return_code, stderr_msg):
        """
        Property test: Failed commands always return ExecutionResult with success=False.
        
        For any non-zero return code, the ExecutionResult should have:
        - success=False
        - error_message is not None
        - return_code matches the actual return code
        """
        # Mock failed execution
        mock_run.return_value = Mock(
            returncode=return_code,
            stdout='',
            stderr=stderr_msg
        )
        
        executor = TerminalExecutor(['test'])
        result = executor.execute('test')
        
        # Verify error handling
        assert result.success is False
        assert result.return_code == return_code
        assert result.error_message is not None
        assert len(result.error_message) > 0
        assert result.stderr == stderr_msg
    
    @settings(max_examples=30)
    @given(
        timeout_value=st.integers(min_value=1, max_value=10)
    )
    @patch('subprocess.run')
    def test_timeout_always_returns_error_result(self, mock_run, timeout_value):
        """
        Property test: Timeout always results in ExecutionResult with success=False.
        
        For any timeout value, when a command times out, the result should have:
        - success=False
        - error_message containing 'timeout'
        - return_code=-1
        """
        import subprocess
        
        # Mock timeout
        mock_run.side_effect = subprocess.TimeoutExpired('test', timeout_value)
        
        executor = TerminalExecutor(['test'], timeout=timeout_value)
        result = executor.execute('test')
        
        # Verify timeout handling
        assert result.success is False
        assert result.return_code == -1
        assert result.error_message is not None
        assert 'timeout' in result.error_message.lower()
        assert result.execution_time >= 0


class TestProperty5CommandTimeoutEnforcement:
    """
    **Validates: Requirements 2.5, 2.6**
    
    Property: Command timeout is enforced for all commands.
    For any timeout value, commands should be terminated if they exceed the timeout.
    """
    
    @settings(max_examples=30)
    @given(
        timeout_value=st.integers(min_value=1, max_value=60)
    )
    def test_timeout_configuration_property(self, timeout_value):
        """
        Property test: Timeout value is correctly configured.
        
        For any positive timeout value, the executor should store and use it.
        """
        executor = TerminalExecutor(['test'], timeout=timeout_value)
        assert executor.timeout == timeout_value


class TestPropertyExecutionResultStructure:
    """
    Property tests for ExecutionResult structure consistency.
    """
    
    @settings(max_examples=50)
    @given(
        success=st.booleans(),
        stdout=st.text(max_size=200),
        stderr=st.text(max_size=200),
        return_code=st.integers(min_value=-1, max_value=255),
        execution_time=st.floats(min_value=0.0, max_value=100.0, allow_nan=False, allow_infinity=False)
    )
    def test_execution_result_structure_property(self, success, stdout, stderr, return_code, execution_time):
        """
        Property test: ExecutionResult maintains consistent structure.
        
        For any valid field values, ExecutionResult should be constructible
        and all fields should be accessible.
        """
        result = ExecutionResult(
            success=success,
            stdout=stdout,
            stderr=stderr,
            return_code=return_code,
            execution_time=execution_time,
            error_message="test error" if not success else None
        )
        
        # Verify all fields are accessible
        assert result.success == success
        assert result.stdout == stdout
        assert result.stderr == stderr
        assert result.return_code == return_code
        assert result.execution_time == execution_time
        
        # Verify error_message consistency
        if not success:
            assert result.error_message is not None


class TestPropertyWhitelistValidation:
    """
    Additional property tests for whitelist validation edge cases.
    """
    
    @settings(max_examples=50)
    @given(
        whitelist=whitelist_strategy
    )
    def test_empty_command_always_rejected(self, whitelist):
        """
        Property test: Empty commands are always rejected.
        
        For any whitelist, empty or whitespace-only commands should be rejected.
        """
        executor = TerminalExecutor(whitelist)
        
        # Test various empty/whitespace commands
        empty_commands = ['', '   ', '\t', '\n', '  \t\n  ']
        
        for cmd in empty_commands:
            assert executor.is_whitelisted(cmd) is False
            result = executor.execute(cmd)
            assert result.success is False
    
    @settings(max_examples=50)
    @given(
        base_cmd=st.text(
            alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd')),
            min_size=1,
            max_size=20
        ),
        num_args=st.integers(min_value=0, max_value=10)
    )
    def test_whitelist_checks_base_command_only(self, base_cmd, num_args):
        """
        Property test: Whitelist validation only checks base command.
        
        For any base command and any number of arguments, only the base
        command should be checked against the whitelist.
        """
        executor = TerminalExecutor([base_cmd])
        
        # Build command with multiple arguments
        args = ' '.join(['arg'] * num_args)
        full_command = f"{base_cmd} {args}".strip()
        
        # Should be whitelisted regardless of arguments
        assert executor.is_whitelisted(full_command) is True


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
