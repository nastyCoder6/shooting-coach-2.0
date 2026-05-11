from core.video import VideoProvider
from core.detector import MediaPipeDetector
import cv2

# Wstaw tutaj ścieżkę do jakiegoś wideo z rzutem (lub dowolnego .mp4)
VIDEO_PATH = r"C:\Users\Dom\Desktop\code\kyrie.mkv" 

def test_run():
    provider = VideoProvider(VIDEO_PATH)
    try:
        provider.open()
        print(f"Metadane: {provider.get_metadata()}")
        
        for i, frame in enumerate(provider.get_frame_generator()):
            cv2.imshow("Test Streamlit", frame)
            if cv2.waitKey(1) & 0xFF == ord('q') or i > 100:
                break
        print("Test zakończony sukcesem!")
    except Exception as e:
        print(f"Coś poszło nie tak: {e}")
    finally:
        provider.close()
        cv2.destroyAllWindows()

def test_ai_pipeline():
# Inicjalizacja komponentów zgodnie z architekturą systemu [cite: 70]
    provider = VideoProvider(VIDEO_PATH)
    # Detector domyślnie szuka modelu w 'models/pose_landmarker_heavy.task'
    detector = MediaPipeDetector()
    
    try:
        provider.open()
        metadata = provider.get_metadata()
        print(f"Rozpoczynam analizę: {metadata}")

        # Pętla przetwarzania wykorzystująca generator (złożoność O(1)) [cite: 74]
        for frame in provider.get_frame_generator():
            
            # Pobieramy timestamp w ms bezpośrednio z obiektu VideoCapture w providerze
            # Jest to niezbędne dla RunningMode.VIDEO w MediaPipe Tasks [cite: 113]
            timestamp_ms = int(provider.cap.get(cv2.CAP_PROP_POS_MSEC))
            
            # 1. Ekstrakcja punktów szkieletowych (Landmarks) [cite: 79]
            landmarks = detector.detect_landmarks(frame, timestamp_ms)
            
            # 2. Rysowanie autorskich połączeń BASKETBALL_CONNECTIONS [cite: 15]
            if landmarks:
                frame = detector.draw_landmarks(frame, landmarks)
            
            # Wyświetlanie wyników w oknie OpenCV [cite: 51]
            cv2.imshow("Shooting Coach 2.0 - AI Pipeline Test", frame)
            
            # Wyjście z pętli po naciśnięciu 'q'
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
        print("Analiza zakończona pomyślnie.")
        
    except Exception as e:
        print(f"Błąd krytyczny podczas testu: {e}")
        
    finally:
        # Zawsze zwalniamy zasoby systemowe 
        provider.close()
        cv2.destroyAllWindows()
        
if __name__ == "__main__":
    test_ai_pipeline()

