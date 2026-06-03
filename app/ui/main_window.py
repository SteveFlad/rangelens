from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFileDialog,
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
from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QCloseEvent

from app.config import APP_NAME, APP_VERSION
from app.device.optishot_reader import OptiShotDeviceError
from app.services.session_service import SessionService


class MainWindow(QMainWindow):
    def __init__(self, mock_mode: bool = False):
        super().__init__()
        self.mock_mode = mock_mode
        self.session_service = SessionService(mock_mode=mock_mode)
        self.setWindowTitle(f"{APP_NAME} {APP_VERSION}")
        self.resize(1100, 700)
        self.auto_detect_enabled = False
        self._setup_ui()
        self._setup_auto_detect()

    def _setup_ui(self) -> None:
        root = QWidget()
        self.setCentralWidget(root)
        layout = QVBoxLayout(root)

        top_bar = QHBoxLayout()
        self.mode_label = QLabel("Mode: Mock" if self.mock_mode else "Mode: Device")
        self.auto_detect_checkbox = QCheckBox("Auto-Detect Swings")
        self.auto_detect_checkbox.stateChanged.connect(self._toggle_auto_detect)
        if self.mock_mode:
            self.auto_detect_checkbox.setEnabled(False)
            self.auto_detect_checkbox.setToolTip("Auto-detect not available in mock mode")
        self.club_combo = QComboBox()
        self.club_combo.addItems(["Driver", "5-Wood", "7-Iron", "PW"])
        self.capture_button = QPushButton("Capture Mock Shot" if self.mock_mode else "Capture Device Shot")
        self.capture_button.clicked.connect(self._capture_shot)
        self.export_button = QPushButton("Export Session")
        self.export_button.clicked.connect(self._export_session)
        top_bar.addWidget(self.mode_label)
        top_bar.addWidget(self.auto_detect_checkbox)
        top_bar.addStretch()
        top_bar.addWidget(QLabel("Club:"))
        top_bar.addWidget(self.club_combo)
        top_bar.addWidget(self.capture_button)
        top_bar.addWidget(self.export_button)
        layout.addLayout(top_bar)

        self.table = QTableWidget(0, 8)
        self.table.setHorizontalHeaderLabels([
            "Club", "Speed", "Face", "Path", "Contact", "Carry", "Lateral", "Shape"
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

    def _setup_auto_detect(self) -> None:
        """Setup timer for automatic swing detection."""
        self.auto_detect_timer = QTimer()
        self.auto_detect_timer.timeout.connect(self._check_for_swing)
        self.auto_detect_timer.setInterval(50)  # Check every 50ms

    def _toggle_auto_detect(self, state: int) -> None:
        """Enable or disable automatic swing detection."""
        self.auto_detect_enabled = (state == 2)  # Qt.CheckState.Checked
        
        if self.auto_detect_enabled:
            self.capture_button.setEnabled(False)
            self.auto_detect_timer.start()
            self.statusBar().showMessage("Auto-detect enabled - waiting for swing...")
        else:
            self.auto_detect_timer.stop()
            self.capture_button.setEnabled(True)
            self.statusBar().showMessage("Auto-detect disabled")

    def _check_for_swing(self) -> None:
        """Check for swing detection in auto-detect mode."""
        if not self.auto_detect_enabled or self.mock_mode:
            return
        
        try:
            shot = self.session_service.reader.check_for_swing(self.club_combo.currentText())
            if shot is not None:
                # Process the detected shot
                self._process_shot(shot)
        except OptiShotDeviceError as exc:
            self.statusBar().showMessage(str(exc), 5000)
            self.auto_detect_checkbox.setChecked(False)

    def _process_shot(self, shot_input) -> None:
        """Process and display a captured shot."""
        from app.analytics.ball_flight import estimate_shot
        from app.analytics.dispersion import summarize_dispersion
        from app.analytics.coaching_rules import coaching_insights
        
        record = estimate_shot(shot_input)
        self.session_service.shots.append(record)
        summary = summarize_dispersion(self.session_service.shots)
        insights = coaching_insights(summary)
        
        row = self.table.rowCount()
        self.table.insertRow(row)
        values = [
            record.club,
            str(record.club_speed_mph),
            str(record.face_angle_deg),
            str(record.path_deg),
            str(record.contact_point),
            str(record.carry_yards),
            str(record.lateral_yards),
            record.shot_shape,
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
        self.statusBar().showMessage("Shot detected and captured!", 2000)

    def _capture_shot(self) -> None:
        try:
            record, summary, insights = self.session_service.capture_shot(
                self.club_combo.currentText()
            )
        except OptiShotDeviceError as exc:
            self.statusBar().showMessage(str(exc), 5000)
            return
        row = self.table.rowCount()
        self.table.insertRow(row)
        values = [
            record.club,
            str(record.club_speed_mph),
            str(record.face_angle_deg),
            str(record.path_deg),
            str(record.contact_point),
            str(record.carry_yards),
            str(record.lateral_yards),
            record.shot_shape,
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
        source = "Mock" if self.mock_mode else "Device"
        self.statusBar().showMessage(f"{source} shot captured", 3000)

    def _export_session(self) -> None:
        if not self.session_service.shots:
            self.statusBar().showMessage("No shots to export", 3000)
            return
        
        default_filename = self.session_service.get_export_filename()
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Export Session",
            default_filename,
            "CSV Files (*.csv);;All Files (*)"
        )
        
        if filename:
            try:
                self.session_service.export_to_csv(filename)
                self.statusBar().showMessage(f"Session exported to {filename}", 5000)
            except Exception as e:
                self.statusBar().showMessage(f"Export failed: {e}", 5000)

    def closeEvent(self, event: QCloseEvent) -> None:
        if self.auto_detect_enabled:
            self.auto_detect_timer.stop()
        self.session_service.close()
        super().closeEvent(event)
