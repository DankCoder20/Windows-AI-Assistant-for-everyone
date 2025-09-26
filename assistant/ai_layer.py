import json
from typing import Any, Dict
import requests
from .config import get_config
from .logger import get_logger


class AILayer:
    """Groq API integration to convert NL commands into structured JSON actions."""

    def __init__(self) -> None:
        self.config = get_config()
        self.logger = get_logger()
        self._model = "llama-3.3-70b-versatile"
        self._endpoint = "https://api.groq.com/openai/v1/chat/completions"

    def parse_command(self, user_command: str) -> Dict[str, Any]:
        """Send the user command to Groq API and return a structured action JSON.

        The expected schema:
            {
              "action": "create_folder|move_files|open_app|delete_folder",
              "path": "C:\\...",            # for create/delete
              "source": "C:\\...",          # for move
              "destination": "C:\\...",     # for move
              "app": "notepad.exe"           # for open_app
            }
        """
        system_prompt = (
            "You are a precise command parser for a Windows AI assistant. "
            "Convert the user's natural language instruction into a STRICT JSON object with keys: "
            "action, path, source, destination, app. Only include relevant keys. "
            "Allowed actions: create_folder, move_files, open_app, delete_folder. "
            "Return ONLY JSON, no explanations."
        )

        body = {
            "model": self._model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_command},
            ],
            "temperature": 0.0,
        }

        headers = {
            "Authorization": f"Bearer {self.config.get_groq_api_key()}",
            "Content-Type": "application/json",
        }

        try:
            resp = requests.post(self._endpoint, headers=headers, data=json.dumps(body), timeout=30)
            resp.raise_for_status()
            data = resp.json()

            content = data["choices"][0]["message"]["content"].strip()
            # Some models may wrap JSON in code fences; attempt to extract JSON
            if content.startswith("```") and content.endswith("```"):
                inner = content[3:-3].strip()
                if inner.lower().startswith("json\n"):
                    inner = inner.split("\n", 1)[1]
                content = inner

            action = json.loads(content)
            if not isinstance(action, dict):
                raise ValueError("Parsed response is not a JSON object")

            self.logger.log_command(user_command, action)
            return action
        except Exception as e:
            self.logger.log_api_error(str(e))
            raise


_ai_instance: AILayer | None = None


def get_ai_layer() -> AILayer:
    global _ai_instance
    if _ai_instance is None:
        _ai_instance = AILayer()
    return _ai_instance


