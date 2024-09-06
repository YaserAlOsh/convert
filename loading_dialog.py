from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt, QTimer, QSize
from PyQt6.QtGui import QMovie
from utils import resource_path

class LoadingDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Processing")
        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.WindowTitleHint | Qt.WindowType.CustomizeWindowHint)
        self.setFixedSize(200, 200)

        layout = QVBoxLayout()
        self.setLayout(layout)
        print("Spinner")
        # Create and set up the spinner label
        self.spinner_label = QLabel(self)
        self.movie = QMovie(resource_path("loading_spinner.gif"))
        self.movie.setScaledSize(QSize(50, 50))  # Adjust size as needed
        self.spinner_label.setMovie(self.movie)
        self.spinner_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        print("Processing")
        # Create and set up the text label
        self.text_label = QLabel("Processing...", self)
        self.text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Add widgets to layout
        layout.addWidget(self.spinner_label)
        layout.addWidget(self.text_label)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Set up the timer for text update
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_text)
        self.timer.start(500)
        self.dot_count = 0

        # Start the spinner animation
        self.start_animation()

    def update_text(self):
        self.dot_count = (self.dot_count + 1) % 4
        self.text_label.setText("Processing" + "." * self.dot_count)

    def start_animation(self):
        self.movie.start()

    def stop_animation(self):
        self.movie.stop()

    def closeEvent(self, event):
        self.stop_animation()
        event.accept()