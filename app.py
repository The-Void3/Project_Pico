import sys
from PyQt6.QtWidgets import QApplication, QStackedWidget, QPushButton
from Screens.loadingwheel import EnrollmentProgress
from Screens.Weather_screen import WeatherScreen
from Screens.SiriPopupScreen import SiriPopupScreen
from PicoVoice import PicoVoiceEagle, DEV_MODE


class App:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.stack = QStackedWidget()
        self.stack.resize(1200, 800)

        self.voice_assistant = PicoVoiceEagle(load_profile=True)

        self.weather_screen = WeatherScreen()
        self.siri_popup = SiriPopupScreen(self.stack, self.weather_screen)
        self.enrollment_screen = EnrollmentProgress(
            self.stack,
            self.weather_screen,
            self.voice_assistant
        )

        self.test_button = QPushButton("🎤 Activate Jarvis")
        self.test_button.clicked.connect(self.simulate_assistant_trigger)
        self.weather_screen.layout().addWidget(self.test_button)

        self.stack.addWidget(self.enrollment_screen)
        self.stack.addWidget(self.weather_screen)
        self.stack.addWidget(self.siri_popup)

    def simulate_assistant_trigger(self):
        try:
            # 1. Capture voice input using Vosk
            transcript = next(self.voice_assistant.speech_to_text())

            # 2. Send to local LLaMA model
            response = self.voice_assistant.llama_query(transcript)

            # 3. Display on the popup
            self.siri_popup.show_query(transcript)
            self.siri_popup.show_response(response)

        except Exception as e:
            print(f"❌ Error during assistant trigger: {e}")

    def run(self):
        if DEV_MODE:
            self.stack.setCurrentWidget(self.weather_screen)
        else:
            self.stack.setCurrentWidget(self.enrollment_screen)
        self.stack.show()
        sys.exit(self.app.exec())


if __name__ == "__main__":
    app_instance = App()
    app_instance.run()
