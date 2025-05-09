from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QScrollArea, QFrame
from PyQt6.QtCore import Qt, pyqtSignal, QDateTime, QTimer
from PyQt6.QtGui import QFont


class ChatGPTScreen(QWidget):
    voice_request_signal = pyqtSignal()

    def __init__(self, stack, weather_screen):
        super().__init__()
        self.stack = stack
        self.weather_screen = weather_screen
        self.conversation_history = ""
        self.last_cleared = QDateTime.currentDateTime()

        self.setStyleSheet("background-color: #111; color: white;")

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.chat_area = QScrollArea()
        self.chat_area.setWidgetResizable(True)
        self.chat_area.setStyleSheet("""
        QScrollArea {
        background-color: transparent;
        }
        QWidget {
        background-color: transparent;
        }
        """)

        self.chat_widget = QWidget()
        self.chat_layout = QVBoxLayout()
        self.chat_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.chat_widget.setLayout(self.chat_layout)

        self.chat_area.setWidget(self.chat_widget)

        button_bar = QHBoxLayout()

        back_btn = QPushButton("← Back")
        back_btn.setFixedWidth(100)
        back_btn.clicked.connect(self.back_to_main)
        back_btn.setStyleSheet("""
        padding: 8px;
        font-weight: bold;
        background-color: #333;
        color: white;
        border-radius: 6px;
        """)

        clear_btn = QPushButton("🗑️ Clear Chat")
        clear_btn.setFixedWidth(120)
        clear_btn.clicked.connect(self.clear_chat)
        clear_btn.setStyleSheet("""
        padding: 8px;
        font-weight: bold;
        background-color: #333;
        color: white;
        border-radius: 6px;
        """)

        top_btn = QPushButton("⬆️ Top")
        top_btn.setFixedWidth(100)
        top_btn.clicked.connect(self.scroll_to_top)
        top_btn.setStyleSheet("""
        padding: 8px;
        font-weight: bold;
        background-color: #333;
        color: white;
        border-radius: 6px;
        """)

        button_bar.addWidget(back_btn)
        button_bar.addStretch()
        button_bar.addWidget(top_btn)
        button_bar.addWidget(clear_btn)

        layout.addLayout(button_bar)
        layout.addWidget(self.chat_area)

        self.ask_btn = QPushButton("🎤 Ask Another Question")
        self.ask_btn.setFixedHeight(40)
        self.ask_btn.setStyleSheet("padding: 8px; font-size: 16px; font-weight: bold; background-color: #4a90e2; color: white; border-radius: 8px;")
        self.ask_btn.clicked.connect(self.request_next_input)
        layout.addWidget(self.ask_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        self.setLayout(layout)

    def add_message(self, user_text: str, assistant_text: str):
        if self.last_cleared.secsTo(QDateTime.currentDateTime()) > 86400:
            self.clear_chat()

        user_msg = QLabel(user_text)
        user_msg.setWordWrap(True)
        user_msg.setFont(QFont("Arial", 14))
        user_msg.setStyleSheet("color: white; background-color: #4a90e2; padding: 10px; border-radius: 10px;")
        user_msg.setAlignment(Qt.AlignmentFlag.AlignRight)
        user_container = QHBoxLayout()
        user_container.addStretch()
        user_container.addWidget(user_msg)

        assistant_msg = QLabel(assistant_text)
        assistant_msg.setWordWrap(True)
        assistant_msg.setFont(QFont("Arial", 14))
        assistant_msg.setStyleSheet("color: white; background-color: #444; padding: 10px; border-radius: 10px;")
        assistant_msg.setAlignment(Qt.AlignmentFlag.AlignLeft)
        assistant_container = QHBoxLayout()
        assistant_container.addWidget(assistant_msg)
        assistant_container.addStretch()

        self.chat_layout.addLayout(user_container)
        self.chat_layout.addSpacing(5)
        self.chat_layout.addLayout(assistant_container)
        self.chat_layout.addSpacing(15)
        user_container.setContentsMargins(10, 0, 10, 0)
        assistant_container.setContentsMargins(10, 0, 10, 0)

        self.conversation_history += f"User: {user_text}\nAssistant: {assistant_text}\n"

        QTimer.singleShot(100, lambda: self.chat_area.verticalScrollBar().setValue(self.chat_area.verticalScrollBar().maximum()))
        QTimer.singleShot(0, self.repaint)

    def scroll_to_top(self):
        self.chat_area.verticalScrollBar().setValue(0)

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
        self.conversation_history = ""
        self.last_cleared = QDateTime.currentDateTime()

    def request_next_input(self):
        self.voice_request_signal.emit()
