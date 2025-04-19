from pvrecorder import PvRecorder
import numpy as np
import time

recorder = PvRecorder(device_index=0, frame_length=512)

try:
    recorder.start()
    print("🎤 Mic started. Speak now...")

    start = time.time()
    while time.time() - start < 5:
        frame = recorder.read()
        amplitude = np.abs(np.array(frame)).mean() / 32768
        print(f"Amplitude: {amplitude:.4f}")
        time.sleep(0.03)

    recorder.stop()
    recorder.delete()
    print("✅ Mic stopped safely.")

except Exception as e:
    print(f"❌ Crash occurred: {e}")
