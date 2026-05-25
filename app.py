import streamlit as st
import cv2
import tempfile
import numpy as np

from core.video import VideoProvider
from core.detector import MediaPipeDetector
from core.geometry import GeometryEngine
from logic.profiler import AnthropometricProfiler
from logic.state_manager import ShotStateManager
from logic.models import ReferenceModel
from logic.feedback import FeedbackGenerator

# Klasa pomocnicza do konwersji słowników na obiekty dla GeometryEngine
class Point:
    def __init__(self, d):
        self.x, self.y, self.z = d['x'], d['y'], d['z']

def main():
    st.set_page_config(page_title="Shooting Coach 2.0", layout="wide")
    st.title("Shooting Coach 2.0")
    st.markdown("Autonomiczny system ekspercki do biomechanicznej analizy rzutu.")

    # --- Pasek boczny ---
    st.sidebar.header("Konfiguracja Treningu")
    uploaded_file = st.sidebar.file_uploader("Wgraj wideo z rzutem", type=['mp4', 'mkv'])
    coach_model = st.sidebar.selectbox("Wzorzec techniczny", ["Stephen Curry"])

    if uploaded_file is not None:
        # Zapisz wideo do pliku tymczasowego (wymóg OpenCV)
        tfile = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
        tfile.write(uploaded_file.read())

        if st.sidebar.button("Analizuj Rzut", type="primary"):
            
            # 1. Inicjalizacja instancji systemu[cite: 1]
            provider = VideoProvider(tfile.name)
            detector = MediaPipeDetector()
            geometry = GeometryEngine()
            profiler = AnthropometricProfiler()
            state_manager = ShotStateManager()
            
            ref_model = ReferenceModel()
            ref_model.load_from_json("models/curry_shot.json")
            feedback_gen = FeedbackGenerator(ref_model)

            provider.open()
            fps = provider.get_metadata().get('fps', 30)
            
            # Kolumny Streamlit do wyświetlania wideo i statystyk
            col1, col2 = st.columns([2, 1])
            video_placeholder = col1.empty()
            stats_placeholder = col2.empty()
            
            frame_count = 0
            prev_wrist = None
            last_time = 0
            
            final_feedback_elbow = ""
            final_feedback_knee = ""
            release_angles = {}

            # 2. Główna pętla przetwarzania (Pipeline)[cite: 1]
            for frame in provider.get_frame_generator():
                timestamp_ms = int(provider.cap.get(cv2.CAP_PROP_POS_MSEC))
                time_delta = (timestamp_ms - last_time) / 1000.0
                last_time = timestamp_ms

                landmarks = detector.detect_landmarks(frame, timestamp_ms)
                
                if landmarks:
                    # Kalibracja (pierwsze 30 klatek) i normalizacja antropometryczna[cite: 1]
                    if frame_count < 30:
                        profiler.calibrate(landmarks)
                        cv2.putText(frame, "KALIBRACJA...", (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
                    else:
                        norm_lms = profiler.normalize_landmarks(landmarks)
                        
                        # Pobranie kluczowych punktów (Prawa strona ciała)
                        shoulder = Point(norm_lms[12])
                        elbow = Point(norm_lms[14])
                        wrist = Point(norm_lms[16])
                        
                        hip = Point(norm_lms[24])
                        knee = Point(norm_lms[26])
                        ankle = Point(norm_lms[28])
                        
                        # 3. Obliczenia geometryczne[cite: 1]
                        elbow_angle = geometry.calculate_angle3d(shoulder, elbow, wrist)
                        knee_angle = geometry.calculate_angle3d(hip, knee, ankle)
                        
                        wrist_velocity = geometry.calculate_velocity(prev_wrist, wrist, time_delta) if prev_wrist else 0
                        prev_wrist = wrist

                        # 4. Maszyna stanów i wnioskowanie[cite: 1]
                        state_manager.update_state(elbow_angle, wrist_velocity)
                        current_state = state_manager.current_state

                        # Jeśli właśnie wykryto wyrzut, zapisz parametry i wygeneruj feedback!
                        if state_manager.current_state and not final_feedback_elbow:
                            release_angles = {"elbow": elbow_angle, "knee": knee_angle}
                            
                            final_feedback_elbow = feedback_gen.generate_report(elbow_angle, "EXECUTION", "elbow")
                            final_feedback_knee = feedback_gen.generate_report(knee_angle, "EXECUTION", "knee")
                            
                            cv2.putText(frame, "WYRZUT ZAREJESTROWANY", (50, 150), cv2.FONT_HERSHEY_DUPLEX, 1.5, (0, 0, 255), 3)

                        # Rysowanie parametrów na wideo
                        cv2.putText(frame, f"Faza: {current_state}", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
                        cv2.putText(frame, f"Lokiec: {int(elbow_angle)}", (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                        cv2.putText(frame, f"Kolano: {int(knee_angle)}", (20, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 100, 0), 2)

                    # Rysowanie szkieletu
                    frame = detector.draw_landmarks(frame, landmarks)
                
                # Aktualizacja obrazu w UI
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                video_placeholder.image(frame_rgb, channels="RGB", use_column_width=True)
                
                # Aktualizacja statystyk na żywo
                with stats_placeholder.container():
                    st.write("### Parametry na żywo")
                    st.metric("Faza rzutu", state_manager.current_state)
                    if 'elbow_angle' in locals():
                        st.metric("Kąt Łokcia", f"{int(elbow_angle)}°")
                        st.metric("Kąt Kolana", f"{int(knee_angle)}°")
                
                frame_count += 1

            provider.close()
            
            # --- RAPORT KOŃCOWY ---
            st.divider()
            st.subheader("📊 Twój Raport Korygujący")
            
            if final_feedback_elbow:
                col_a, col_b = st.columns(2)
                with col_a:
                    st.info(f"**Ręka rzucająca (Łokieć: {int(release_angles['elbow'])}°)**\n\nAnaliza systemu: {final_feedback_elbow}")
                with col_b:
                    st.info(f"**Nogi (Kolano: {int(release_angles['knee'])}°)**\n\nAnaliza systemu: {final_feedback_knee}")
            else:
                st.warning("Nie udało się jednoznacznie wykryć momentu wyrzutu piłki (Release Point). Spróbuj innego wideo.")

if __name__ == "__main__":
    main()