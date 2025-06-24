import os
import time
import threading
import cv2
from datetime import datetime
import argparse

from camera.camera_manager import CameraManager
from camera.face_detector import FaceDetector
from utils.temperature import TemperatureManager
from utils.milk_time import MilkTimeManager
from web.server import WebServer

def parse_args():
    parser = argparse.ArgumentParser(description='ベビィカメラ')
    parser.add_argument('--save-dir', type=str, default='images',
                        help='画像の保存先ディレクトリ（デフォルト: images）')
    parser.add_argument('--width', type=int, default=972, help='キャプチャ画像の幅（デフォルト: 972）')
    parser.add_argument('--height', type=int, default=1296, help='キャプチャ画像の高さ（デフォルト: 1296）')
    return parser.parse_args()

def draw_labels(frame, timestamp, temp_hum, face_status, milk_time):
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 1.2
    thickness = 2
    pad = 10

    # 時刻と温湿度の表示
    label = f'{timestamp}  /  T: {temp_hum[0]}C  H: {temp_hum[1]}%'
    (text_w, text_h), _ = cv2.getTextSize(label, font, font_scale, thickness)
    cv2.rectangle(frame, (0, 0), (text_w + 2*pad, text_h + 2*pad), (50, 50, 50), -1)
    cv2.putText(frame, label, (pad, text_h + pad), font, font_scale, (255,255,255), thickness, cv2.LINE_AA)

    # 顔検出状態の表示
    status_y = text_h + 2*pad + 50
    (status_w, status_h), _ = cv2.getTextSize(face_status, font, font_scale, thickness)
    cv2.rectangle(frame, (0, status_y - status_h - pad), 
                 (status_w + 2*pad, status_y), (50, 50, 50), -1)
    cv2.putText(frame, face_status, (pad, status_y - pad), 
               font, font_scale, (255,255,255), thickness, cv2.LINE_AA)

    # ミルク時間の表示
    milk_y = status_y + 50
    (milk_w, milk_h), _ = cv2.getTextSize(milk_time, font, font_scale, thickness)
    cv2.rectangle(frame, (0, milk_y - milk_h - pad), 
                 (milk_w + 2*pad, milk_y), (50, 50, 50), -1)
    cv2.putText(frame, milk_time, (pad, milk_y - pad), 
               font, font_scale, (255,255,255), thickness, cv2.LINE_AA)

    return frame

def main():
    args = parse_args()
    os.makedirs(args.save_dir, exist_ok=True)

    # 各コンポーネントの初期化
    camera_manager = CameraManager(args.width, args.height)
    face_detector = FaceDetector()
    temp_manager = TemperatureManager()
    milk_manager = MilkTimeManager()
    web_server = WebServer(camera_manager, face_detector, temp_manager, milk_manager)

    def camera_thread():
        while True:
            frame = camera_manager.capture_frame()
            
            # ラベルの描画
            frame = draw_labels(
                frame,
                datetime.now().strftime('%Y.%m.%d  %H:%M:%S'),
                temp_manager.get_temp_hum(),
                f"[NO FACE] ({face_detector.no_face_count} attempts)" if face_detector.detection_result is None else "FaceDetected",
                milk_manager.format_time_ago(milk_manager.get_milk_time())
            )

            # 顔検出結果の描画
            if face_detector.detection_result is not None:
                frame = face_detector.draw_face_box(frame, face_detector.detection_result)

            camera_manager.update_frame(frame)
            time.sleep(0.1)

    def save_thread():
        last_saved = time.time()
        noface_saved = False
    
        while True:
            frame = camera_manager.get_frame()
            if frame is not None:
                detection_result, debug_image = face_detector.detect(frame)
                face_detector.detection_result = detection_result
                face_detector.detection_time = datetime.now()
    
                if detection_result is None:
                    face_detector.no_face_count += 1
                else:
                    face_detector.no_face_count = 0
                    noface_saved = False  # 成功したらリセット

                # 顔検出失敗が15回以上連続した場合、スナップショットを保存
                if face_detector.no_face_count >= 15 and not noface_saved:
                    os.makedirs('/tmp/noface', exist_ok=True)
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    noface_path = os.path.join('/tmp/noface', f"noface_{timestamp}.jpg")
                    cv2.imwrite(noface_path, frame)
                    noface_saved = True
    
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
