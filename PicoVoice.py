import ast
import re
import pveagle
import os
import time
import numpy as np
import requests
import pyttsx3
from dotenv import load_dotenv
from pvrecorder import PvRecorder
from typing import Generator
from vosk import Model, KaldiRecognizer
from govee_control import turn_on, turn_off, set_color

load_dotenv()

DEV_MODE = True  # Set to False for real usage


class PicoVoiceEagle:
    def __init__(self, load_profile=True):
        self.DEFAULT_DEVICE_INDEX = -1
        self.access_key = os.getenv("ACCESS_KEY")
        self.eagle_profiler = pveagle.create_profiler(access_key=self.access_key)
        self.speaker_profile = None
        self.tts_engine = pyttsx3.init()  # 🗣️ Initialize TTS engine
        self.tts_engine.setProperty('rate', 175)

        if DEV_MODE and load_profile:
            print("🧪 DEV_MODE: Loading pre-saved profile...")
            try:
                with open("speaker_profile.eagle", "rb") as f:
                    speaker_profile_bytes = f.read()
                self.speaker_profile = pveagle.EagleProfile.from_bytes(speaker_profile_bytes)
            except FileNotFoundError:
                print("❌ No speaker_profile.eagle file found — skipping load.")

    def speak(self, text: str):
        text = re.sub(r"^\s*[\*\-]\s+", "- ", text, flags=re.MULTILINE)
        text = re.sub(r"[*_~`#]", "", text)
        self.tts_engine.say(text)
        self.tts_engine.runAndWait()

    def speech_to_text(self, prints: bool = True, model_path: str = r"vosk-model-small-en-us-0.15") -> Generator[str, None, None]:
        start_time = time.time()
        device_index = -1
        model = Model(model_path)
        recognizer = KaldiRecognizer(model, 16000)
        print("Model Initialized")

        recorder = PvRecorder(frame_length=512, device_index=device_index)

        try:
            recorder.start()
            print("Recording... Press Ctrl+C to stop.")

            while time.time() - start_time < 5:
                frame = recorder.read()
                audio_data = np.int16(frame).tobytes()
                if recognizer.AcceptWaveform(audio_data):
                    result = recognizer.Result()
                    text = ast.literal_eval(result).get('text', '')
                    if text and prints:
                        print(f"Recognized: {text}")
                    yield text
        except KeyboardInterrupt:
            print("\nStopping...")
        finally:
            recorder.stop()
            recorder.delete()

    def enroll(self):
        print("🚨 enroll() was called!")

        recorder = PvRecorder(
            device_index=self.DEFAULT_DEVICE_INDEX,
            frame_length=self.eagle_profiler.min_enroll_samples
        )
        recorder.start()

        enroll_percentage = 0
        while enroll_percentage < 100.0:
            audio_frame = recorder.read()
            enroll_percentage, feedback = self.eagle_profiler.enroll(audio_frame)
            print(f"Enrollment: {enroll_percentage:.2f} - {feedback}")

        recorder.stop()
        self.speaker_profile = self.eagle_profiler.export()

        with open("speaker_profile.eagle", "wb") as f:
            f.write(self.speaker_profile.to_bytes())

        recorder.delete()

    def listening(self):
        if not self.speaker_profile:
            print("🔁 Speaker profile not loaded. Aborting listening.")
            return

        eagle = pveagle.create_recognizer(
            access_key=self.access_key,
            speaker_profiles=[self.speaker_profile]
        )

        recorder = PvRecorder(
            device_index=self.DEFAULT_DEVICE_INDEX,
            frame_length=eagle.frame_length
        )

        recorder.start()

        try:
            while True:
                audio_frame = recorder.read()
                scores = eagle.process(audio_frame)
                if scores[0] > 0.85:
                    print("Speaker verified. Listening for commands...")
                    for text in self.speech_to_text():
                        if text:
                            print(f"Recognized: {text}")
                            self.handle_command(text)
        except KeyboardInterrupt:
            print("Voice command listening stopped.")

        recorder.stop()
        recorder.delete()
        eagle.delete()

    def handle_command(self, command: str) -> tuple[bool, str]:
        command = command.lower()

        if "turn on the light" in command:
            print("🟡 Turning on the light...")
            turn_on()
            return True, "The light is now on."

        elif "turn off the light" in command:
            print("⚫ Turning off the light...")
            turn_off()
            return True, "The light is now off."

        elif "make the light red" in command:
            print("🔴 Setting light to red...")
            set_color(255, 0, 0)
            return True, "Light set to red."

        elif "make the light blue" in command:
            print("🔵 Setting light to blue...")
            set_color(0, 0, 255)
            return True, "Light set to blue."

        elif "make the light green" in command:
            print("🟢 Setting light to green...")
            set_color(0, 255, 0)
            return True, "Light set to green."

        else:
            print("🤖 Not a Smart Command, Sent to LLM.")
            return False, ""

    def llama_query(self, prompt: str) -> str:
        try:
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "gemma2:2b",
                    "prompt": prompt,
                    "stream": False
                },
                timeout=30
            )
            data = response.json()
            reply = data.get("response", "⚠️ No response from model.")
            return reply
        except requests.exceptions.Timeout:
            return "⏳ The model took too long to respond."
        except Exception as e:
            return f"❌ API call failed: {e}"
