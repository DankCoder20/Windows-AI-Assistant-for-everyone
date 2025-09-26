import os
import shutil
import subprocess
from typing import Dict, Any

from .logger import get_logger


class Executor:
    def __init__(self) -> None:
        self.logger = get_logger()

    def execute(self, action: Dict[str, Any]) -> str:
        act = action.get("action")
        details = {k: v for k, v in action.items() if k != "action"}
        self.logger.log_action_start(act, details)

        try:
            if act == "create_folder":
                # If destination is present (defensive), join it to path
                path = action.get("path")
                destination = action.get("destination")
                if destination and isinstance(destination, str) and destination.strip():
                    path = os.path.join(path, destination.strip())
                return self._create_folder(path)
            if act == "move_files":
                return self._move_files(action["source"], action["destination"])
            if act == "open_app":
                return self._open_app(action.get("app") or action.get("path"))
            if act == "delete_folder":
                if not action.get("confirmed"):
                    raise PermissionError("Destructive action not confirmed")
                return self._delete_folder(action["path"]) 

            raise ValueError(f"Unsupported action: {act}")
        except Exception as exc:
            self.logger.log_action_error(act or "unknown", str(exc), details)
            raise

    def _create_folder(self, path: str) -> str:
        os.makedirs(path, exist_ok=True)
        self.logger.log_action_success("create_folder", {"path": path})
        return f"Folder created or already exists: {path}"

    def _move_files(self, source: str, destination: str) -> str:
        if os.path.isdir(source):
            # Move a directory into destination (destination can be folder or new path)
            result_path = shutil.move(source, destination)
            self.logger.log_action_success("move_files", {"source": source, "destination": destination})
            return f"Moved directory to: {result_path}"
        else:
            # Move a single file
            os.makedirs(os.path.dirname(os.path.abspath(destination)), exist_ok=True)
            result_path = shutil.move(source, destination)
            self.logger.log_action_success("move_files", {"source": source, "destination": destination})
            return f"Moved file to: {result_path}"

    def _open_app(self, app: str) -> str:
        # Use start via shell to allow opening with file association on Windows
        subprocess.Popen(app if isinstance(app, list) else app, shell=True)
        self.logger.log_action_success("open_app", {"app": app})
        return f"Opened: {app}"

    def _delete_folder(self, path: str) -> str:
        shutil.rmtree(path)
        self.logger.log_action_success("delete_folder", {"path": path})
        return f"Deleted folder: {path}"


_executor_instance: Executor | None = None


def get_executor() -> Executor:
    global _executor_instance
    if _executor_instance is None:
        _executor_instance = Executor()
    return _executor_instance


