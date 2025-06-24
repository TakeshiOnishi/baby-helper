from picamera2 import Picamera2
import cv2
import numpy as np
import threading

class CameraManager:
    def __init__(self, width, height):
        self.current_frame = None
        self.frame_lock = threading.Lock()
        
        # カメラの初期化
        tuning = Picamera2.load_tuning_file("ov5647_noir.json")
        self.picam2 = Picamera2(tuning=tuning)
        config = self.picam2.create_preview_configuration(main={"size": (width, height)})
        self.picam2.configure(config)
        self.picam2.start()

    def capture_frame(self):
        frame = self.picam2.capture_array()
        frame = cv2.flip(frame, -1)
        frame = cv2.cvtColor(np.array(frame), cv2.COLOR_RGB2BGR)
        return frame

    def update_frame(self, frame):
        with self.frame_lock:
            self.current_frame = frame.copy()

    def get_frame(self):
        with self.frame_lock:
            return self.current_frame.copy() if self.current_frame is not None else None 
