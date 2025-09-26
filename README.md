# Windows AI Assistant (Groq API)

A Windows desktop assistant with an always-on GUI that parses natural language via Groq API into structured actions and executes OS-level tasks (create folder, move files, open apps, delete folders) with validation and logging.

## Requirements

- Python 3.10+
- Windows 10/11

## Setup

1. Create a `.env` file (or copy `docs.env.example` to `.env`) with:

```
GROQ_API_KEY=your_api_key_here
ALLOWED_DIRECTORIES=C:\Users\%USERNAME%\Desktop,C:\Users\%USERNAME%\Documents
LOG_FILE_PATH=assistant.log
DEFAULT_TEXT_EDITOR=notepad.exe
DEFAULT_BROWSER=start
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Run

```bash
python main.py
```

## Usage

- Type a command like:
  - "Create a folder called Reports on my Desktop"
  - "Move C:\\Users\\<you>\\Desktop\\a.txt to C:\\Users\\<you>\\Documents"
  - "Open notepad"
  - "Delete the folder C:\\Users\\<you>\\Desktop\\Old"
- Check the "Confirm destructive actions" box for move/delete.

## Notes

- All actions are validated against `ALLOWED_DIRECTORIES`.
- Logs written to `LOG_FILE_PATH`.

## Modules

- `assistant/ai_layer.py`: Groq API integration
- `assistant/validator.py`: Validates actions and paths
- `assistant/executor.py`: Executes filesystem/app actions
- `assistant/logger.py`: Logging utility
- `assistant/config.py`: Environment-backed configuration
- `gui/main_window.py`: PySide6 GUI
- `main.py`: Entrypoint
