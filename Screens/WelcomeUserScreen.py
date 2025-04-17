from PyQt6.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

class WelcomeUserScreen(QWidget):
    def __init__(self, stack, weather_screen, user_name):
        super().__init__()
        self.stack = stack
        self.weather_screen = weather_screen
        self.user_name = user_name

        self.setStyleSheet("background-color: black; color: white;")

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.title_label = QLabel(f"Welcome, {self.user_name}!")
        self.title_label.setFont(QFont("Arial", 24))
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.get_started_button = QPushButton("GET STARTED")
        self.get_started_button.setFixedWidth(400)
        self.get_started_button.clicked.connect(self.goto_weather)

        layout.addWidget(self.title_label)
        layout.addSpacing(20)
        layout.addWidget(self.get_started_button)

        self.setLayout(layout)

    def goto_weather(self):
        # Only after login or enrollment can they see "Get Started"
        self.stack.setCurrentWidget(self.weather_screen)
