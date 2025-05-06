import requests

API_KEY = "58fba9ce-dacf-48ed-b2e7-6902596c919a"
HEADERS = {
    "Govee-API-Key": API_KEY,
    "Content-Type": "application/json"
}
BASE_URL = "https://developer-api.govee.com/v1"
PREFERRED_DEVICE_ID = "D2:05:D0:C9:07:DB:C6:B0"
PREFERRED_MODEL = "H6008"


def control_device(cmd_name, cmd_value):
    payload = {
        "device": PREFERRED_DEVICE_ID,
        "model": PREFERRED_MODEL,
        "cmd": {"name": cmd_name, "value": cmd_value}
    }
    url = f"{BASE_URL}/devices/control"
    resp = requests.put(url, headers=HEADERS, json=payload)
    if resp.status_code != 200:
        print(f"❌ Error {resp.status_code}: {resp.text}")
    else:
        print("✅", resp.json().get("message", "OK"))


def turn_on():
    control_device("turn", "on")


def turn_off():
    control_device("turn", "off")


def set_color(r, g, b):
    control_device("color", {"r": r, "g": g, "b": b})


def set_brightness(level):
    control_device("brightness", level)
