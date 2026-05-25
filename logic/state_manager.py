class ShotStateManager:
    """
    Implementacja Maszyny Stanów (State Machine) dla rzutu koszykarskiego.
    Fazy: PREPARATION -> EXECUTION -> FOLLOW_THROUGH
    """
    def __init__(self):
        self.current_state = "PREPARATION"
        self.frame_buffer = []
        self.release_detected = False
    
    def update_state(self, elbow_angle: float, wrist_velocity: float):
        """
        Decyduje o zmianie fazy rzutu na podstawie kątów i prędkości.
        """
        if self.current_state == "PREPARATION" and elbow_angle < 100:
            # zawodnik ugina rękę - zaczyna rzut
            self.current_state = "EXECUTION"
            
        elif self.current_state == "EXECUTION" and elbow_angle > 150:
            # wyprost ręki - moment wypuszczenia piłki
            self.current_state = "FOLLOW_THROUGH"
            self.release_detected = True