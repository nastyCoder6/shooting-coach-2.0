import numpy as np

class AnthropometricProfiler:
    """
    Odpowiedzialny za personalizację analizy rzutu. Uniezależnia system od wzrostu gracza i jego odległości od kamery.
    """

    def __init__(self):
        self.torso_length = 1.0 # wartość domyślna
        self.user_profile = {}

    def calibrate(self, landmarks) -> dict:
        """
        Wyznacza unikalne proporcje na podstawie klatek inicjujących.
        """
        if not landmarks:
            return {}
        
        # Punkty 11, 12 (barki) i 23, 24 (biodra)
        left_shoulder = np.array([landmarks[11].x, landmarks[11].y])
        right_shoulder = np.array([landmarks[12].x, landmarks[12].y])
        left_hip = np.array([landmarks[23].x, landmarks[23].y])
        right_hip = np.array([landmarks[24].x, landmarks[24].y]) 

        # środek tułowia jako punkt odniesienia
        shoulder_mid = (left_shoulder + right_shoulder) / 2
        hip_mid = (left_hip + right_hip) / 2

        self.torso_length = np.linalg.norm(shoulder_mid - hip_mid)

        self.user_profile = {
            "torso_length": self.torso_length,
            "hip_mid": hip_mid
        }
        return self.user_profile
    
    def normalize_landmarks(self, landmarks):
        """
        Przesuwa układ współrzędnych do środka bioder i skaluje względem tułowia
        """
        if not self.user_profile:
            return landmarks
        
        origin = self.user_profile["hip_mid"]

        # nowa lista punktów z przesuniętymi współrzędnymi
        normalized = []
        for lm in landmarks:
            norm_x = (lm.x - origin[0]) / self.torso_length
            norm_y = (lm.y - origin[1]) / self.torso_length
            normalized.append({"x": norm_x, "y": norm_y, "z": lm.z})
        return normalized