import json

class ReferenceModel:
    """
    Klasa przechowująca dane profilu referencyjnego (np. Curry_shot.json).
    Odpowiada za bezpieczne wyciąganie zakresów min/max dla stawów.
    """
    def __init__(self):
        self.data = {}

    def load_from_json(self, file_path: str):
        with open(file_path, 'r', encoding='utf-8') as f:
            self.data = json.load(f)

    def get_joint_params(self, phase: str, joint: str) -> dict:
        """
        Zwraca słownik z {min, max, description} dla danego stawu i fazy.
        Zwraca None, jeśli dana faza/staw nie są zdefiniowane.
        """
        try:
            return self.data[phase][joint]
        except KeyError:
            return None