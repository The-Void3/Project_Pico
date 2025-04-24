from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QScrollArea, QFrame
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont


class ChatGPTScreen(QWidget):
    voice_request_signal = pyqtSignal()  # 🚀 Signal to ask for new voice input

    def __init__(self, stack, weather_screen):
        super().__init__()
        self.stack = stack
        self.weather_screen = weather_screen
        self.conversation_history = ""  # 🧠 Stores full chat history

        self.setStyleSheet("background-color: rgba(0, 0, 0, 230);")

        # === Main Layout ===
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # === Scrollable Chat Area ===
        self.chat_area = QScrollArea()
        self.chat_area.setWidgetResizable(True)
        self.chat_area.setStyleSheet("border: none;")

        self.chat_widget = QWidget()
        self.chat_layout = QVBoxLayout()
        self.chat_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.chat_widget.setLayout(self.chat_layout)

        self.chat_area.setWidget(self.chat_widget)

        # === Buttons Bar ===
        button_bar = QHBoxLayout()

        back_btn = QPushButton("← Back")
        back_btn.setFixedWidth(100)
        back_btn.clicked.connect(self.back_to_main)
        back_btn.setStyleSheet("padding: 8px; font-weight: bold;")

        clear_btn = QPushButton("🗑️ Clear Chat")
        clear_btn.setFixedWidth(120)
        clear_btn.clicked.connect(self.clear_chat)
        clear_btn.setStyleSheet("padding: 8px; font-weight: bold;")

        button_bar.addWidget(back_btn)
        button_bar.addStretch()
        button_bar.addWidget(clear_btn)

        layout.addLayout(button_bar)
        layout.addWidget(self.chat_area)

        # === Ask Again Button ===
        self.ask_btn = QPushButton("🎤 Ask Another Question")
        self.ask_btn.setFixedHeight(40)
        self.ask_btn.setStyleSheet("padding: 8px; font-size: 16px; font-weight: bold; background-color: #4a90e2; color: white; border-radius: 8px;")
        self.ask_btn.clicked.connect(self.request_next_input)
        layout.addWidget(self.ask_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        self.setLayout(layout)

    def add_message(self, user_text: str, assistant_text: str):
        # === User Message ===
        user_msg = QLabel(user_text)
        user_msg.setWordWrap(True)
        user_msg.setFont(QFont("Arial", 14))
        user_msg.setStyleSheet("color: white; background-color: #4a90e2; padding: 10px; border-radius: 10px;")
        user_msg.setAlignment(Qt.AlignmentFlag.AlignRight)
        user_container = QHBoxLayout()
        user_container.addStretch()
        user_container.addWidget(user_msg)

        # === Assistant Response ===
        assistant_msg = QLabel(assistant_text)
        assistant_msg.setWordWrap(True)
        assistant_msg.setFont(QFont("Arial", 14))
        assistant_msg.setStyleSheet("color: white; background-color: #444; padding: 10px; border-radius: 10px;")
        assistant_msg.setAlignment(Qt.AlignmentFlag.AlignLeft)
        assistant_container = QHBoxLayout()
        assistant_container.addWidget(assistant_msg)
        assistant_container.addStretch()

        # Add to chat layout
        self.chat_layout.addLayout(user_container)
        self.chat_layout.addSpacing(5)
        self.chat_layout.addLayout(assistant_container)
        self.chat_layout.addSpacing(15)

        # Update chat memory
        self.conversation_history += f"User: {user_text}\nAssistant: {assistant_text}\n"

        # Scroll to bottom
        self.chat_area.verticalScrollBar().setValue(self.chat_area.verticalScrollBar().maximum())

    def back_to_main(self):
        self.stack.setCurrentWidget(self.weather_screen)

    def clear_chat(self):
        def recursive_clear(layout):
            while layout.count():
                item = layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()
                elif item.layout():
                    recursive_clear(item.layout())

        recursive_clear(self.chat_layout)
        self.conversation_history = ""  # 🧽 Reset conversation context

    def request_next_input(self):
        self.voice_request_signal.emit()  # 🔁 Ask App to capture new voice input
