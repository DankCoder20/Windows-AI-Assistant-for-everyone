import logging
import os
from datetime import datetime
from typing import Optional
from .config import get_config

class AssistantLogger:
    def __init__(self, log_file: Optional[str] = None):
        self.config = get_config()
        self.log_file = log_file or self.config.get_log_file_path()

        self._setup_logger()

    def _setup_logger(self):
        log_dir = os.path.dirname(self.log_file)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)

        self.logger = logging.getLogger("WindowsAIAssistant")
        self.logger.setLevel(logging.INFO)

        if not self.logger.handlers:
            file_handler = logging.FileHandler(self.log_file, encoding='utf-8')
            console_handler = logging.StreamHandler()

            formatter = logging.Formatter(
                '%(asctime)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )

            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)

            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)

    def log_command(self, user_command: str, parsed_action: dict):
        self.logger.info(f"USER_COMMAND: {user_command}")
        self.logger.info(f"PARSED_ACTION: {parsed_action}")

    def log_action_start(self, action: str, details: dict):
        self.logger.info(f"ACTION_START: {action} | Details: {details}")

    def log_action_success(self, action: str, details: dict):
        self.logger.info(f"ACTION_SUCCESS: {action} | Details: {details}")

    def log_action_error(self, action: str, error: str, details: dict):
        self.logger.error(f"ACTION_ERROR: {action} | Error: {error} | Details: {details}")

    def log_validation_error(self, error: str, details: dict):
        self.logger.warning(f"VALIDATION_ERROR: {error} | Details: {details}")

    def log_api_error(self, error: str):
        self.logger.error(f"API_ERROR: {error}")

    def log_system_error(self, error: str):
        self.logger.critical(f"SYSTEM_ERROR: {error}")

    def log_info(self, message: str):
        self.logger.info(message)

    def log_warning(self, message: str):
        self.logger.warning(message)

    def log_error(self, message: str):
        self.logger.error(message)

_logger_instance: Optional[AssistantLogger] = None

def get_logger() -> AssistantLogger:
    global _logger_instance
    if _logger_instance is None:
        _logger_instance = AssistantLogger()
    return _logger_instance