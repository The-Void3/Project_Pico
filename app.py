import sys
import threading
import time
from PyQt6.QtWidgets import QApplication, QStackedWidget, QPushButton
from PyQt6.QtCore import QObject, pyqtSignal

from Screens.loadingwheel import EnrollmentProgress
from Screens.Weather_screen import WeatherScreen
from Screens.ChatGPTScreen import ChatGPTScreen  # [ChatGPT]
# from Screens.SiriPopupScreen import SiriPopupScreen  # [Siri]

from wake_word_listener import listen_for_wake_word
from PicoVoice import PicoVoiceEagle, DEV_MODE


class SignalBridge(QObject):
    wake_word_triggered = pyqtSignal()

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

        self.signal_bridge = SignalBridge()
        self.signal_bridge.wake_word_triggered.connect(self.simulate_assistant_trigger)

    def simulate_assistant_trigger(self):
        try:
            # 0. Ensure chat screen is visible before anything else
            self.stack.setCurrentWidget(self.chat_screen)

            # 1. Capture voice input
            transcript = next(self.voice_assistant.speech_to_text())

            # 2. Build a prompt that includes full chat history
            history = self.chat_screen.conversation_history  # [ChatGPT]
            context_prompt = f"{history}User: {transcript}\nAssistant:"  # [ChatGPT]

            # 3. Send it to the local LLaMA model
            response = self.voice_assistant.llama_query(context_prompt)  # For [ChatGPT], change to context_prompt. For [Siri], change to transcript

            # 4. Display on the chat screen
            self.chat_screen.add_message(transcript, response)  # [ChatGPT]

            # 5. LLM speaks the reply
            self.voice_assistant.speak(response)

            # === Siri-style ===
            # self.stack.setCurrentWidget(self.siri_popup)  # [Siri]
            # self.siri_popup.show_query(transcript)        # [Siri]
            # self.siri_popup.show_response(response)       # [Siri]

        except Exception as e:
            print(f"❌ Error during assistant trigger: {e}")

    def start_wake_word_loop(self):
        while True:
            listen_for_wake_word()
            self.signal_bridge.wake_word_triggered.emit()
            time.sleep(3)  # ⏳ Wait 3 seconds before listening again

    def run(self):
        if DEV_MODE:
            self.stack.setCurrentWidget(self.weather_screen)
        else:
            self.stack.setCurrentWidget(self.enrollment_screen)

        self.stack.show()
        threading.Thread(target=self.start_wake_word_loop, daemon=True).start()  # 👂 Run in background
        self.app.exec()


if __name__ == "__main__":
    app_instance = App()
    app_instance.run()
