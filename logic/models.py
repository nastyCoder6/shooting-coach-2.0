import json
import os

class ReferenceModel:
    """
    Repozytorium wiedzy eksperckiej. Przechowuje idealne zakresy biomechaniczne.
    """
    def __init__(self):
        self.ideal_ranges = {}

    def load_from_json(self, file_path: str):
        """Wczytuje profil biomechaniczny rzutu. """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Nie znaleziono wzorca: {file_path}")

        with open(file_path, 'r') as f:
            self.ideal_ranges = json.load(f)

    def get_ideal_angle(self, joint_name: str, phase: str) -> dict:
        """Zwraca zakres (min, max) dla danego stawu w konkretnej fazie. """
        return self.ideal_ranges.get(phase, {}).get(joint_name, {"min": 0, "max": 180})
