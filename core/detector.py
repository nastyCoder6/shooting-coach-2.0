import cv2
import mediapipe as mp
from abc import ABC, abstractmethod
from mediapipe.tasks.python import vision
from mediapipe.tasks import python

class IPoseDetector(ABC):
    """
    Interfejs detektora postaw - definiuje kontrakt dla modułów detekcji.
    """
    @abstractmethod
    def detect_landmarks(self, frame, timestamp_ms: int):
        pass

class MediaPipeDetector(IPoseDetector):
    # Definicja połączeń specyficznych dla analizy koszykarskiej
    BASKETBALL_CONNECTIONS = [
        (12, 14), (14, 16), (16, 20), (16, 22), # Ręka rzucająca (prawa)
        (11, 13), (13, 15), (15, 19),           # Ręka pomocnicza (lewa)
        (11, 12), (23, 24), (11, 23), (12, 24), # Tułów i postawa
        (24, 26), (26, 28), (28, 30), (28, 32), # Noga prawa
        (23, 25), (25, 27), (27, 29), (27, 31)  # Noga lewa
    ]

    def __init__(self, model_path: str = "models/pose_landmarker_heavy.task"):
        """Inicjalizacja silnika detekcji postaw."""
        base_options = python.BaseOptions(model_asset_path=model_path)
        options = vision.PoseLandmarkerOptions(
            base_options=base_options,
            running_mode=vision.RunningMode.VIDEO,
            min_pose_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.detector = vision.PoseLandmarker.create_from_options(options)

    def detect_landmarks(self, frame, timestamp_ms: int):
        """Ekstrakcja punktów postaw z klatki (landmarks)."""
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=rgb_frame
        )
        result = self.detector.detect_for_video(mp_image, timestamp_ms)
        if result.pose_landmarks:
            return result.pose_landmarks[0]
        return None

    def draw_landmarks(self, frame, landmarks):
        """Rysowanie punktów postaw (landmarks) na klatce."""
        if not landmarks:
            return frame
        
        h, w, _ = frame.shape

        for lm in landmarks:
            x_px = int(lm.x * w)
            y_px = int(lm.y * h)
            cv2.circle(frame, (x_px, y_px), 3, (255, 0, 0), -1)
        
        for start_inx, end_idx in self.BASKETBALL_CONNECTIONS:
            start_lm = landmarks[start_inx]
            end_lm = landmarks[end_idx]
            
            pt1 = (int(start_lm.x * w), int(start_lm.y * h))
            pt2 = (int(end_lm.x * w), int(end_lm.y * h))

            cv2.line(frame, pt1, pt2, (255, 255, 200), 2)

        return frame
