from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel
from PyQt6.QtCore import Qt

class MainMenuScreen(QWidget):
    def __init__(self, stack, weather_screen, voice_assistant):
        super().__init__()
        self.stack = stack
        self.weather_screen = weather_screen
        self.voice_assistant = voice_assistant

        self.setStyleSheet("background-color: black; color: white;")

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title = QLabel("Welcome! Sign up or Log in.")
        title.setStyleSheet("font-size: 32px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        new_user_button = QPushButton("New User")
        new_user_button.setFixedSize(200, 50)
        new_user_button.clicked.connect(self.go_to_enrollment)

        choose_user_button = QPushButton("Choose Profile")
        choose_user_button.setFixedSize(200, 50)
        choose_user_button.clicked.connect(self.go_to_profile_selection)

        layout.addWidget(title)
        layout.addSpacing(20)
        layout.addWidget(new_user_button)
        layout.addWidget(choose_user_button)

        self.setLayout(layout)

    def go_to_enrollment(self):
        from Screens.EnrollmentScreen import EnrollmentScreen
        enrollment_screen = EnrollmentScreen(
            self.stack,
            self.weather_screen,
            self.voice_assistant
        )
        self.stack.addWidget(enrollment_screen)
        self.stack.setCurrentWidget(enrollment_screen)

    def go_to_profile_selection(self):
        from Screens.SelectProfileScreen import SelectProfileScreen
        select_screen = SelectProfileScreen(
            self.stack,
            self.weather_screen
        )
        self.stack.addWidget(select_screen)
        self.stack.setCurrentWidget(select_screen)
