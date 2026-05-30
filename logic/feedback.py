class FeedbackGenerator:
    def __init__(self, ref_model):
        self.ref_model = ref_model

    def generate_report(self, actual_angle: float, phase: str, joint: str) -> dict:
        params = self.ref_model.get_joint_params(phase, joint)
        
        if not params:
            return {"status": "error", "text": "Brak danych referencyjnych do oceny tego parametru."}

        min_angle = params.get("min", 0.0)
        max_angle = params.get("max", 0.0)
        description = params.get("description", "")

        actual_angle = int(actual_angle)
        
        if actual_angle < min_angle:
            diff = int(min_angle - actual_angle)
            return {
                "status": "alert",
                "text": f"**Kąt jest zbyt mały ({actual_angle}°).** \n\nZłoty standard dla tej fazy to **{int(min_angle)}° - {int(max_angle)}°**. Brakuje Ci około {diff}° do dolnej granicy normy. Rozłóż staw mocniej. \n\n*Cel: {description}*"
            }
            
        elif actual_angle > max_angle:
            diff = int(actual_angle - max_angle)
            return {
                "status": "alert",
                "text": f"**Kąt jest zbyt duży ({actual_angle}°).** \n\nZłoty standard dla tej fazy to **{int(min_angle)}° - {int(max_angle)}°**. Przestrzeliłeś o około {diff}° powyżej górnej granicy. Utrzymaj staw bardziej zgięty. \n\n*Cel: {description}*"
            }
            
        else:
            return {
                "status": "success",
                "text": f"**Idealnie! ({actual_angle}°)** \n\nTwój wynik mieści się w profesjonalnym zakresie (**{int(min_angle)}° - {int(max_angle)}°**). Utrzymaj ten nawyk ruchowy. \n\n*Cel: {description}*"
            }