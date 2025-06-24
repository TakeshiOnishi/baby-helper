# baby-helper

Raspberry Pi ベースの見守りカメラシステムです。  
赤ちゃんの見守りに特化し、以下の機能を提供します

- リアルタイム映像配信（MJPEG）
- 温湿度の取得と表示（SwitchBot連携）
- 顔検出表示
- Bluetoothシャッター連携によるミルク時間記録
- 10秒ごとの高画質キャプチャ保存

---

## 🛠️ セットアップ手順

### 0. Raspberry環境

- OS `Raspberry Pi OS （Debian bookworm 12）`
- ユーザー名は`baby`

### 1. 依存パッケージのインストール

```bash
sudo apt update
sudo apt install python3-pip python3-venv python3-evdev authbind
```

### 2. 仮想環境とパッケージセットアップ

```bash
python3 -m venv my_venv
source my_venv/bin/activate
export PYTHONPATH=$PYTHONPATH:/usr/lib/python3/dist-packages
pip install flask requests opencv-python numpy python-dotenv evdev picamera2
```

### 3. Bluetoothシャッター（CW268）の登録

<details><summary>▶ 手順を開く</summary>

```bash
bluetoothctl
power on
scan on
# 該当のデバイス名を見つけたらアドレスを指定 (e.g. "CW Shutter XX:XX:XX:XX:XX")
pair XX:XX:XX:XX:XX:XX
trust XX:XX:XX:XX:XX:XX
connect XX:XX:XX:XX:XX:XX
```

ルール設定：

```bash
sudo vi /etc/udev/rules.d/99-cw268.rules

# 登録内容
# KERNEL=="event*", SUBSYSTEM=="input", ATTRS{name}=="CW Shutter", SYMLINK+="input/cw268_milk"
```

```bash
sudo udevadm control --reload-rules
sudo udevadm trigger
sudo usermod -aG input baby
```

</details>

---

## ⚙️ サービス設定

```bash
sudo cp systemd/*.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable baby_camera.service
sudo systemctl enable cw268_milk_watcher.service
sudo systemctl start baby_camera.service
sudo systemctl start cw268_milk_watcher.service
```

---

## 🌡 SwitchBot 環境変数の設定

```bash
cp scripts/switchbot.env.example scripts/switchbot.env
# エディタで編集して実際のトークンとデバイスIDを設定
```

---

## 📦 デプロイと更新

### デプロイ

```bash
./bin/deploy.sh
```

### 更新時の再起動

```bash
sudo systemctl restart baby_camera.service
sudo systemctl restart cw268_milk_watcher.service
```

### ログ確認

```bash
journalctl -u baby_camera.service -f
journalctl -u cw268_milk_watcher.service -f
```

---

## 🕒 SwitchBot メトリクス収集（cron）

```bash
crontab -e
# 以下を追加（5分毎に実行）
*/5 * * * * /home/baby/my_venv/bin/python3 /home/baby/scripts/switchbot_get_metrics.py
```

---

## 🌐 アクセス方法

ブラウザで以下のURLへアクセス：

```
http://[Raspberry PiのIP]
```
---

## 📋 必要環境

- Raspberry Pi（Camera Module対応）
- Python 3.8+
- SwitchBot 温湿度計
- CW268 Bluetoothシャッター
