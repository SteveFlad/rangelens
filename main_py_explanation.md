# main.py Code Explanation

This document provides a detailed line-by-line explanation of `app/main.py`.

## Overview
This is the entry point for the RangeLens application, a PyQt6-based GUI application for golf swing analysis.

---

## Code Breakdown

### Lines 1-3: Standard Library Imports
```python
import argparse
import logging
import sys
```
- `import argparse` - Imports Python's command-line argument parsing library
- `import logging` - Imports Python's logging framework for application logging
- `import sys` - Imports system-specific parameters and functions (needed for sys.argv and exit codes)

### Line 5: PyQt6 Import
```python
from PyQt6.QtWidgets import QApplication
```
- Imports the main application class from PyQt6, which manages the GUI application's control flow and settings

### Line 7: Local Import
```python
from app.ui.main_window import MainWindow
```
- Imports the MainWindow class that defines the application's primary user interface

### Lines 10-13: Command-line Argument Parser
```python
def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="RangeLens")
    parser.add_argument("--mock", action="store_true", help="Run in mock mode")
    return parser.parse_args()
```
- `def parse_args() -> argparse.Namespace:` - Defines a function that returns parsed command-line arguments
- `parser = argparse.ArgumentParser(description="RangeLens")` - Creates an argument parser for the RangeLens application
- `parser.add_argument("--mock", action="store_true", help="Run in mock mode")` - Adds a `--mock` flag option that users can pass to run the app in mock mode (simulated data instead of real device)
- `return parser.parse_args()` - Parses the command-line arguments and returns them as a Namespace object

### Lines 16-29: Main Application Entry Point
```python
def main() -> int:
    # Configure logging to show timestamps and level
    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s] %(levelname)s: %(message)s',
        datefmt='%H:%M:%S'
    )
    
    args = parse_args()
    app = QApplication(sys.argv)
    window = MainWindow(mock_mode=args.mock)
    window.show()
    return app.exec()
```
- `def main() -> int:` - Defines the main function that runs the application and returns an integer exit code
- `logging.basicConfig(` - Configures the logging system with default settings
- `level=logging.INFO,` - Sets log level to INFO (shows INFO, WARNING, ERROR, and CRITICAL messages)
- `format='[%(asctime)s] %(levelname)s: %(message)s',` - Sets log message format to show timestamp, log level, and message
- `datefmt='%H:%M:%S'` - Formats timestamps as hours:minutes:seconds
- `)` - Closes the logging configuration
- `args = parse_args()` - Calls the argument parser to get command-line arguments
- `app = QApplication(sys.argv)` - Creates the PyQt6 application object, passing command-line arguments
- `window = MainWindow(mock_mode=args.mock)` - Creates the main window, passing whether to run in mock mode
- `window.show()` - Displays the main window on screen
- `return app.exec()` - Starts the Qt event loop and returns the exit code when the app closes

### Lines 32-33: Python Entry Point
```python
if __name__ == "__main__":
    raise SystemExit(main())
```
- `if __name__ == "__main__":` - Checks if the script is being run directly (not imported as a module)
- `raise SystemExit(main())` - Calls the main function and exits with its return code (cleaner than sys.exit())

---

## Summary

This is a standard PyQt6 application entry point that:
1. Sets up logging with timestamps
2. Parses command-line arguments for optional mock mode
3. Creates the GUI application and main window
4. Starts the Qt event loop
5. Returns the application exit code when closed

## Usage

Run normally:
```bash
python -m app.main
```

Run in mock mode (with simulated data):
```bash
python -m app.main --mock
```
