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
            # 1. Capture voice input
            transcript = next(self.voice_assistant.speech_to_text())

            # 2. Build a prompt that includes full chat history
            history = self.chat_screen.conversation_history  # [ChatGPT]
            context_prompt = f"{history}User: {transcript}\nAssistant:"  # [ChatGPT]

            # 3. Send it to the local LLaMA model
            response = self.voice_assistant.llama_query(context_prompt)  # For [ChatGPT], change to context_prompt. For [Siri], change to transcript

            # 4. Display on the chat screen

            # === ChatGPT-style ===
            self.stack.setCurrentWidget(self.chat_screen)  # [ChatGPT]
            self.chat_screen.add_message(transcript, response)  # [ChatGPT]

            # === Siri-style ===
            # self.stack.setCurrentWidget(self.siri_popup)  # [Siri]
            # self.siri_popup.show_query(transcript)        # [Siri]
            # self.siri_popup.show_response(response)       # [Siri]

        except Exception as e:
            print(f"❌ Error during assistant trigger: {e}")

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
