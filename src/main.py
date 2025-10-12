import os
import time
import threading
import cv2
from datetime import datetime
import argparse

from camera.camera_manager import CameraManager
from utils.temperature import TemperatureManager
from web.server import WebServer

def parse_args():
    parser = argparse.ArgumentParser(description='ベビィカメラ')
    parser.add_argument('--save-dir', type=str, default='images',
                        help='画像の保存先ディレクトリ（デフォルト: images）')
    parser.add_argument('--width', type=int, default=972, help='キャプチャ画像の幅（デフォルト: 972）')
    parser.add_argument('--height', type=int, default=1296, help='キャプチャ画像の高さ（デフォルト: 1296）')
    return parser.parse_args()

def draw_labels(frame, timestamp, temp_hum):
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 1.2
    thickness = 2
    pad = 10

    # 時刻と温湿度の表示
    label = f'{timestamp}  /  T: {temp_hum[0]}C  H: {temp_hum[1]}%'
    (text_w, text_h), _ = cv2.getTextSize(label, font, font_scale, thickness)
    cv2.rectangle(frame, (0, 0), (text_w + 2*pad, text_h + 2*pad), (50, 50, 50), -1)
    cv2.putText(frame, label, (pad, text_h + pad), font, font_scale, (255,255,255), thickness, cv2.LINE_AA)



    return frame

def main():
    args = parse_args()
    os.makedirs(args.save_dir, exist_ok=True)

    # 各コンポーネントの初期化
    camera_manager = CameraManager(args.width, args.height)
    temp_manager = TemperatureManager()
    web_server = WebServer(camera_manager, temp_manager)

    def camera_thread():
        while True:
            frame = camera_manager.capture_frame()
            
            # ラベルの描画
            frame = draw_labels(
                frame,
                datetime.now().strftime('%Y.%m.%d  %H:%M:%S'),
                temp_manager.get_temp_hum()
            )

            camera_manager.update_frame(frame)
            time.sleep(0.1)

    def save_thread():
        last_saved = time.time()
    
        while True:
            frame = camera_manager.get_frame()
            if frame is not None:
                now = time.time()
                if now - last_saved >= 10:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    cv2.imwrite(os.path.join(args.save_dir, f"{timestamp}.jpg"), frame)
                    last_saved = now
    
            time.sleep(2)

    # スレッドの開始
    threading.Thread(target=camera_thread, daemon=True).start()
    threading.Thread(target=save_thread, daemon=True).start()

    # Webサーバーの起動
    web_server.run()

if __name__ == '__main__':
    main() 
