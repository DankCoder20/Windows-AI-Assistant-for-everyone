import os
from dotenv import load_dotenv
from typing import List, Optional

class Config:
    def __init__(self, env_file: str = ".env"):
        load_dotenv(env_file)

        self.groq_api_key = self._get_required_env("GROQ_API_KEY")
        self.allowed_directories = self._parse_directories(
            os.getenv("ALLOWED_DIRECTORIES", f"C:\\Users\\{os.getenv('USERNAME', 'User')}\\Desktop")
        )
        self.log_file_path = os.getenv("LOG_FILE_PATH", "assistant.log")
        self.default_text_editor = os.getenv("DEFAULT_TEXT_EDITOR", "notepad.exe")
        self.default_browser = os.getenv("DEFAULT_BROWSER", "start")

    def _get_required_env(self, key: str) -> str:
        value = os.getenv(key)
        if not value:
            raise ValueError(f"Required environment variable '{key}' is not set")
        return value

    def _parse_directories(self, directories_str: str) -> List[str]:
        return [d.strip() for d in directories_str.split(",") if d.strip()]

    def is_path_allowed(self, path: str) -> bool:
        abs_path = os.path.abspath(path)
        return any(abs_path.startswith(allowed_dir) for allowed_dir in self.allowed_directories)

    def get_log_file_path(self) -> str:
        return self.log_file_path

    def get_groq_api_key(self) -> str:
        return self.groq_api_key

_config_instance: Optional[Config] = None

def get_config() -> Config:
    global _config_instance
    if _config_instance is None:
        _config_instance = Config()
    return _config_instance