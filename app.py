import sys
import threading
import time
from PyQt6.QtWidgets import QApplication, QStackedWidget, QPushButton
from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtGui import QPalette, QColor
from PyQt6.QtCore import Qt
from Screens.loadingwheel import EnrollmentProgress
from Screens.Weather_screen import WeatherScreen
from Screens.ChatGPTScreen import ChatGPTScreen  # [ChatGPT]
from wake_word_listener import listen_for_wake_word
from PicoVoice import PicoVoiceEagle, DEV_MODE


class SignalBridge(QObject):
    wake_word_triggered = pyqtSignal()


class App:
    def __init__(self):
        self.app = QApplication(sys.argv)
        # ✅ Set global dark theme
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(17, 17, 17))  # dark gray background
        palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)  # white text
        palette.setColor(QPalette.ColorRole.Button, QColor(50, 50, 50))  # button background
        palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)  # button text
        palette.setColor(QPalette.ColorRole.Base, QColor(25, 25, 25))  # text field / input background
        palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.white)

        self.app.setPalette(palette)
        self.stack = QStackedWidget()
        self.stack.resize(1200, 800)

        self.voice_assistant = PicoVoiceEagle(load_profile=True)

        self.weather_screen = WeatherScreen()
        self.chat_screen = ChatGPTScreen(self.stack, self.weather_screen)  # [ChatGPT]
        self.chat_screen.voice_request_signal.connect(self.simulate_assistant_trigger)  # [ChatGPT]

        self.enrollment_screen = EnrollmentProgress(
            self.stack,
            self.weather_screen,
            self.voice_assistant
        )

        self.test_button = QPushButton("🎤 Activate Assistant")
        self.test_button.setStyleSheet("background-color: black; color: white;")
        self.test_button.clicked.connect(self.simulate_assistant_trigger)
        self.weather_screen.layout().addWidget(self.test_button)

        self.stack.addWidget(self.enrollment_screen)
        self.stack.addWidget(self.weather_screen)
        self.stack.addWidget(self.chat_screen)  # [ChatGPT]

        self.signal_bridge = SignalBridge()
        self.signal_bridge.wake_word_triggered.connect(self.simulate_assistant_trigger)

    def simulate_assistant_trigger(self):
        try:
            # 0. Ensure chat screen is visible before anything else
            self.stack.setCurrentWidget(self.chat_screen)

            # 1. Capture voice input
            transcript = next(self.voice_assistant.speech_to_text())

            # 2. Try handling as a smart home command first
            handled, smart_reply = self.voice_assistant.handle_command(transcript)
            if handled:
                self.chat_screen.add_message(transcript, smart_reply)
                self.voice_assistant.speak(smart_reply)
                return

            # 3. Build LLM prompt
            history = self.chat_screen.conversation_history  # [ChatGPT]
            context_prompt = f"{history}User: {transcript}\nAssistant:"  # [ChatGPT]

            # 4. Send it to the local LLaMA model
            response = self.voice_assistant.llama_query(context_prompt)

            # 5. Display on the chat screen & LLM speaks the reply
            self.chat_screen.add_message(transcript, response)  # [ChatGPT]
            self.voice_assistant.speak(response)

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

        self.stack.showFullScreen()
        threading.Thread(target=self.start_wake_word_loop, daemon=True).start()  # 👂 Run in background
        self.app.exec()


if __name__ == "__main__":
    app_instance = App()
    app_instance.run()
