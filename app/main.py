import argparse
import logging
import sys
from pathlib import Path

try:
    from PyQt6.QtWidgets import QApplication
except ModuleNotFoundError as exc:
    if exc.name == "PyQt6":
        raise SystemExit(
            "PyQt6 is not installed in the active Python environment.\n"
            "Activate the project venv and install dependencies:\n"
            "  .\\.venv\\Scripts\\Activate.ps1\n"
            "  pip install -r requirements.txt\n"
            "Then run: python -m app.main --mock"
        ) from exc
    raise

if __package__ in (None, ""):
    # Support direct execution: python app/main.py
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.ui.main_window import MainWindow


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="RangeLens")
    parser.add_argument("--mock", action="store_true", help="Run in mock mode")
    return parser.parse_args()


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


if __name__ == "__main__":
    raise SystemExit(main())
