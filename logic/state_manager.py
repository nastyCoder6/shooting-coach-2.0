class ShotStateManager:
    """
    Maszyna Stanów oparta na analizie wektora pionowego Y nadgarstka.
    """
    def __init__(self):
        self.current_state = "READY"
        self.release_detected = False
        self.wrist_y_history = []
        self.movement_threshold = 0.015 

    def update_state(self, elbow_angle: float, wrist_y: float):
        self.wrist_y_history.append(wrist_y)
        
        if len(self.wrist_y_history) > 5:
            self.wrist_y_history.pop(0)
            
        if len(self.wrist_y_history) < 5:
            return

        # Różnica wysokości nadgarstka
        y_diff = self.wrist_y_history[-1] - self.wrist_y_history[0]

        if self.current_state == "READY":
            # DIP (ruch w dół)
            if y_diff > self.movement_threshold:
                self.current_state = "PREPARATION"
                
        elif self.current_state == "PREPARATION":
            # WYRZUT (ruch w górę)
            if y_diff < -self.movement_threshold:
                self.current_state = "EXECUTION"
                
        elif self.current_state == "EXECUTION":
            # FOLLOW THROUGH (Twoja ulubiona, działająca reguła 145 stopni)
            if elbow_angle > 145:
                self.current_state = "FOLLOW THROUGH"
                self.release_detected = True