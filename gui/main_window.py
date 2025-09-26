from PySide6 import QtCore, QtWidgets
from typing import Dict, Any

from assistant.ai_layer import get_ai_layer
from assistant.validator import get_validator
from assistant.executor import get_executor
from assistant.logger import get_logger


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Windows AI Assistant")
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
        self.resize(720, 420)

        self.ai = get_ai_layer()
        self.validator = get_validator()
        self.executor = get_executor()
        self.logger = get_logger()

        self._build_ui()

    def _build_ui(self) -> None:
        central = QtWidgets.QWidget(self)
        layout = QtWidgets.QVBoxLayout(central)

        self.input_edit = QtWidgets.QPlainTextEdit()
        self.input_edit.setPlaceholderText("Describe what you want to do...")
        self.run_button = QtWidgets.QPushButton("Execute")
        self.confirm_checkbox = QtWidgets.QCheckBox("Confirm destructive actions (move/delete)")

        self.log_view = QtWidgets.QPlainTextEdit()
        self.log_view.setReadOnly(True)

        hl = QtWidgets.QHBoxLayout()
        hl.addWidget(self.run_button)
        hl.addWidget(self.confirm_checkbox)

        layout.addWidget(self.input_edit)
        layout.addLayout(hl)
        layout.addWidget(self.log_view)

        self.setCentralWidget(central)

        self.run_button.clicked.connect(self.on_execute_clicked)

    def append_log(self, text: str) -> None:
        self.log_view.appendPlainText(text)

    def on_execute_clicked(self) -> None:
        user_text = self.input_edit.toPlainText().strip()
        if not user_text:
            return
        try:
            action: Dict[str, Any] = self.ai.parse_command(user_text)
            ok, msg = self.validator.validate_action(action)
            if not ok:
                self.logger.log_validation_error(msg, action)
                self.append_log(f"Validation error: {msg}")
                return

            if self.validator.requires_confirmation(action) and not self.confirm_checkbox.isChecked():
                self.append_log("Confirmation required. Check the box and try again.")
                return

            if self.confirm_checkbox.isChecked():
                action["confirmed"] = True

            result = self.executor.execute(action)
            self.append_log(result)
        except Exception as exc:
            self.append_log(f"Error: {exc}")


def create_app() -> QtWidgets.QApplication:
    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
    return app


