from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QGraphicsOpacityEffect
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation
from PyQt6.QtGui import QFont

class SiriPopupScreen(QWidget):
    def __init__(self, stack, weather_screen):
        super().__init__()
        self.stack = stack
        self.weather_screen = weather_screen

        self.setStyleSheet("background-color: rgba(0, 0, 0, 200);")

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.listening_label = QLabel("🎤 Listening...")
        self.listening_label.setFont(QFont("Arial", 24))
        self.listening_label.setStyleSheet("color: white;")
        self.listening_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.query_label = QLabel("")
        self.query_label.setFont(QFont("Arial", 18))
        self.query_label.setStyleSheet("color: lightgray;")
        self.query_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.response_label = QLabel("")
        self.response_label.setFont(QFont("Arial", 20))
        self.response_label.setStyleSheet("color: white;")
        self.response_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(self.listening_label)
        layout.addSpacing(20)
        layout.addWidget(self.query_label)
        layout.addWidget(self.response_label)
        self.setLayout(layout)

        # Fade animation setup
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)
        self.fade_anim = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_anim.setDuration(400)

    def show_query(self, query: str):
        self.query_label.setText(f"You said: {query}")
        self.fade_in()

    def show_response(self, response: str):
        self.response_label.setText(response)
        QTimer.singleShot(5000, self.fade_out)

    def fade_in(self):
        self.opacity_effect.setOpacity(0.0)
        self.stack.setCurrentWidget(self)
        self.fade_anim.stop()
        self.fade_anim.setStartValue(0.0)
        self.fade_anim.setEndValue(1.0)
        self.fade_anim.start()

    def fade_out(self):
        self.fade_anim.stop()
        self.fade_anim.setStartValue(1.0)
        self.fade_anim.setEndValue(0.0)
        self.fade_anim.start()
        self.fade_anim.finished.connect(self.hide_popup)

    def hide_popup(self):
        self.stack.setCurrentWidget(self.weather_screen)
