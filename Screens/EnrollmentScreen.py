import sys
import json
import os
from PyQt6.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
from PicoVoice import PicoVoiceEagle

from Screens.WelcomeUserScreen import WelcomeUserScreen

PROFILE_PATH = "profiles.json"

class EnrollmentScreen(QWidget):
    def __init__(self, stack, weather_screen, voice_assistant):
        super().__init__()
        self.stack = stack
        self.weather_screen = weather_screen
        self.voice_assistant = voice_assistant

        self.setStyleSheet("background-color: black; color: white;")

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.title = QLabel("Create New Profile")
        self.title.setFont(QFont("Arial", 24))
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter your name")
        self.name_input.setFixedWidth(300)

        self.pin_input = QLineEdit()
        self.pin_input.setPlaceholderText("Enter 4-digit PIN")
        self.pin_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.pin_input.setMaxLength(4)
        self.pin_input.setFixedWidth(300)

        self.enroll_button = QPushButton("Start Voice Enrollment")
        self.enroll_button.setFixedWidth(200)
        self.enroll_button.clicked.connect(self.start_enrollment)

        layout.addWidget(self.title)
        layout.addSpacing(20)
        layout.addWidget(self.name_input)
        layout.addWidget(self.pin_input)
        layout.addSpacing(20)
        layout.addWidget(self.enroll_button)

        self.setLayout(layout)

    def start_enrollment(self):
        name = self.name_input.text().strip()
        pin = self.pin_input.text().strip()

        if not name or not pin.isdigit() or len(pin) != 4:
            QMessageBox.warning(self, "Invalid Input", "Please enter a valid name and 4-digit PIN.")
            return

        QMessageBox.information(self, "Voice Enrollment", "Please speak into your microphone until the enrollment process is complete.")

        # Voice enrollment
        self.voice_assistant.enroll()

        self.save_profile(name, pin)
        QMessageBox.information(self, "Success", "Enrollment complete!")

        # After enrolling, go to the WelcomeUserScreen
        welcome_screen = WelcomeUserScreen(self.stack, self.weather_screen, user_name=name)
        self.stack.addWidget(welcome_screen)
        self.stack.setCurrentWidget(welcome_screen)

    def save_profile(self, name, pin):
        data = {}
        if os.path.exists(PROFILE_PATH):
            with open(PROFILE_PATH, "r") as f:
                data = json.load(f)

        data[name] = pin
        with open(PROFILE_PATH, "w") as f:
            json.dump(data, f, indent=4)
