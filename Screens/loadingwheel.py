import sys
import os
import math
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt6.QtGui import QPainter, QColor, QPen, QFont
from PyQt6.QtWidgets import QWidget, QApplication, QLabel, QVBoxLayout, QStackedWidget
from Screens.Weather_screen import WeatherScreen
from PicoVoice import PicoVoiceEagle, DEV_MODE

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


class LoadingSpinner(QWidget):
    def __init__(self, parent=None, size=1000, line_width=6, speed=10, color="#3498db"):
        super().__init__(parent)
        self.angle = 0
        self.size = size
        self.line_width = line_width
        self.speed = speed
        self.color = QColor(color)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.rotate)
        self.timer.start(self.speed)

        self.setFixedSize(self.size, self.size)

    def rotate(self):
        self.angle = (self.angle + 5) % 360
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        center = self.rect().center()
        radius = self.size // 2 - self.line_width

        pen = QPen(self.color, self.line_width, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)

        for i in range(12):
            alpha = int(255 * (i + 1) / 12)
            pen.setColor(QColor(self.color.red(), self.color.green(), self.color.blue(), alpha))
            painter.setPen(pen)

            angle = self.angle - i * 30
            radian_angle = math.radians(angle)

            x = center.x() + radius * math.cos(radian_angle)
            y = center.y() + radius * math.sin(radian_angle)

            painter.drawPoint(int(x), int(y))

        painter.end()


class EnrollmentThread(QThread):
    finished = pyqtSignal()

    def run(self):
        if DEV_MODE:
            print("🧪 DEV_MODE active: skipping enrollment in background thread.")
        else:
            pico = PicoVoiceEagle()
            pico.enroll()
        self.finished.emit()


class EnrollmentProgress(QWidget):
    def __init__(self, stack, weather_screen, voice_assistant):
        super().__init__()
        self.stack = stack
        self.weather_screen = weather_screen
        self.voice_assistant = voice_assistant
        self.setWindowTitle("Enrollment in Progress")
        self.setGeometry(100, 100, 800, 600)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.spinner = LoadingSpinner(self, size=80, line_width=6, speed=15, color="#3498db")
        self.label = QLabel("Enrollment in Progress", self)
        self.label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(self.spinner, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.label)
        self.setLayout(layout)

        # Start enrollment in a separate thread
        self.enrollment_thread = EnrollmentThread()
        self.enrollment_thread.finished.connect(self.on_enrollment_complete)
        self.enrollment_thread.start()

    def on_enrollment_complete(self):
        self.stack.setCurrentWidget(self.weather_screen)


if __name__ == "__main__":
    from PicoVoice import PicoVoiceEagle

    app = QApplication(sys.argv)
    stack = QStackedWidget()
    stack.resize(1200, 800)

    weather_screen = WeatherScreen()
    voice_assistant = PicoVoiceEagle()
    enrollment_screen = EnrollmentProgress(stack, weather_screen, voice_assistant)

    stack.addWidget(enrollment_screen)
    stack.addWidget(weather_screen)

    stack.setCurrentWidget(enrollment_screen)
    stack.show()
    sys.exit(app.exec())
