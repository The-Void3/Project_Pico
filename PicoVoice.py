import ast
import pveagle
import os
import time
import numpy as np
import subprocess
from dotenv import load_dotenv
from pvrecorder import PvRecorder
from typing import Generator
from vosk import Model, KaldiRecognizer

load_dotenv()

DEV_MODE = True  # Set to False for real usage


class PicoVoiceEagle:
    def __init__(self, load_profile=True):  # Allow turning off profile loading
        self.DEFAULT_DEVICE_INDEX = -1
        self.access_key = os.getenv("ACCESS_KEY")
        self.eagle_profiler = pveagle.create_profiler(access_key=self.access_key)
        self.speaker_profile = None

        if DEV_MODE and load_profile:
            print("🧪 DEV_MODE: Loading pre-saved profile...")
            try:
                with open("speaker_profile.eagle", "rb") as f:
                    speaker_profile_bytes = f.read()
                self.speaker_profile = pveagle.EagleProfile.from_bytes(speaker_profile_bytes)
            except FileNotFoundError:
                print("❌ No speaker_profile.eagle file found — skipping load.")

    def speech_to_text(self, prints: bool = True, model_path: str = r"vosk-model-small-en-us-0.15") -> Generator[
        str, None, None]:
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
        print("🚨 enroll() was called!")  # Debug print for tracking

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

    def handle_command(self, command: str):
        command = command.lower()
        if "turn on the light" in command:
            print("🟡 Turning on the light...")
        elif "turn off the light" in command:
            print("⚫ Turning off the light...")
        elif "what time is it" in command:
            from datetime import datetime
            now = datetime.now().strftime("%H:%M")
            print(f"🕒 The current time is {now}")
        else:
            print("🤖 Command not recognized.")

    def llama_query(self, prompt: str) -> str:
        try:
            process = subprocess.Popen(
                ["ollama", "run", "llama3", prompt],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            stdout, stderr = process.communicate(timeout=90)
            return stdout.strip() if stdout else f"❌ LLaMA Error: {stderr.strip()}"
        except subprocess.TimeoutExpired:
            return "Sorry, the model took too long to respond."
        except Exception as e:
            return f"❌ LLaMA query failed: {e}"
