import cv2 as cv
import os

class VideoProvider:
    """
    Klasa pełniąca rolę adaptera dla lib OpenCV.
    Dostarcza klatki video.
    """
    def __init__(self, path: str):
        self.path = path
        self.cap = None
        self.fps = 0.0

    def open(self) -> None:
        """Otwiera strumień wideo i weryfikuje jego integralność"""
        if not os.path.exists(self.path):
            raise FileNotFoundError(f"Błąd: Nie znaleziono pliku pod ścieżką: {self.path}")
        self.cap = cv.VideoCapture(self.path)

        if not self.cap.isOpened():
            raise ValueError(f"Błąd: OpenCV nie może otworzyć pliku: {self.path}")

        self.fps = self.cap.get(cv.CAP_PROP_FPS)
    
    def get_frame_generator(self):
        """
        Wykorzystuje mechanizm generatorów (yield), co pozwala na przetwarzanie 
        wideo o dowolnej długości bez przepełnienia pamięci RAM.
        """
        if self.cap is None or not self.cap.isOpened():
            raise RuntimeError("Strumień video nie został otwarty - wywołaj metodę open().")

        while True:
            ret, frame = self.cap.read()
            if not ret:
                break

            yield frame

    def get_metadata(self) -> dict:
        """Zwraca metadane wideo niezbędne do normalizacji czasu."""
        return {
            "fps": self.fps,
            "width": int(self.cap.get(cv.CAP_PROP_FRAME_WIDTH)),
            "height": int(self.cap.get(cv.CAP_PROP_FRAME_HEIGHT)),
            "total_frames": int(self.cap.get(cv.CAP_PROP_FRAME_COUNT))
        }
        
    def close(self):
        """Zwalnia zasoby systemowe"""
        if self.cap is not None:
            self.cap.release()
