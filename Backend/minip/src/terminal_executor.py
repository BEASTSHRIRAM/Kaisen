"""
Terminal command executor with whitelist validation and timeout support.

This module provides safe execution of system commands with the following features:
- Whitelist-based command validation
- Timeout enforcement (default 30 seconds)
- Comprehensive error handling
- Detailed execution results

Requirements validated:
- 2.1: Only execute commands from predefined whitelist
- 2.2: Reject non-whitelisted commands with warning
- 2.4: Return error status with failure reason
- 2.5: Set timeout of 30 seconds for command execution
- 2.6: Terminate commands that exceed timeout
"""

import subprocess
import logging
import time
from typing import List
from src.data_models import ExecutionResult


logger = logging.getLogger(__name__)


class TerminalExecutor:
    """
    Executes system commands safely with whitelist validation and timeout.
    
    This class ensures that only pre-approved commands can be executed,
    preventing arbitrary command execution and maintaining system security.
    
    Attributes:
        whitelist: List of allowed base commands
        timeout: Maximum execution time in seconds (default: 30)
    """
    
    def __init__(self, whitelist: List[str], timeout: int = 30):
        """
        Initialize the TerminalExecutor with a command whitelist.
        
        Args:
            whitelist: List of allowed base commands (e.g., ['wmic', 'tasklist'])
            timeout: Maximum execution time in seconds (default: 30)
        
        Raises:
            ValueError: If whitelist is empty or timeout is non-positive
        """
        if not whitelist:
            raise ValueError("Whitelist cannot be empty")
        if timeout <= 0:
            raise ValueError("Timeout must be positive")
        
        self.whitelist = whitelist
        self.timeout = timeout
        logger.info(f"TerminalExecutor initialized with {len(whitelist)} whitelisted commands, timeout={timeout}s")
    
    def is_whitelisted(self, command: str) -> bool:
        """
        Check if a command is in the whitelist.
        
        Extracts the base command (first token) and checks against the whitelist.
        
        Args:
            command: The full command string to validate
        
        Returns:
            True if the base command is whitelisted, False otherwise
        
        Example:
            >>> executor = TerminalExecutor(['wmic', 'tasklist'])
            >>> executor.is_whitelisted('wmic cpu get loadpercentage')
            True
            >>> executor.is_whitelisted('rm -rf /')
            False
        """
        if not command or not command.strip():
            return False
        
        # Extract base command (first token)
        base_command = command.strip().split()[0]
        
        # Check against whitelist
        is_allowed = base_command in self.whitelist
        
        if not is_allowed:
            logger.warning(f"Command not whitelisted: {base_command}")
        
        return is_allowed
    
    def execute(self, command: str) -> ExecutionResult:
        """
        Execute a command if it is whitelisted.
        
        This method performs the following steps:
        1. Validate command against whitelist
        2. Execute command with timeout
        3. Capture stdout, stderr, and return code
        4. Handle timeouts and execution failures
        
        Args:
            command: The command string to execute
        
        Returns:
            ExecutionResult containing execution details and output
        
        Requirements:
            - 2.1: Only executes whitelisted commands
            - 2.2: Rejects non-whitelisted commands
            - 2.4: Returns error status with failure reason
            - 2.5: Enforces 30-second timeout
            - 2.6: Terminates commands exceeding timeout
        """
        # Validate whitelist
        if not self.is_whitelisted(command):
            # Extract base command safely
            cmd_parts = command.split() if command else []
            base_cmd = cmd_parts[0] if cmd_parts else 'empty'
            error_msg = f"Command not whitelisted: {base_cmd}"
            logger.warning(error_msg)
            return ExecutionResult(
                success=False,
                stdout="",
                stderr="",
                return_code=-1,
                execution_time=0.0,
                error_message=error_msg
            )
        
        # Execute command with timeout
        start_time = time.time()
        
        try:
            logger.debug(f"Executing command: {command}")
            
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=self.timeout
            )
            
            execution_time = time.time() - start_time
            
            success = result.returncode == 0
            
            if not success:
                logger.warning(
                    f"Command failed with return code {result.returncode}: {command}"
                )
            
            return ExecutionResult(
                success=success,
                stdout=result.stdout,
                stderr=result.stderr,
                return_code=result.returncode,
                execution_time=execution_time,
                error_message=None if success else f"Command failed with return code {result.returncode}"
            )
        
        except subprocess.TimeoutExpired:
            execution_time = time.time() - start_time
            error_msg = f"Command timeout after {self.timeout} seconds"
            logger.error(f"{error_msg}: {command}")
            
            return ExecutionResult(
                success=False,
                stdout="",
                stderr="",
                return_code=-1,
                execution_time=execution_time,
                error_message=error_msg
            )
        
        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = f"Unexpected error during command execution: {str(e)}"
            logger.error(f"{error_msg}: {command}")
            
            return ExecutionResult(
                success=False,
                stdout="",
                stderr="",
                return_code=-1,
                execution_time=execution_time,
                error_message=error_msg
            )
