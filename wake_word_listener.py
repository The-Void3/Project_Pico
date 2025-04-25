import os
import struct
import pvporcupine
import pyaudio
from dotenv import load_dotenv

load_dotenv()
ACCESS_KEY = os.getenv("ACCESS_KEY")


def listen_for_wake_word():
    porcupine = pvporcupine.create(access_key=ACCESS_KEY, keywords=["jarvis"])

    pa = pyaudio.PyAudio()
    stream = pa.open(
        rate=porcupine.sample_rate,
        channels=1,
        format=pyaudio.paInt16,
        input=True,
        frames_per_buffer=porcupine.frame_length,
    )

    print("🎧 Listening for wake word...")

    try:
        while True:
            audio = stream.read(porcupine.frame_length, exception_on_overflow=False)
            pcm = struct.unpack_from("h" * porcupine.frame_length, audio)

            result = porcupine.process(pcm)
            if result >= 0:
                print("🟢 Wake word detected!")
                break
    finally:
        stream.stop_stream()
        stream.close()
        pa.terminate()
        porcupine.delete()
