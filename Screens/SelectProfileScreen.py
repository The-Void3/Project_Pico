import json
import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QListWidget,
    QLineEdit, QMessageBox
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
from Screens.WelcomeUserScreen import WelcomeUserScreen

PROFILE_PATH = "profiles.json"

class SelectProfileScreen(QWidget):
    def __init__(self, stack, weather_screen):
        super().__init__()
        self.stack = stack
        self.weather_screen = weather_screen

        self.setStyleSheet("background-color: black; color: white;")

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title = QLabel("Select Profile")
        title.setFont(QFont("Arial", 24))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.profile_list = QListWidget()
        self.profile_list.setStyleSheet("background-color: white; color: black;")
        self.profile_list.setFixedWidth(300)

        self.load_profiles()

        self.pin_input = QLineEdit()
        self.pin_input.setPlaceholderText("Enter 4-digit PIN")
        self.pin_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.pin_input.setMaxLength(4)
        self.pin_input.setFixedWidth(300)

        login_button = QPushButton("Log In")
        login_button.clicked.connect(self.authenticate_profile)

        layout.addWidget(title)
        layout.addSpacing(20)
        layout.addWidget(self.profile_list)
        layout.addWidget(self.pin_input)
        layout.addWidget(login_button)

        self.setLayout(layout)

    def load_profiles(self):
        self.profile_list.clear()
        if os.path.exists(PROFILE_PATH):
            with open(PROFILE_PATH, "r") as f:
                data = json.load(f)
                # data is { "Alice": "1234", "Bob": "4321" }
                for name in data.keys():
                    self.profile_list.addItem(name)

    def authenticate_profile(self):
        selected_item = self.profile_list.currentItem()
        entered_pin = self.pin_input.text().strip()

        if not selected_item:
            QMessageBox.warning(self, "No Profile", "Please select a profile.")
            return

        if not entered_pin:
            QMessageBox.warning(self, "Empty PIN", "Please enter your PIN.")
            return

        profile_name = selected_item.text()

        if os.path.exists(PROFILE_PATH):
            with open(PROFILE_PATH, "r") as f:
                data = json.load(f)
                if profile_name in data:
                    if data[profile_name] == entered_pin:
                        # Valid login -> Welcome screen
                        welcome_screen = WelcomeUserScreen(self.stack, self.weather_screen, user_name=profile_name)
                        self.stack.addWidget(welcome_screen)
                        self.stack.setCurrentWidget(welcome_screen)
                        return
                    else:
                        QMessageBox.warning(self, "Invalid PIN", "Incorrect PIN. Try again.")
                        return

        QMessageBox.critical(self, "Error", "Profile not found or corrupted.")
