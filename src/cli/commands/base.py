"""Base command class for CLI commands."""
from abc import ABC, abstractmethod
import logging
from pathlib import Path
import os
from datetime import datetime

from ..utils import confirm_production

class Command(ABC):
    """Base class for all CLI commands."""
    
    def __init__(self, env: str, dry_run: bool = False, debug: bool = False, setup_logs: bool = False) -> None:
        """Initialize command.
        
        Args:
            env: Environment to run in
            dry_run: Whether to run in dry run mode
            debug: Whether to run in debug mode
            setup_logs: Whether to set up logging immediately
        """
        self.env = env
        self.dry_run = dry_run
        self.debug = debug
        self.guid = None  # Operation-specific identifier
        self.logger = logging.getLogger(self.__class__.__name__)
        
        if debug:
            logging.getLogger().setLevel(logging.DEBUG)
            
        if setup_logs:
            self.setup_logging()
    
    def setup_logging(self) -> None:
        """Set up logging for this command."""
        # Remove any existing handlers
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
        
        # Get data directory from environment or default to "data"
        data_dir = os.getenv("DATA_DIR", "data")
        
        # Create structured log directory
        log_dir = Path(data_dir) / "logs" / self.env / self.__class__.__name__.lower()
        log_dir.parent.mkdir(parents=True, exist_ok=True)
        
        # Check permissions before creating directory
        if not os.access(log_dir.parent, os.W_OK):
            raise PermissionError(f"Cannot write to log directory: {log_dir.parent}")
        
        # Create log directory
        log_dir.mkdir(parents=True, exist_ok=True)
        
        # Create log file with timestamp and operation details
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")  # Added microseconds
        print(f"\nSetting up logging for {self.__class__.__name__}")
        print(f"Timestamp: {timestamp}")
        print(f"GUID: {self.guid}")
        operation_id = self.guid if self.guid else "batch"
        log_file = log_dir / f"{timestamp}_{operation_id}.log"
        print(f"Creating log file: {log_file}")
        
        # Add file handler to logger
        handler = logging.FileHandler(log_file)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        
        # Set logger level based on debug flag
        self.logger.setLevel(logging.DEBUG if self.debug else logging.INFO)
        
        # Log initial messages
        self.logger.info(f"Started {self.__class__.__name__} operation [GUID: {self.guid}]")
        if self.dry_run:
            self.logger.info("DRY RUN MODE - No changes will be made")
    
    @abstractmethod
    def validate(self) -> bool:
        """Validate command can be executed.
        
        Returns:
            True if validation passes
            
        Raises:
            ValueError: If validation fails
        """
        # Check production safety
        if self.env == "prod" and not self.dry_run:
            if not confirm_production():
                raise ValueError("Operation cancelled")
        return True
    
    @abstractmethod
    def execute(self) -> bool:
        """Execute the command.
        
        Returns:
            True if successful
        """
        pass
    
    @abstractmethod
    def verify(self) -> bool:
        """Verify command execution was successful.
        
        Returns:
            True if verification passes
        """
        pass
    
    def run(self) -> bool:
        """Run the full command lifecycle.
        
        Returns:
            True if successful
        """
        try:
            # Re-setup logging to ensure GUID is captured
            self.setup_logging()
            
            if not self.validate():
                return False
                
            if not self.execute():
                return False
                
            if not self.verify():
                return False
                
            return True
            
        except Exception as e:
            self.logger.error("Command failed: %s", str(e))
            if self.debug:
                self.logger.exception("Detailed error:")
            return False 