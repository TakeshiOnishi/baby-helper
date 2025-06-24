# ベビィカメラ

Raspberry Piを使用したベビーモニタリングシステム

## ディレクトリ構成

```
.
├── bin/                       # ユーティリティスクリプト
│   └── gen_timelapse_archive.sh  # 撮影画像の圧縮アーカイブ生成
├── scripts/                    # 実行スクリプト
│   ├── switchbot_get_metrics.py
│   └── switchbot.env          # 環境変数設定（Git管理外）
├── src/                       # メインアプリケーション
│   ├── main.py
│   └── ...
├── systemd/                   # systemdサービス設定
│   ├── baby_camera.service
│   └── cw268_milk_watcher.service
└── README.md
```

## 初期セットアップ

1. Python環境のセットアップ
```bash
# 必要なパッケージのインストール
sudo apt update
sudo apt install python3-pip python3-venv python3-evdev

# venvの作成と有効化
python3 -m venv my_venv
source my_venv/bin/activate

# picamera2のインストール
export PYTHONPATH=$PYTHONPATH:/usr/lib/python3/dist-packages
pip3 install picamera2 --upgrade

# 必要なPythonパッケージのインストール
pip install flask
pip install requests
pip install opencv-python
pip install numpy
pip install python-dotenv
pip install evdev
```

2. Bluetoothデバイス（CW268）の設定
```bash
bluetoothctl
power on
scan on
# 該当のデバイス名を見つけたら (e.g. "CW Shutter")
pair XX:XX:XX:XX:XX:XX
trust XX:XX:XX:XX:XX:XX
connect XX:XX:XX:XX:XX:XX

sudo vi /etc/udev/rules.d/99-cw268.rules
# KERNEL=="event*", SUBSYSTEM=="input", ATTRS{name}=="CW Shutter", SYMLINK+="input/cw268_milk"
sudo udevadm control --reload-rules
sudo udevadm trigger

# ユーザーをinputグループに追加
sudo usermod -aG input baby
```

3. 環境変数の設定
```bash
# switchbot.envの作成
cp scripts/switchbot.env.example scripts/switchbot.env
# switchbot.envを編集して実際のトークンとデバイスIDを設定
```

4. サービスの設定
```bash
# サービスファイルのコピー
sudo cp systemd/*.service /etc/systemd/system/

# サービスの有効化と起動
sudo systemctl daemon-reload
sudo systemctl enable baby_camera.service
sudo systemctl enable cw268_milk_watcher.service
sudo systemctl start baby_camera.service
sudo systemctl start cw268_milk_watcher.service
```

---

### ポート80でWebサーバを起動する場合のauthbind設定

本システムのWebサーバ（`src/web/server.py`）はデフォルトでポート80で起動します。通常、ポート80はroot権限が必要ですが、`authbind`を利用することで一般ユーザー（例: `baby`）でも安全にポート80を利用できます。

1. authbindのインストール
   ```bash
   sudo apt install authbind
   ```
2. ポート80の利用許可設定
   ```bash
   sudo touch /etc/authbind/byport/80
   sudo chown baby /etc/authbind/byport/80
   sudo chmod 755 /etc/authbind/byport/80
   ```

5. SwitchBotメトリクス収集の設定
```bash
# cronの設定
crontab -e

# 以下の行を追加（5分毎に実行）
*/5 * * * * /home/baby/my_venv/bin/python3 /home/baby/scripts/switchbot_get_metrics.py
```

## デプロイと更新

1. コードのデプロイ
```bash
rsync -av ./ baby:/home/baby/  --exclude='.git'
```

2. 更新後の再起動
```bash
# サービスを再起動
sudo systemctl restart baby_camera.service
sudo systemctl restart cw268_milk_watcher.service

# ログの確認
sudo journalctl -u baby_camera.service -f
sudo journalctl -u cw268_milk_watcher.service -f
```

## 必要条件

- Python 3.8以上
- Raspberry Pi（カメラモジュール対応）
- SwitchBot（温湿度センサー用）
- CW268 Bluetoothシャッター

## 機能

- リアルタイムビデオストリーミング
- 顔検出
- 温湿度表示（SwitchBot）
- ミルク時間の表示（CW268 Bluetoothシャッター）
- 定期的な画像保存

## アクセス方法

起動後、ブラウザで以下のURLにアクセス：
```
http://[Raspberry PiのIPアドレス]
```

## MJPEG配信の画質・fps切り替え

- デフォルト（軽量モード）: `/video_feed` で画質50・2fpsで配信
- 高画質モード: `/video_feed?quality=best` で画質95・10fpsで配信

※ どちらも保存画像（save_thread）は最高画質のままです。
