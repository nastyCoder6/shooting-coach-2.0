class FeedbackGenerator:
    """
    Kontroler logiki biznesowej. Generuje raporty korygujące na podstawie odchyleń od modelu wzorcowego
    """
    def __init__(self, reference_model):
        self.reference_model = reference_model

    def generate_report(self, user_angle: float, phase: str, joint: str) ->str:
        ranges = self.reference_model.get_ideal_angle(joint, phase)
        r_min = ranges["min"]
        r_max = ranges["max"]

        if user_angle < r_min:
            return "Zwiększ kąt wyprostu - ręka zbyt mocno ugięta w momencie rzutu."
        elif user_angle > r_max:
            return "Zbyt duży wyprost - tracisz kontrolę nad trajektorią."
        else:
            return "Idealna technika! Zachowaj ten parametr."
    
    def create_visual_overlay(self, frame, metrics: dict):
        """Nakłada analityczne podsumowanie na końcową klatkę."""
        # Implementacja rysowania statystyk na ekranie (np. po rzucie)
        pass