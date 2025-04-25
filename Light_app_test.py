import sys
from PyQt6.QtWidgets import QApplication, QStackedWidget, QPushButton
from Screens.loadingwheel import EnrollmentProgress
from Screens.Weather_screen import WeatherScreen
from Screens.ChatGPTScreen import ChatGPTScreen  # [ChatGPT]
# from Screens.SiriPopupScreen import SiriPopupScreen  # [Siri]

from PicoVoice import PicoVoiceEagle, DEV_MODE


class App:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.stack = QStackedWidget()
        self.stack.resize(1200, 800)

        self.voice_assistant = PicoVoiceEagle(load_profile=True)

        self.weather_screen = WeatherScreen()
        self.chat_screen = ChatGPTScreen(self.stack, self.weather_screen)  # [ChatGPT]
        self.chat_screen.voice_request_signal.connect(self.simulate_assistant_trigger)  # [ChatGPT]
        # self.siri_popup = SiriPopupScreen(self.stack, self.weather_screen)  # [Siri]

        self.enrollment_screen = EnrollmentProgress(
            self.stack,
            self.weather_screen,
            self.voice_assistant
        )

        self.test_button = QPushButton("🎤 Activate Assistant")
        self.test_button.clicked.connect(self.simulate_assistant_trigger)
        self.weather_screen.layout().addWidget(self.test_button)

        self.stack.addWidget(self.enrollment_screen)
        self.stack.addWidget(self.weather_screen)
        self.stack.addWidget(self.chat_screen)  # [ChatGPT]
        # self.stack.addWidget(self.siri_popup)  # [Siri]

    def simulate_assistant_trigger(self):
        try:
            transcript = next(self.voice_assistant.speech_to_text())
            self.stack.setCurrentWidget(self.chat_screen)
            self.process_transcript(transcript)
        except Exception as e:
            print(f"❌ Error during assistant trigger: {e}")

    def process_transcript(self, transcript):
        print("📥 Transcript:", transcript)

        command = transcript.lower()
        if "turn on the light" in command or "turn on the lights" in command:
            self.voice_assistant.govee_turn_on()
            self.voice_assistant.speak("Turning on the light.")
            self.chat_screen.add_message(transcript, "🟡 The light has been turned on.")
        elif "turn off the light" in command or "turn off the lights" in command:
            self.voice_assistant.govee_turn_off()
            self.voice_assistant.speak("Turning off the light.")
            self.chat_screen.add_message(transcript, "⚫ The light has been turned off.")
        elif "what time is it" in command:
            from datetime import datetime
            now = datetime.now().strftime("%I:%M %p")
            self.voice_assistant.speak(f"The current time is {now}.")
            self.chat_screen.add_message(transcript, f"🕒 The current time is {now}.")
        else:
            history = self.chat_screen.conversation_history
            context_prompt = f"{history}User: {transcript}\nAssistant:"
            response = self.voice_assistant.llama_query(context_prompt)
            self.chat_screen.add_message(transcript, response)

    def run(self):
        if DEV_MODE:
            self.stack.setCurrentWidget(self.weather_screen)
        else:
            self.stack.setCurrentWidget(self.enrollment_screen)

        self.stack.show()
        self.app.exec()


if __name__ == "__main__":
    app_instance = App()
    app_instance.run()
