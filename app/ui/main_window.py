from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QMainWindow,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from app.config import APP_NAME, APP_VERSION
from app.services.session_service import SessionService


class MainWindow(QMainWindow):
    def __init__(self, mock_mode: bool = False):
        super().__init__()
        self.mock_mode = mock_mode
        self.session_service = SessionService()
        self.setWindowTitle(f"{APP_NAME} {APP_VERSION}")
        self.resize(1100, 700)
        self._setup_ui()

    def _setup_ui(self) -> None:
        root = QWidget()
        self.setCentralWidget(root)
        layout = QVBoxLayout(root)

        top_bar = QHBoxLayout()
        self.mode_label = QLabel("Mode: Mock" if self.mock_mode else "Mode: Device")
        self.club_combo = QComboBox()
        self.club_combo.addItems(["Driver", "5-Wood", "7-Iron", "PW"])
        self.capture_button = QPushButton("Capture Mock Shot")
        self.capture_button.clicked.connect(self._capture_shot)
        top_bar.addWidget(self.mode_label)
        top_bar.addStretch()
        top_bar.addWidget(QLabel("Club:"))
        top_bar.addWidget(self.club_combo)
        top_bar.addWidget(self.capture_button)
        layout.addLayout(top_bar)

        self.table = QTableWidget(0, 7)
        self.table.setHorizontalHeaderLabels([
            "Time", "Club", "Speed", "Face", "Path", "Carry", "Lateral"
        ])
        layout.addWidget(self.table)

        bottom = QHBoxLayout()
        self.summary_list = QListWidget()
        self.insights_box = QTextEdit()
        self.insights_box.setReadOnly(True)
        bottom.addWidget(self.summary_list, 1)
        bottom.addWidget(self.insights_box, 2)
        layout.addLayout(bottom)

        self.statusBar().showMessage("Ready")

    def _capture_shot(self) -> None:
        record, summary, insights = self.session_service.capture_mock_shot(
            self.club_combo.currentText()
        )
        row = self.table.rowCount()
        self.table.insertRow(row)
        values = [
            record.timestamp,
            record.club,
            str(record.club_speed_mph),
            str(record.face_angle_deg),
            str(record.path_deg),
            str(record.carry_yards),
            str(record.lateral_yards),
        ]
        for column, value in enumerate(values):
            self.table.setItem(row, column, QTableWidgetItem(value))

        self.summary_list.clear()
        self.summary_list.addItem(f"Shots: {summary.shot_count}")
        self.summary_list.addItem(f"Avg carry: {summary.avg_carry} yd")
        self.summary_list.addItem(f"Avg lateral: {summary.avg_lateral} yd")
        self.summary_list.addItem(f"Max radius: {summary.max_radius} yd")
        self.summary_list.addItem(f"Dominant miss: {summary.dominant_miss}")
        self.insights_box.setPlainText("\n".join(insights))
        self.statusBar().showMessage("Mock shot captured", 3000)
