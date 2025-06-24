import cv2
import mediapipe as mp
from datetime import datetime

class FaceDetector:
    def __init__(self):
        self.mp_face_detection = mp.solutions.face_detection
        self.detection_result = None
        self.detection_time = None
        self.no_face_count = 0

    def top_crop(self, image, top_ratio=0.7):
        h, w, _ = image.shape
        ch = int(h * top_ratio)
        return image[:ch, :]

    def detect(self, frame):
        h, w, _ = frame.shape
        rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        last_trial_image_bgr = frame.copy()

        for ratio in [0.7, 0.5]:
            trial_image = self.top_crop(rgb_image, ratio) if ratio < 1.0 else rgb_image
            last_trial_image_bgr = cv2.cvtColor(trial_image, cv2.COLOR_RGB2BGR)
            
            with self.mp_face_detection.FaceDetection(
                model_selection=0,
                min_detection_confidence=0.3
            ) as face_detection:
                results = face_detection.process(trial_image)
                if results.detections:
                    for detection in results.detections:
                        bbox = detection.location_data.relative_bounding_box
                        cropped_h_actual = int(h * ratio)
                        cropped_w_actual = w

                        x1 = int(bbox.xmin * cropped_w_actual)
                        y1 = int(bbox.ymin * cropped_h_actual)
                        x2 = int((bbox.xmin + bbox.width) * cropped_w_actual)
                        y2 = int((bbox.ymin + bbox.height) * cropped_h_actual)

                        y_offset_correction = 10
                        y1 = max(0, y1 - y_offset_correction)
                        y2 = max(0, y2 - y_offset_correction)

                        confidence = detection.score[0]
                        if confidence > 0.3:
                            return (x1, y1, x2, y2, "FACE"), last_trial_image_bgr
        return None, last_trial_image_bgr

    def draw_face_box(self, frame, bbox):
        if bbox is not None:
            x1, y1, x2, y2, _ = bbox
            overlay = frame.copy()
            cv2.rectangle(overlay, (x1, y1), (x2, y2), (150, 255, 150), thickness=1)
            return cv2.addWeighted(overlay, 0.15, frame, 0.85, 0)
        return frame 
