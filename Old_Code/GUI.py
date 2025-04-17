import customtkinter as ctk
import requests
import time
import tkinter as tk
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from PicoVoice import PicoVoiceEagle

# OpenWeatherMap API Key (Replace with your actual API key)
API_KEY = "7489dd63b5474b9e944194316251303"
CITY = "San Antonio"
URL = f"http://api.weatherapi.com/v1/current.json?key={API_KEY}&q={CITY}"

# Set appearance for customtkinter
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class SmartDisplay(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="#87CEFA")  # Light blue background
        self.configure(width=400, height=400)

        # Define fonts
        large_font = ("Arial", 48, "bold")
        medium_font = ("Arial", 24)
        small_font = ("Arial", 16)

        # Temperature Display
        self.temp_label = ctk.CTkLabel(self, text="Fetching weather...", font=medium_font, text_color="black", fg_color="#87CEFA")
        self.temp_label.place(x=50, y=50)

        # Weather Icon Placeholder
        self.canvas = tk.Canvas(self, width=50, height=50, bg="#87CEFA", highlightthickness=0)
        self.canvas.place(x=130, y=50)
        self.weather_icon = self.canvas.create_oval(5, 5, 45, 45, fill="yellow", outline="black")

        # Time Display
        self.time_label = ctk.CTkLabel(self, text="12:00 AM", font=large_font, text_color="black", fg_color="#87CEFA")
        self.time_label.place(x=300, y=50)

        # Date Display
        self.date_label = ctk.CTkLabel(self, text="Fri 2/7", font=medium_font, text_color="black", fg_color="#87CEFA")
        self.date_label.place(x=300, y=120)

        # Breaking News Section (Placeholder)
        self.news_label = ctk.CTkLabel(self, text="Breaking: ........................................", font=small_font,
                                       text_color="black", fg_color="#87CEFA")
        self.news_label.place(x=50, y=250)

        # Start updates
        self.update_time()
        self.update_weather()

    def update_time(self):
        current_time = time.strftime("%I:%M %p")
        current_date = time.strftime("%a %m/%d")
        self.time_label.configure(text=current_time)
        self.date_label.configure(text=current_date)
        self.after(1000, self.update_time)  # Update every second

    def update_weather(self):
        try:
            response = requests.get(URL)
            data = response.json()

            if response.status_code == 200:
                temp = data["current"]["temp_f"]  # Use temp_c for Celsius
                condition = data["current"]["condition"]["text"]
                self.temp_label.configure(text=f"{temp}°F\n{condition}")
            else:
                self.temp_label.configure(text="Weather unavailable")
        except Exception as e:
            self.temp_label.configure(text="Network error")

        self.after(600000, self.update_weather)  # Refresh every 10 minutes

class VoiceAssistant(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.enroll_label = None
        self.eagle = PicoVoiceEagle()
        # Create two subframes: one for enrollment and one for the main interface
        self.enroll_frame = ctk.CTkFrame(self)
        self.main_frame = ctk.CTkFrame(self)

        self.enroll_frame.pack(fill="both", expand=True)
        self.show_enroll_screen()

    def show_enroll_screen(self):
        # Clear any existing widgets in enroll_frame
        for widget in self.enroll_frame.winfo_children():
            widget.destroy()
        self.enroll_label = ctk.CTkLabel(self.enroll_frame, text="Enrolling")
        self.enroll_label.pack(pady=20)

        # After a short delay, run enrollment and switch screens
        self.after(500, self.complete_enrollment)

    def complete_enrollment(self):
        self.eagle.enroll()
        self.show_main_screen()

    def show_main_screen(self):
        self.enroll_frame.pack_forget()
        self.main_frame.pack(fill="both", expand=True)

        label = ctk.CTkLabel(self.main_frame, text="Ready for command")
        label.pack(pady=20)

        listen_btn = ctk.CTkButton(self.main_frame, text="Listening", command=self.eagle.listening)
        listen_btn.pack(pady=20)

if __name__ == "__main__":
    app = ctk.CTk()
    app.geometry("500x500")  # Set window size

    smart_display = SmartDisplay(app)
    smart_display.pack(fill="both", expand=True)

    voice_assistant = VoiceAssistant(app)
    voice_assistant.pack(fill="both", expand=True)

    app.mainloop()