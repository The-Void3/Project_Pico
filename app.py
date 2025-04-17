import sys
from PyQt6.QtWidgets import QApplication, QStackedWidget, QPushButton
from Screens.loadingwheel import EnrollmentProgress
from Screens.Weather_screen import WeatherScreen
from Screens.SiriPopupScreen import SiriPopupScreen
from PicoVoice import PicoVoiceEagle


class App:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.stack = QStackedWidget()
        self.stack.resize(1200, 800)

        self.voice_assistant = PicoVoiceEagle()

        # Initialize screens
        self.weather_screen = WeatherScreen()
        self.siri_popup = SiriPopupScreen(self.stack, self.weather_screen)
        self.enrollment_screen = EnrollmentProgress(
            self.stack,
            self.weather_screen,
            self.voice_assistant
        )

        # Test button to simulate wake word trigger
        self.test_button = QPushButton("🎤 Activate Assistant")
        self.test_button.clicked.connect(self.simulate_assistant_trigger)
        self.weather_screen.layout().addWidget(self.test_button)

        # Add screens to stack
        self.stack.addWidget(self.enrollment_screen)
        self.stack.addWidget(self.weather_screen)
        self.stack.addWidget(self.siri_popup)

    def simulate_assistant_trigger(self):
        self.stack.setCurrentWidget(self.siri_popup)
        self.siri_popup.show_query("What's the weather?")
        self.siri_popup.show_response("It's 75°F and sunny in McAllen.")

    def run(self):
        self.stack.setCurrentWidget(self.enrollment_screen)
        self.stack.show()
        sys.exit(self.app.exec())


if __name__ == "__main__":
    app_instance = App()
    app_instance.run()
