from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPainter, QColor, QBrush
import numpy as np


class VoiceWaveformWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(60)
        self.setMaximumHeight(80)
        self.setStyleSheet("background-color: transparent;")

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(30)  # Refresh rate ~33 FPS

        self.amplitude = 0.0
        self.bars = 20
        self.phase = 0.0

    def update_amplitude(self, value):
        self.amplitude = value

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = self.width()
        h = self.height()
        bar_width = w / self.bars

        color = QColor(52, 152, 219, 180)  # Light blue glow
        painter.setBrush(QBrush(color))
        painter.setPen(Qt.PenStyle.NoPen)

        for i in range(self.bars):
            phase_shift = self.phase + (i / self.bars) * np.pi * 2
            height_factor = (np.sin(phase_shift) + 1) / 2  # Normalize 0-1
            bar_height = h * height_factor * (0.2 + 0.8 * self.amplitude)
            x = i * bar_width
            y = (h - bar_height) / 2
            painter.drawRoundedRect(x, y, bar_width * 0.8, bar_height, 3, 3)

        self.phase += 0.15  # Animate flow
        if self.phase > 2 * np.pi:
            self.phase -= 2 * np.pi
