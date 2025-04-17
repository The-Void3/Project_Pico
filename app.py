import sys
from PyQt6.QtWidgets import QApplication, QStackedWidget
from Screens.loadingwheel import EnrollmentProgress
from Screens.Weather_screen import WeatherScreen
from PicoVoice import PicoVoiceEagle


class App:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.stack = QStackedWidget()
        self.stack.resize(1200, 800)  # Set window size

        # Create the voice assistant instance
        self.voice_assistant = PicoVoiceEagle()

        # Initialize screens
        self.weather_screen = WeatherScreen()
        self.enrollment_screen = EnrollmentProgress(
            self.stack,
            self.weather_screen,
            self.voice_assistant
        )

        # Add screens to the stack
        self.stack.addWidget(self.enrollment_screen)
        self.stack.addWidget(self.weather_screen)

    def run(self):
        self.stack.setCurrentWidget(self.enrollment_screen)
        self.stack.show()
        sys.exit(self.app.exec())


if __name__ == "__main__":
    app_instance = App()
    app_instance.run()
