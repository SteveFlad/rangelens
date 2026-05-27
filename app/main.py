import argparse
import sys

from PyQt6.QtWidgets import QApplication

from app.ui.main_window import MainWindow


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="RangeLens")
    parser.add_argument("--mock", action="store_true", help="Run in mock mode")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    app = QApplication(sys.argv)
    window = MainWindow(mock_mode=args.mock)
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
