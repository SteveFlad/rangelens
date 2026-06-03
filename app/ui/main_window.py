from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QMainWindow,
    QMessageBox,
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


def _describe_face_angle(face_angle_deg: float) -> str:
    """Add description to face angle value."""
    if abs(face_angle_deg) < 1.0:
        desc = "square"
    elif face_angle_deg < 0:
        desc = "closed"
    else:
        desc = "open"
    return f"{face_angle_deg} ({desc})"


def _describe_path(path_deg: float) -> str:
    """Add description to path value."""
    if abs(path_deg) < 1.0:
        desc = "square"
    elif path_deg > 0:
        desc = "in-to-out"
    else:
        desc = "out-to-in"
    return f"{path_deg} ({desc})"


def _describe_contact(contact_point: float) -> str:
    """Add description to contact point value."""
    if abs(contact_point) < 0.5:
        desc = "center"
    elif contact_point < 0:
        desc = "toe"
    else:
        desc = "heel"
    return f"{contact_point} ({desc})"


class MainWindow(QMainWindow):
    def __init__(self, mock_mode: bool = False):
        super().__init__()
        self.mock_mode = mock_mode
        self.session_service = SessionService(mock_mode=mock_mode)
        self.setWindowTitle(f"{APP_NAME} {APP_VERSION}")
        self.resize(1100, 700)
        self.auto_detect_enabled = False
        self._error_disabled = False  # Track if disabled due to error
        self._setup_ui()
        self._setup_auto_detect()

    def _setup_ui(self) -> None:
        root = QWidget()
        self.setCentralWidget(root)
        layout = QVBoxLayout(root)

        top_bar = QHBoxLayout()
        self.mode_label = QLabel("Mode: Mock" if self.mock_mode else "Mode: Device")
        
        # LED status indicator
        self.led_indicator = QLabel("●")
        self.led_indicator.setStyleSheet("font-size: 20px; color: gray;")
        self.led_indicator.setToolTip("Pad Status")
        if not self.mock_mode:
            self._set_led_green()
        
        self.auto_detect_checkbox = QCheckBox("Auto-Detect Swings")
        self.auto_detect_checkbox.stateChanged.connect(self._toggle_auto_detect)
        if self.mock_mode:
            self.auto_detect_checkbox.setEnabled(False)
            self.auto_detect_checkbox.setToolTip("Auto-detect not available in mock mode")
        self.club_combo = QComboBox()
        self.club_combo.addItems(["Driver", "5-Wood", "7-Iron", "PW"])
        self.capture_button = QPushButton("Capture Mock Shot" if self.mock_mode else "Capture Device Shot")
        self.capture_button.clicked.connect(self._capture_shot)
        self.import_button = QPushButton("Import Session")
        self.import_button.clicked.connect(self._import_session)
        self.clear_button = QPushButton("Clear Session")
        self.clear_button.clicked.connect(self._clear_session)
        self.export_button = QPushButton("Export Session")
        self.export_button.clicked.connect(self._export_session)
        top_bar.addWidget(self.mode_label)
        top_bar.addWidget(self.led_indicator)
        top_bar.addWidget(self.auto_detect_checkbox)
        top_bar.addStretch()
        top_bar.addWidget(QLabel("Club:"))
        top_bar.addWidget(self.club_combo)
        top_bar.addWidget(self.capture_button)
        top_bar.addWidget(self.import_button)
        top_bar.addWidget(self.clear_button)
        top_bar.addWidget(self.export_button)
        layout.addLayout(top_bar)

        self.table = QTableWidget(0, 8)
        self.table.setHorizontalHeaderLabels([
            "Club", "Speed Mph", "Face", "Path", "Contact", "Carry Yds", "Lateral Yds", "Shape"
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

    def _set_led_green(self) -> None:
        """Set LED indicator to green (ready)."""
        self.led_indicator.setStyleSheet("font-size: 20px; color: #00ff00;")
        self.led_indicator.setToolTip("Pad Status: Ready")
    
    def _set_led_red(self) -> None:
        """Set LED indicator to red (busy)."""
        self.led_indicator.setStyleSheet("font-size: 20px; color: #ff0000;")
        self.led_indicator.setToolTip("Pad Status: Busy")
    
    def _toggle_auto_detect(self, state: int) -> None:
        """Enable or disable automatic swing detection."""
        self.auto_detect_enabled = (state == 2)  # Qt.CheckState.Checked
        
        if self.auto_detect_enabled:
            self._error_disabled = False  # Clear error flag when re-enabling
            self.capture_button.setEnabled(False)
            self.auto_detect_timer.start()
            self.statusBar().showMessage("Auto-detect enabled - waiting for swing...")
        else:
            self.auto_detect_timer.stop()
            self.capture_button.setEnabled(True)
            # Only show "disabled" message if it wasn't an error that caused the disable
            if not self._error_disabled:
                self.statusBar().showMessage("Auto-detect disabled")
            self._error_disabled = False  # Reset flag

    def _check_for_swing(self) -> None:
        """Check for swing detection in auto-detect mode."""
        if not self.auto_detect_enabled or self.mock_mode:
            return
        
        try:
            shot = self.session_service.reader.check_for_swing(self.club_combo.currentText())
            if shot is not None:
                # Process the detected shot
                self._set_led_red()  # Indicate busy processing
                self._process_shot(shot)
                self._set_led_green()  # Back to ready
        except OptiShotDeviceError as exc:
            # Check if this is a transient sensor error (invalid reading) or fatal device error
            error_str = str(exc)
            is_transient = ("invalid club speed" in error_str or 
                           "invalid swing speed" in error_str or
                           "did not contain a valid" in error_str)
            
            if is_transient:
                # Transient sensor error - log it but keep auto-detect running
                error_msg = f"Sensor Error: {exc} (Try again)"
                self._log_error(error_msg)
                self.statusBar().showMessage(error_msg, 4000)
                self._set_led_green()
            else:
                # Fatal device error - disable auto-detect
                error_msg = f"Device Error: {exc}"
                self._log_error(error_msg)
                self.statusBar().showMessage(error_msg, 10000)
                self._error_disabled = True
                self.auto_detect_checkbox.setChecked(False)
                self._set_led_green()
        except Exception as exc:
            # Log unexpected errors but keep auto-detect running
            error_msg = f"Warning: {exc}"
            self._log_error(error_msg)
            self.statusBar().showMessage(error_msg, 5000)
            self._set_led_green()

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
            _describe_face_angle(record.face_angle_deg),
            _describe_path(record.path_deg),
            _describe_contact(record.contact_point),
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

    def _log_error(self, message: str) -> None:
        """Log error message to insights box."""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        error_log = f"[{timestamp}] ERROR: {message}\n\n"
        current_text = self.insights_box.toPlainText()
        self.insights_box.setPlainText(error_log + current_text)

    def _capture_shot(self) -> None:
        if not self.mock_mode:
            self._set_led_red()  # Indicate busy capturing
        try:
            record, summary, insights = self.session_service.capture_shot(
                self.club_combo.currentText()
            )
        except OptiShotDeviceError as exc:
            self.statusBar().showMessage(str(exc), 5000)
            if not self.mock_mode:
                self._set_led_green()
            return
        row = self.table.rowCount()
        self.table.insertRow(row)
        values = [
            record.club,
            str(record.club_speed_mph),
            _describe_face_angle(record.face_angle_deg),
            _describe_path(record.path_deg),
            _describe_contact(record.contact_point),
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
        
        if not self.mock_mode:
            self._set_led_green()  # Back to ready

    def _import_session(self) -> None:
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Import Session",
            "",
            "RangeLens Files (LENS_*.csv);;CSV Files (*.csv);;All Files (*)"
        )
        
        if filename:
            try:
                count = self.session_service.import_from_csv(filename)
                self._refresh_display()
                self.statusBar().showMessage(f"Imported {count} shot(s) from {filename}", 5000)
            except Exception as e:
                self.statusBar().showMessage(f"Import failed: {e}", 5000)

    def _refresh_display(self) -> None:
        """Refresh the entire display with current session data."""
        from app.analytics.dispersion import summarize_dispersion
        from app.analytics.coaching_rules import coaching_insights
        
        # Clear and repopulate table
        self.table.setRowCount(0)
        for record in self.session_service.shots:
            row = self.table.rowCount()
            self.table.insertRow(row)
            values = [
                record.club,
                str(record.club_speed_mph),
                _describe_face_angle(record.face_angle_deg),
                _describe_path(record.path_deg),
                _describe_contact(record.contact_point),
                str(record.carry_yards),
                str(record.lateral_yards),
                record.shot_shape,
            ]
            for column, value in enumerate(values):
                self.table.setItem(row, column, QTableWidgetItem(value))
        
        # Update summary and insights
        if self.session_service.shots:
            summary = summarize_dispersion(self.session_service.shots)
            insights = coaching_insights(summary)
            
            self.summary_list.clear()
            self.summary_list.addItem(f"Shots: {summary.shot_count}")
            self.summary_list.addItem(f"Avg carry: {summary.avg_carry} yd")
            self.summary_list.addItem(f"Avg lateral: {summary.avg_lateral} yd")
            self.summary_list.addItem(f"Max radius: {summary.max_radius} yd")
            self.summary_list.addItem(f"Dominant miss: {summary.dominant_miss}")
            self.insights_box.setPlainText("\n".join(insights))
        else:
            self.summary_list.clear()
            self.insights_box.clear()

    def _clear_session(self) -> None:
        """Clear all session data without saving."""
        if not self.session_service.shots:
            self.statusBar().showMessage("No shots to clear", 3000)
            return
        
        # Clear the session data
        self.session_service.shots.clear()
        
        # Clear the display
        self.table.setRowCount(0)
        self.summary_list.clear()
        self.insights_box.clear()
        
        self.statusBar().showMessage("Session cleared", 3000)

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
