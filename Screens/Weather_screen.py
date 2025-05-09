import sys
import requests
from datetime import datetime
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt, QTimer

# Weather API config
API_KEY = "7489dd63b5474b9e944194316251303"
CITY = "Mcallen"
URL = f"https://api.weatherapi.com/v1/current.json?key={API_KEY}&q={CITY}"


class WeatherScreen(QWidget):
    def __init__(self):
        super().__init__()

        self.setStyleSheet("""
            background-image: url(/home/PicoVoice/Project_Pico/Screens/aurora.jp);
            background-repeat: no-repeat;
            background-position: center;
            background-size: cover;
            border: none;
        """)
        self.setContentsMargins(0, 0, 0, 0)

        # Transparent container
        container = QWidget()
        container_layout = QVBoxLayout()
        container_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        container.setLayout(container_layout)
        container.setStyleSheet("background-color: black;")

        # Time
        self.time_label = QLabel()
        self._style_label(self.time_label, 60)

        # Date
        self.date_label = QLabel()
        self._style_label(self.date_label, 28)

        # City
        self.city_label = QLabel()
        self._style_label(self.city_label, 18)

        # Weather Condition
        self.condition_label = QLabel()
        self._style_label(self.condition_label, 18)

        # Temperature
        self.temp_label = QLabel()
        self._style_label(self.temp_label, 24)

        # Add widgets in order
        for label in [
            self.time_label,
            self.date_label,
            self.city_label,
            self.condition_label,
            self.temp_label
        ]:
            container_layout.addWidget(label)

        # Layout to window
        main_layout = QVBoxLayout()
        main_layout.addWidget(container)
        self.setLayout(main_layout)

        # Start updates
        self.update_time()
        self.update_weather()

    def _style_label(self, label, size):
        label.setFont(QFont("Georgia", size, QFont.Weight.Bold))
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("color: white;")
        label.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

    def update_time(self):
        now = datetime.now()
        self.time_label.setText(now.strftime("%I:%M %p").lstrip("0"))
        self.date_label.setText(now.strftime("%B %d, %Y"))
        QTimer.singleShot(10000, self.update_time)

    def update_weather(self):
        try:
            response = requests.get(URL)
            if response.status_code == 200:
                data = response.json()
                city = data["location"]["name"]
                region = data["location"]["region"]
                self.city_label.setText(f"{city}, {region}")

                condition = data["current"]["condition"]["text"]
                temp = data["current"]["temp_f"]
                self.condition_label.setText(condition)
                self.temp_label.setText(f"{temp}°F")
            else:
                self.city_label.setText("City Unavailable")
                self.condition_label.setText("Weather Unavailable")
                self.temp_label.setText("")
        except:
            self.city_label.setText("City Error")
            self.condition_label.setText("Network Error")
            self.temp_label.setText("")

        QTimer.singleShot(600000, self.update_weather)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    screen = WeatherScreen()
    screen.resize(800, 600)
    screen.show()
    sys.exit(app.exec())
