import cv2
import numpy as np
from core.video import VideoProvider
from core.detector import MediaPipeDetector
from core.geometry import GeometryEngine
from logic.profiler import AnthropometricProfiler
from logic.models import ReferenceModel
from logic.feedback import FeedbackGenerator
from logic.state_manager import ShotStateManager

class ShootingPipeline:
    def __init__(self, reference_model_path: str):
        self.detector = MediaPipeDetector()
        self.geometry = GeometryEngine()
        self.profiler = AnthropometricProfiler()
        
        # Inicjalizacja Maszyny Stanów (rozpoznawanie faz)
        self.state_manager = ShotStateManager()
        
        self.ref_model = ReferenceModel()
        self.ref_model.load_from_json(reference_model_path)
        self.feedback_gen = FeedbackGenerator(self.ref_model)
        
        self.min_knee_prep = 180.0
        self.max_elbow_exec = 0.0
        self.knee_at_exec = 0.0

        self.report_prep_knee = {}
        self.report_exec_elbow = {}
        self.report_exec_knee = {}

    def process_video(self, video_path: str, handedness: str = "Prawa"):
        if handedness == "Lewa":
            idx_shoulder, idx_elbow, idx_wrist = 11, 13, 15
            idx_hip, idx_knee, idx_ankle = 23, 25, 27
        else:
            idx_shoulder, idx_elbow, idx_wrist = 12, 14, 16
            idx_hip, idx_knee, idx_ankle = 24, 26, 28

        provider = VideoProvider(video_path)
        provider.open()
        
        # --- ZABEZPIECZENIE PRZED BŁĘDAMI CZASU OpenCV ---
        fps = provider.cap.get(cv2.CAP_PROP_FPS)
        if fps <= 0 or np.isnan(fps): 
            fps = 30.0 
        time_delta = 1.0 / fps  # Np. 0.033 sekundy na klatkę
        
        frame_count = 0
        prev_wrist = None  # Do liczenia prędkości

        for frame in provider.get_frame_generator():
            # Stabilny czas wyliczany na podstawie FPS, a nie msec z OpenCV
            timestamp_ms = int(frame_count * time_delta * 1000)
            landmarks = self.detector.detect_landmarks(frame, timestamp_ms)
            stats = {}
            
            if landmarks:
                norm_lms = self.profiler.normalize_landmarks(landmarks)
                
                shoulder, elbow, wrist = norm_lms[idx_shoulder], norm_lms[idx_elbow], norm_lms[idx_wrist]
                hip, knee, ankle = norm_lms[idx_hip], norm_lms[idx_knee], norm_lms[idx_ankle]
                
                elbow_angle = self.geometry.calculate_angle2d(shoulder, elbow, wrist)
                knee_angle = self.geometry.calculate_angle2d(hip, knee, ankle)
                
                # --- POBRANIE WSPÓŁRZĘDNYCH Y (Mniejsze Y to WYŻEJ na ekranie) ---
                wrist_y = wrist.get('y', 0.0) if isinstance(wrist, dict) else wrist.y
                shoulder_y = shoulder.get('y', 0.0) if isinstance(shoulder, dict) else shoulder.y
                
                # --- DELEGOWANIE DECYZJI DO MASZYNY STANÓW ---
                self.state_manager.update_state(elbow_angle, wrist_y)
                current_phase = self.state_manager.current_state

                # --- LOGIKA REJESTRACJI DANYCH DO RAPORTU KOŃCOWEGO JSON ---
                
                if current_phase == "PREPARATION":
                    if knee_angle < self.min_knee_prep:
                        self.min_knee_prep = knee_angle
                
                elif current_phase in ["EXECUTION", "FOLLOW THROUGH"]:
                    # BRAMKA BIOMECHANICZNA:
                    # Pozwalamy kątowi rosnąć aż do osiągnięcia absolutnego szczytu (np. 170 stopni).
                    # Ale odetniemy zapis w ułamku sekundy, gdy gracz OPUSCI rękę po rzucie
                    # (gdy nadgarstek spadnie poniżej linii barków).
                    if wrist_y < shoulder_y:  
                        if elbow_angle > self.max_elbow_exec:
                            self.max_elbow_exec = elbow_angle
                            self.knee_at_exec = knee_angle

                # --- PRZEKAZANIE DANYCH DO INTERFEJSU STREAMLIT ---
                stats = {
                    "state": current_phase,
                    "elbow_angle": elbow_angle,
                    "knee_angle": knee_angle
                }
                
                side_label = "L" if handedness == "Lewa" else "P"
                cv2.putText(frame, f"Phase: {current_phase}", (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                cv2.putText(frame, f"Elbow ({side_label}): {int(elbow_angle)}", (20, 65), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cv2.putText(frame, f"Knee ({side_label}): {int(knee_angle)}", (20, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 100, 0), 2)

            frame = self.detector.draw_landmarks(frame, landmarks)
            
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_count += 1
            yield frame_rgb, stats

        provider.close()

        # --- EWALUACJA NA KONIEC WIDEO ---
        if self.max_elbow_exec > 0: 
            self.report_prep_knee = self.feedback_gen.generate_report(self.min_knee_prep, "PREPARATION", "knee")
            self.report_exec_elbow = self.feedback_gen.generate_report(self.max_elbow_exec, "EXECUTION", "elbow")
            self.report_exec_knee = self.feedback_gen.generate_report(self.knee_at_exec, "EXECUTION", "knee")
