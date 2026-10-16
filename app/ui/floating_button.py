"""Small floating button window that stays on top to recall main window."""
from PyQt6.QtWidgets import QWidget, QPushButton, QVBoxLayout
from PyQt6.QtCore import Qt, QPoint, QTimer
from PyQt6.QtGui import QMouseEvent


class FloatingButton(QWidget):
    """A small, draggable, always-on-top button to bring main window to front."""
    
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.dragging = False
        self.drag_position = QPoint()
        self.mouse_press_pos = None  # Track where mouse was pressed
        
        # Make window frameless and always on top
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool  # Prevents taskbar icon
        )
        
        # Set window properties
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(80, 80)
        
        # Create layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Create button (for display only - clicks handled at widget level)
        self.button = QPushButton("RL\nShow")
        self.button.setStyleSheet("""
            QPushButton {
                background-color: rgba(0, 120, 215, 220);
                color: white;
                border: 2px solid rgba(0, 100, 200, 255);
                border-radius: 35px;
                font-size: 12px;
                font-weight: bold;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: rgba(0, 140, 235, 240);
                border: 2px solid rgba(0, 120, 220, 255);
            }
            QPushButton:pressed {
                background-color: rgba(0, 100, 195, 255);
            }
        """)
        # Don't connect clicked - we'll handle at widget level
        self.button.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        # Install event filter to capture button's mouse events
        self.button.installEventFilter(self)
        layout.addWidget(self.button)
        self.update_button_label(next_action_show_rangelens=True)
        
        # Position after a short delay to ensure Qt is fully initialized
        QTimer.singleShot(100, self._position_initial)
    
    def _position_initial(self):
        """Position in bottom-right corner of screen."""
        try:
            from PyQt6.QtGui import QGuiApplication
            screen = QGuiApplication.primaryScreen()
            if screen:
                geometry = screen.geometry()
                # Position with some margin from edge
                # Use geometry.x() and geometry.y() to account for screen position
                x = geometry.x() + geometry.width() - self.width() - 20
                y = geometry.y() + geometry.height() - self.height() - 80  # Account for taskbar
                self.move(x, y)
            else:
                # Fallback position
                self.move(100, 100)
        except Exception:
            # If anything goes wrong, use a safe default position
            self.move(100, 100)
    
    def update_button_label(self, next_action_show_rangelens: bool) -> None:
        """Update button text to indicate what the next click will show."""
        if next_action_show_rangelens:
            self.button.setText("RL\nShow")
        else:
            self.button.setText("OS\nShow")

    def _toggle_window_target(self) -> None:
        """Toggle between showing RangeLens and revealing OptiShot."""
        is_rangelens_shown = self.main_window.toggle_rangelens_optishot()
        self.update_button_label(next_action_show_rangelens=not is_rangelens_shown)
    
    def eventFilter(self, obj, event):
        """Filter events from the button to handle dragging."""
        if obj == self.button:
            if event.type() == event.Type.MouseButtonPress:
                self.mousePressEvent(event)
                return True
            elif event.type() == event.Type.MouseMove:
                self.mouseMoveEvent(event)
                return True
            elif event.type() == event.Type.MouseButtonRelease:
                self.mouseReleaseEvent(event)
                return True
        return super().eventFilter(obj, event)
    
    def mousePressEvent(self, event: QMouseEvent):
        """Start dragging the button."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = False  # Not dragging yet
            self.mouse_press_pos = event.globalPosition().toPoint()
            self.drag_position = self.mouse_press_pos - self.frameGeometry().topLeft()
            event.accept()
    
    def mouseMoveEvent(self, event: QMouseEvent):
        """Drag the button around the screen."""
        if event.buttons() == Qt.MouseButton.LeftButton and self.mouse_press_pos:
            # Check if mouse moved enough to be considered a drag (not just a click)
            distance = (event.globalPosition().toPoint() - self.mouse_press_pos).manhattanLength()
            if distance > 5 or self.dragging:  # 5 pixel threshold
                self.dragging = True
                self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()
    
    def mouseReleaseEvent(self, event: QMouseEvent):
        """Stop dragging or show main window on click."""
        if event.button() == Qt.MouseButton.LeftButton:
            if not self.dragging and self.mouse_press_pos:
                # This was a click, not a drag - toggle displayed app
                self._toggle_window_target()
            self.dragging = False
            self.mouse_press_pos = None
            event.accept()
    
    def mouseDoubleClickEvent(self, event: QMouseEvent):
        """Double-click to toggle displayed app."""
        if event.button() == Qt.MouseButton.LeftButton:
            self._toggle_window_target()
            event.accept()
