from evdev import InputDevice, categorize, ecodes
import time
import os
from datetime import datetime

DEVICE_PATH = "/dev/input/cw268_milk"

while True:
    if not os.path.exists(DEVICE_PATH):
        time.sleep(1)
        continue

    try:
        dev = InputDevice(DEVICE_PATH)
        print(f"[INFO] デバイス接続: {DEVICE_PATH}")
        for event in dev.read_loop():
            if event.type == ecodes.EV_KEY:
                key_event = categorize(event)
                if key_event.keystate == key_event.key_down:
                    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    with open("/tmp/milk_time.txt", "w") as f:
                        f.write(now + "\n")
                    print(f"[MILK] ボタン押下: {now}")
    except Exception as e:
        print(f"[WARN] デバイス切断またはエラー: {e}")
        time.sleep(1)
