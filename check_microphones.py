from pvrecorder import PvRecorder

devices = PvRecorder.get_available_devices()
print("🎙️ Available Microphones:")
for index, name in enumerate(devices):
    print(f"{index}: {name}")
