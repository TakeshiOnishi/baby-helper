# baby-helper

> ⚠️ **注意: このアプリはあくまで便利ツールです。**
> **運用場所や用途によっては、必ず冗長化やバックアップ等の安全対策を講じてください。**

Raspberry Pi ベースの見守りカメラシステムです。  
赤ちゃんの見守りに特化し、以下の機能を提供します

- リアルタイム映像配信（MJPEG）
- 温湿度の取得と表示（SwitchBot連携）
- 10秒ごとの高画質キャプチャ保存

---

## 🛠️ セットアップ手順

### 0. 動作環境など

- Raspberry Pi4
  - OS `Raspberry Pi OS （Debian bookworm 12）`
  - ユーザー名は`baby`
  - OV5647 カメラモジュール
  - Python 3.11
- SwitchBot 温湿度計

### 1. 依存パッケージのインストール

```bash
sudo apt update
sudo apt install python3-pip python3-venv authbind
```

### 2. 仮想環境とパッケージセットアップ

```bash
python3 -m venv my_venv
source my_venv/bin/activate
export PYTHONPATH=$PYTHONPATH:/usr/lib/python3/dist-packages
pip install flask requests opencv-python numpy python-dotenv picamera2
```

### 3. SwitchBot 温湿度計設定

```bash
cp scripts/switchbot.env.example scripts/switchbot.env
# エディタで編集して実際のトークンとデバイスIDを設定
```

### 4. デプロイ

```bash
./bin/deploy.sh
```

#### ⚙️ サービス有効化

```bash
sudo cp systemd/*.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable baby_camera.service
sudo systemctl start baby_camera.service
```

#### 🕒 SwitchBot 温湿度情報収集（cron）

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

## 📁 ディレクトリ・ファイル構成

```
baby-helper
├── bin/                # デプロイやタイムラプス生成用スクリプト
│   ├── deploy.sh
│   └── gen_timelapse_archive.sh
├── newrelic_flex_send_cpu_info.yml  # NewRelic用設定
├── README.md           # このドキュメント
├── scripts/            # 補助スクリプト・環境変数ファイル
│   ├── switchbot_get_metrics.py     # SwitchBotデータ取得
│   └── switchbot.env.sample         # SwitchBot用サンプルenv
├── src/                # アプリ本体
│   ├── camera/         # カメラ制御
│   │   └── camera_manager.py
│   ├── main.py         # メインエントリ
│   ├── utils/          # ユーティリティ
│   │   └── temperature.py
│   └── web/            # Webサーバ
│       └── server.py
├── systemd/            # systemdサービス定義
│   └── baby_camera.service
```

## Option: CPU温度をNewRelicでモニタリング

- 前提: NewRelic Infrastructure Agentを[インストール済み](https://docs.newrelic.com/jp/docs/infrastructure/infrastructure-agent/linux-installation/package-manager-install/)

```
cp ./newrelic_flex_send_cpu_info.yml /etc/newrelic-infra/integrations.d/cpu_temp.yml
sudo systemctl restart newrelic-infra.service
```

```
# NRQL
SELECT max(cpu_measure_temp) from TemperatureSample facet entityName TIMESERIES AUTO
```
