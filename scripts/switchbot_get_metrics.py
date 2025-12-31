#!/usr/bin/env python3
import os
import json
import requests
from datetime import datetime, timedelta
import time
from pathlib import Path

# 環境変数ファイルのパスを設定（プロジェクトルートの.env）
env_file = Path(__file__).parent.parent / '.env'

# 環境変数ファイルを読み込む
if env_file.exists():
    with open(env_file) as f:
        for line in f:
            if line.strip() and not line.startswith('#') and '=' in line:
                key, value = line.strip().split('=', 1)
                os.environ[key] = value.strip('"')

SWITCHBOT_TOKEN = os.getenv("SWITCHBOT_TOKEN")
SWITCHBOT_DEVICE_ID = os.getenv("SWITCHBOT_DEVICE_ID")
SWITCHBOT_CACHE_FILE = "/tmp/switchbot_cache.json"

if not SWITCHBOT_TOKEN or not SWITCHBOT_DEVICE_ID:
    raise ValueError("環境変数 SWITCHBOT_TOKEN または SWITCHBOT_DEVICE_ID が設定されていません。")

def get_switchbot_data():
    if os.path.exists(SWITCHBOT_CACHE_FILE):
        with open(SWITCHBOT_CACHE_FILE, "r") as f:
            cache = json.load(f)
            ts = datetime.fromisoformat(cache["timestamp"])
            if datetime.now() - ts < timedelta(minutes=5):
                return cache["data"]
    try:
        res = requests.get(
            f"https://api.switch-bot.com/v1.0/devices/{SWITCHBOT_DEVICE_ID}/status",
            headers={"Authorization": SWITCHBOT_TOKEN}
        )
        body = res.json()["body"]
        data = {
            "temperature": body["temperature"],
            "humidity": body["humidity"],
            "battery": body.get("battery"),
            "updated": datetime.now().strftime("%H:%M")
        }
        with open(SWITCHBOT_CACHE_FILE, "w") as f:
            json.dump({"timestamp": datetime.now().isoformat(), "data": data}, f)
        return data
    except Exception as e:
        print(f"SwitchBot API error: {e}")
        return None

data = get_switchbot_data()
