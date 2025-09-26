import os
from typing import Dict, Any, Tuple, Optional
from .config import get_config
from .logger import get_logger


class Validator:
    def __init__(self) -> None:
        self.config = get_config()
        self.logger = get_logger()

    def validate_action(self, action: Dict[str, Any]) -> Tuple[bool, str]:
        if not isinstance(action, dict):
            return False, "Action must be a JSON object"

        allowed_actions = {"create_folder", "move_files", "open_app", "delete_folder"}
        act = action.get("action")
        if act not in allowed_actions:
            return False, f"Unsupported action: {act}"

        if act in {"create_folder", "delete_folder"}:
            path = action.get("path")
            if not path or not isinstance(path, str):
                return False, "Missing or invalid 'path'"

            # For create_folder, allow path aliases like "desktop" and optional destination name
            if act == "create_folder":
                normalized = self._normalize_create_folder_path(path, action.get("destination"))
                action["path"] = normalized
                if "destination" in action:
                    del action["destination"]
                path = normalized

            # For delete_folder, allow path aliases and optional subfolder provided via 'source' or 'destination'
            if act == "delete_folder":
                subfolder = action.get("source") or action.get("destination")
                normalized_del = self._normalize_delete_folder_path(path, subfolder)
                action["path"] = normalized_del
                # Remove helper keys to avoid confusion downstream
                if "source" in action:
                    del action["source"]
                if "destination" in action:
                    del action["destination"]
                path = normalized_del

            if not self._is_allowed_path(path):
                return False, f"Path not allowed: {path}"

            if act == "create_folder":
                parent = os.path.dirname(os.path.abspath(path))
                if not os.path.exists(parent):
                    return False, f"Parent directory does not exist: {parent}"
            else:  # delete_folder
                if not os.path.isdir(path):
                    return False, f"Folder does not exist: {path}"

        if act == "move_files":
            src = action.get("source")
            dst = action.get("destination")
            if not src or not dst:
                return False, "Missing 'source' or 'destination'"
            if not self._is_allowed_path(src) or not self._is_allowed_path(dst):
                return False, "Source or destination path not allowed"
            if not os.path.exists(src):
                return False, f"Source not found: {src}"
            dst_parent = dst if os.path.isdir(dst) else os.path.dirname(os.path.abspath(dst))
            if not os.path.exists(dst_parent):
                return False, f"Destination directory not found: {dst_parent}"

        if act == "open_app":
            app = action.get("app") or action.get("path")
            if not app:
                return False, "Missing 'app' to open"

        return True, "OK"

    def requires_confirmation(self, action: Dict[str, Any]) -> bool:
        return action.get("action") in {"delete_folder", "move_files"}

    def _is_allowed_path(self, path: str) -> bool:
        try:
            return self.config.is_path_allowed(path)
        except Exception:
            return False

    def _normalize_create_folder_path(self, base_path: str, destination: Optional[str]) -> str:
        """Resolve special folder aliases and join optional destination name for create_folder.

        Examples:
        - base_path="desktop", destination="saksham" => C:\\Users\\<user>\\Desktop\\saksham
        - base_path="C:\\Users\\...\\Desktop", destination="saksham" => join
        - base_path already absolute and no destination => unchanged
        """
        alias = base_path.strip().lower()
        user_home = os.path.expanduser("~")
        special_map = {
            "desktop": os.path.join(user_home, "Desktop"),
            "documents": os.path.join(user_home, "Documents"),
            "docs": os.path.join(user_home, "Documents"),
            "downloads": os.path.join(user_home, "Downloads"),
        }

        if alias in special_map:
            resolved_base = special_map[alias]
        else:
            resolved_base = base_path

        if not os.path.isabs(resolved_base):
            resolved_base = os.path.abspath(resolved_base)

        if destination and isinstance(destination, str) and destination.strip():
            return os.path.join(resolved_base, destination.strip())
        return resolved_base

    def _normalize_delete_folder_path(self, base_path: str, subfolder: Optional[str]) -> str:
        """Resolve aliases for delete_folder and optionally join a subfolder name.

        Supports cases like path="Desktop" with subfolder name in 'source' or 'destination'.
        """
        # Reuse create-folder normalization without joining a destination first
        resolved_base = self._normalize_create_folder_path(base_path, None)
        if subfolder and isinstance(subfolder, str) and subfolder.strip() and not os.path.isabs(subfolder):
            return os.path.join(resolved_base, subfolder.strip())
        return resolved_base


_validator_instance: Validator | None = None


def get_validator() -> Validator:
    global _validator_instance
    if _validator_instance is None:
        _validator_instance = Validator()
    return _validator_instance


