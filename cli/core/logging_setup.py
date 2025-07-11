"""
Logging setup for ReconAI
"""

import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Optional

def setup_logging(
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    log_dir: str = "logs",
    verbose: bool = False
):
    """
    Setup logging for ReconAI
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_file: Log file name (optional)
        log_dir: Directory for log files
        verbose: Enable verbose console output
    """
    
    # Create logs directory
    log_dir_path = Path(log_dir)
    log_dir_path.mkdir(exist_ok=True)
    
    # Set logging level
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Create root logger
    logger = logging.getLogger()
    logger.setLevel(numeric_level)
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_level = logging.DEBUG if verbose else logging.INFO
    console_handler.setLevel(console_level)
    
    # Console formatter - clean format for user-facing messages
    console_formatter = logging.Formatter(
        '[%(levelname)s] %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # File handler (if log file specified)
    if log_file:
        log_file_path = log_dir_path / log_file
        
        # Use rotating file handler to prevent huge log files
        file_handler = logging.handlers.RotatingFileHandler(
            log_file_path,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        file_handler.setLevel(numeric_level)
        
        # File formatter - detailed format for debugging
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    
    # Module-specific loggers with clean names
    _setup_module_loggers(verbose)

def _setup_module_loggers(verbose: bool = False):
    """Setup loggers for specific modules"""
    
    module_loggers = [
        'orchestrator',
        'bbot_wrapper', 
        'ai_analyzer',
        'spiderfoot_wrapper',
        'google_dorks'
    ]
    
    for module_name in module_loggers:
        module_logger = logging.getLogger(module_name)
        
        # Don't add handlers to module loggers - they'll inherit from root
        # Just set appropriate levels
        if verbose:
            module_logger.setLevel(logging.DEBUG)
        else:
            module_logger.setLevel(logging.INFO)
        
        # Prevent duplicate messages
        module_logger.propagate = True

def get_logger(name: str) -> logging.Logger:
    """
    Get a logger for a specific module
    
    Args:
        name: Logger name
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)

class ProgressLogger:
    """Logger for showing progress of long-running operations"""
    
    def __init__(self, name: str, total_steps: int):
        self.logger = get_logger(name)
        self.total_steps = total_steps
        self.current_step = 0
        self.operation_name = ""
    
    def start_operation(self, operation_name: str):
        """Start a new operation"""
        self.operation_name = operation_name
        self.current_step = 0
        self.logger.info(f"Starting {operation_name}...")
    
    def step(self, message: str = ""):
        """Advance one step"""
        self.current_step += 1
        progress = (self.current_step / self.total_steps) * 100
        
        if message:
            self.logger.info(f"[{progress:.1f}%] {message}")
        else:
            self.logger.info(f"[{progress:.1f}%] Step {self.current_step}/{self.total_steps}")
    
    def complete(self, message: str = ""):
        """Mark operation as complete"""
        if message:
            self.logger.info(f"✓ {self.operation_name} completed: {message}")
        else:
            self.logger.info(f"✓ {self.operation_name} completed")
    
    def error(self, message: str):
        """Mark operation as failed"""
        self.logger.error(f"✗ {self.operation_name} failed: {message}")

class StatusLogger:
    """Logger for showing status updates with consistent formatting"""
    
    def __init__(self, name: str):
        self.logger = get_logger(name)
    
    def info(self, message: str):
        """Log info message with [+] prefix"""
        self.logger.info(f"[+] {message}")
    
    def warning(self, message: str):
        """Log warning message with [!] prefix"""
        self.logger.warning(f"[!] {message}")
    
    def error(self, message: str):
        """Log error message with [ERROR] prefix"""
        self.logger.error(f"[ERROR] {message}")
    
    def debug(self, message: str):
        """Log debug message with [DEBUG] prefix"""
        self.logger.debug(f"[DEBUG] {message}")
    
    def success(self, message: str):
        """Log success message with [✓] prefix"""
        self.logger.info(f"[✓] {message}")
    
    def failure(self, message: str):
        """Log failure message with [✗] prefix"""
        self.logger.error(f"[✗] {message}")
    
    def step(self, step_num: int, total_steps: int, message: str):
        """Log step progress"""
        self.logger.info(f"[{step_num}/{total_steps}] {message}")

def log_system_info():
    """Log system information for debugging"""
    import platform
    import sys
    
    logger = get_logger('system')
    
    logger.debug("=== System Information ===")
    logger.debug(f"Platform: {platform.platform()}")
    logger.debug(f"Python Version: {sys.version}")
    logger.debug(f"Python Executable: {sys.executable}")
    logger.debug(f"Working Directory: {Path.cwd()}")
    logger.debug("=== End System Information ===")

def log_environment_info():
    """Log environment information for debugging"""
    import os
    
    logger = get_logger('environment')
    
    logger.debug("=== Environment Information ===")
    
    # Log important environment variables (without exposing secrets)
    env_vars = [
        'PATH',
        'USER',
        'HOME',
        'PWD',
        'SHELL'
    ]
    
    for var in env_vars:
        value = os.getenv(var, 'Not set')
        logger.debug(f"{var}: {value}")
    
    # Check for API keys without exposing them
    api_key = os.getenv('OPENAI_API_KEY')
    logger.debug(f"OPENAI_API_KEY: {'Set' if api_key else 'Not set'}")
    
    logger.debug("=== End Environment Information ===")