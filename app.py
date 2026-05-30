import streamlit as st
import tempfile
from pipeline.shooting_pipeline import ShootingPipeline

st.set_page_config(
    page_title="SC2", 
    layout="wide", 
    initial_sidebar_state="expanded",
    page_icon="favicon.ico"
)

def inject_premium_dark_mode_css():
    PRIMARY_BLUE = "#3B82F6"
    TEXT_MAIN = "#F3F4F6"
    BG_CARD = "#1F2937"
    
    css = f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
        html, body, [data-testid="stAppViewContainer"] {{ font-family: 'Inter', sans-serif !important; }}
        [data-testid="stTitle"] {{ font-size: 2rem !important; margin-bottom: 0.2rem !important; color: {TEXT_MAIN} !important; }}
        [data-testid="stMarkdown"] p {{ font-size: 0.95rem !important; margin-top: 0 !important; }}
        hr {{ border-top: 1px solid #374151 !important; margin-top: 1rem !important; margin-bottom: 1rem !important; }}

        /* Karty dolne */
        .premium-card-container {{ display: grid; grid-template-columns: repeat(3, 1fr) !important; gap: 1.5rem; margin-top: 1.5rem; }}
        .report-card {{ background-color: {BG_CARD}; border-radius: 8px; padding: 1.5rem; border: 1px solid #374151; display: flex; gap: 1rem; align-items: flex-start; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); }}
        .card-icon-container {{ background-color: #2D3748; border-radius: 6px; padding: 1rem; display: flex; height: 50px; width: 50px; align-items: center; justify-content: center; }}
        .card-icon {{ font-size: 1.5rem !important; }}
        .card-content h4 {{ margin-top: 0; margin-bottom: 0.4rem !important; color: {TEXT_MAIN}; font-size: 1rem !important; font-weight: 600; }}
        .card-content p {{ margin: 0 !important; color: #D1D5DB; font-size: 0.9rem !important; line-height: 1.5; }}
        
        /* --- KULOODPORNE WYŚRODKOWANIE WIDEO --- */
        [data-testid="stImage"] {{
            width: 100% !important;
            display: flex !important;
            justify-content: center !important;
        }}
        [data-testid="stImage"] img {{
            max-height: 65vh !important;
            width: auto !important;
            margin: 0 auto !important;
            display: block !important;
            border-radius: 8px !important;
            border: 1px solid #374151 !important;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3) !important;
        }}

        /* --- STYLIZACJA PANELA EDUKACYJNEGO (st.info) --- */
        [data-testid="stAlert"] {{
            background-color: {BG_CARD} !important;
            border: 1px solid #374151 !important;
            border-left: 4px solid {PRIMARY_BLUE} !important;
            border-radius: 8px !important;
            padding: 1.5rem !important;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1) !important;
        }}
        [data-testid="stAlert"] p {{
            color: #D1D5DB !important;
            font-size: 0.95rem !important;
            line-height: 1.6 !important;
            margin-bottom: 0.5rem !important;
        }}
        [data-testid="stAlert"] strong {{
            color: {TEXT_MAIN} !important;
            font-size: 1rem !important;
        }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

def inject_metric_dense_css():
    css = """
    <style>
        .side-metrics-card {
            background-color: #1F2937;
            border-radius: 8px;
            padding: 1.5rem;
            border: 1px solid #374151;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
            width: 100%;
        }
        .metrics-header {
            margin-top: 0; 
            color: #F3F4F6; 
            border-bottom: 1px solid #374151; 
            padding-bottom: 0.8rem; 
            margin-bottom: 1.5rem;
            font-size: 1.1rem;
            font-weight: 600;
        }
        .metric-block { margin-bottom: 1.5rem; }
        .metric-block:last-child { margin-bottom: 0; }
        .metric-label { font-size: 0.85rem; text-transform: uppercase; color: #9CA3AF; font-weight: 600; margin-bottom: 0.2rem; }
        .metric-value { font-size: 2.2rem; color: #3B82F6; font-weight: 700; display: flex; align-items: center; gap: 10px; line-height: 1; }
        .phase-text { font-size: 1.6rem; color: #3B82F6; }
        .delta-tag { font-size: 0.75rem; padding: 3px 8px; border-radius: 999px; color: white; font-weight: 600; }
        .delta-tag.success { background-color: #10B981; }
        .delta-tag.live { background-color: #FBBF24; color: #1F2937; }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

def render_sidebar():
    with st.sidebar:
        st.header("Konfiguracja Treningu")
        uploaded_file = st.file_uploader("Wgraj wideo z rzutem", type=["mp4", "mkv"])
        coach_model = st.selectbox("Wzorzec techniczny", ["Stephen_Curry", "Klay_Thompson", "Kevin_Durant", "Damian_Lillard"])
        
        handedness = st.radio(
            "Ręka rzucająca", 
            ["Prawa", "Lewa"], 
            index=0, 
            help="Zmień na 'Lewa', jeśli zawodnik jest leworęczny."
        )
        
        analyze_btn = st.button("Analizuj Rzut", type="primary", width='stretch')
        return uploaded_file, coach_model, handedness, analyze_btn

def render_metric_panel(stats):
    phase = stats.get("state", "Oczekiwanie...")
    arm_angle = f"{int(stats['elbow_angle'])}°" if "elbow_angle" in stats else "--"
    leg_angle = f"{int(stats['knee_angle'])}°" if "knee_angle" in stats else "--"

    html = f"""
    <div class="side-metrics-card">
        <h4 class="metrics-header">Dane poklatkowe</h4>
        <div class="metric-block">
            <div class="metric-label">Faza rzutu</div>
            <div class="metric-value phase-text">{phase} <span class="delta-tag live">LIVE</span></div>
        </div>
        <div class="metric-block">
            <div class="metric-label">Kąt łokcia</div>
            <div class="metric-value">{arm_angle} <span class="delta-tag live">LIVE</span></div>
        </div>
        <div class="metric-block">
            <div class="metric-label">Kąt kolana</div>
            <div class="metric-value">{leg_angle} <span class="delta-tag live">LIVE</span></div>
        </div>
    </div>
    """
    st.markdown(html.replace('\n', ''), unsafe_allow_html=True)

def main():
    inject_premium_dark_mode_css()
    inject_metric_dense_css()
    
    st.title("SC2")
    st.markdown("*Twój osobisty Shooting Coach*")

    # --- NOWA SEKCJA EDUKACYJNA ---
    st.info("""
    **Czym jest SC2?** To analityczny silnik sztucznej inteligencji, który analizuje Twój rzut klatka po klatce. Bez żadnych czujników na ciele – algorytm wykorzystuje widzenie komputerowe do mapowania szkieletu i wyliczania precyzyjnych kątów stawów w przestrzeni 2D. Uzyskane dane zestawia z modelem biomechanicznym graczy NBA, aby wygenerować spersonalizowany raport korygujący.

    **Jak algorytm rozumie Twój rzut?** System śledzi trajektorię nadgarstka i dzieli każdy rzut na 4 fizyczne etapy:
    * **READY:** Pozycja statyczna. Szykujesz się do rzutu, a Twoje ciało jest zrelaksowane.
    * **PREPARATION (Zejście):** Tzw. *Dip*. Obniżasz środek ciężkości (kąt kolan maleje), a nadgarstki z piłką wędrują w dół. To kluczowy moment ładowania energii kinetycznej z parkietu.
    * **EXECUTION (Wyrzut):** Wybuchowy ruch w górę. Otwierasz kąt łokcia i transferujesz siłę z nóg do dłoni. Algorytm szuka tutaj maksymalnej płynności (One-Motion).
    * **FOLLOW THROUGH (Zakończenie):** Słynna *łabędzia szyja*. Ręka zostaje w pełni wyprostowana po wypuszczeniu piłki, a nadgarstek luźno opada w dół, co nadaje piłce odpowiednią rotację wsteczną (backspin).
    """)

    st.divider()

    uploaded_file, coach_model, handedness, analyze_btn = render_sidebar()

    if "analysis_done" not in st.session_state:
        st.session_state.analysis_done = False
        st.session_state.frames = []
        st.session_state.reports = {}

    if analyze_btn and uploaded_file:
        with st.spinner(f"Trener analizuje Twój rzut na tle zawodnika {coach_model}..."):
            tfile = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
            tfile.write(uploaded_file.read())

            model_path = f"models/{coach_model}.json"
            pipeline = ShootingPipeline(model_path)

            frames_data = []
            
            for frame_rgb, stats in pipeline.process_video(tfile.name, handedness=handedness):
                frames_data.append({"frame": frame_rgb, "stats": stats})
            
            st.session_state.frames = frames_data
            
            st.session_state.reports = {
                "prep_knee": pipeline.report_prep_knee if hasattr(pipeline, 'report_prep_knee') else {},
                "exec_elbow": pipeline.report_exec_elbow if hasattr(pipeline, 'report_exec_elbow') else {},
                "exec_knee": pipeline.report_exec_knee if hasattr(pipeline, 'report_exec_knee') else {}
            }
            
            st.session_state.analysis_done = True

    if not st.session_state.analysis_done:
        st.info("Wgraj wideo z rzutem i kliknij **Analizuj Rzut**, aby rozpocząć profilowanie.")
        return
    
    frames = st.session_state.frames
    max_frames = len(frames) - 1

    st.subheader("Analiza Poklatkowa")
    
    frame_idx = st.slider(
        "Wybierz klatkę wideo do szczegółowej analizy", 
        min_value=0, 
        max_value=max_frames, 
        value=0, 
        step=1,
        help="Przesuwaj suwak w lewo i prawo, aby analizować ruch klatka po klatce."
    )

    current_data = frames[frame_idx]
    current_frame = current_data["frame"]
    current_stats = current_data["stats"]

    video_col, metrics_col = st.columns([4, 1], gap="large")

    with video_col:
        # Trik na natywne wyśrodkowanie: 
        # Tworzymy 3 pod-kolumny. Lewa i prawa robią za marginesy, środkowa trzyma wideo.
        # Proporcje [1, 2, 1] idealnie sprawdzają się dla pionowych nagrań z telefonu.
        left_spacer, center_vid_col, right_spacer = st.columns([1, 2, 1])
        
        with center_vid_col:
            st.image(current_frame, channels="RGB", width="stretch")

    with metrics_col:
        render_metric_panel(current_stats)
    
    st.divider()
    st.subheader("Raport Korygujący")
    
    reports = st.session_state.reports
    
    if reports.get("exec_elbow"):
        def get_icon(status):
            return "✅" if status == "success" else "❌"

        pk_status = reports["prep_knee"].get('status', 'error')
        pk_msg = reports["prep_knee"].get('text', 'Brak danych z fazy zejścia.')
        
        ee_status = reports["exec_elbow"].get('status', 'error')
        ee_msg = reports["exec_elbow"].get('text', 'Brak danych z momentu wyrzutu.')
        
        ek_status = reports["exec_knee"].get('status', 'error')
        ek_msg = reports["exec_knee"].get('text', 'Brak danych wyprostu kolana.')

        st.markdown(f"""
            <div class="premium-card-container">
                <div class="report-card">
                    <div class="card-icon-container"><span class="card-icon">🧎‍♂️</span></div>
                    <div class="card-content">
                        <h4>Faza Zejścia (Kolano) {get_icon(pk_status)}</h4>
                        <p>{pk_msg}</p>
                    </div>
                </div>
                <div class="report-card">
                    <div class="card-icon-container"><span class="card-icon">💪</span></div>
                    <div class="card-content">
                        <h4>Wyrzut (Łokieć) {get_icon(ee_status)}</h4>
                        <p>{ee_msg}</p>
                    </div>
                </div>
                <div class="report-card">
                    <div class="card-icon-container"><span class="card-icon">🦵</span></div>
                    <div class="card-content">
                        <h4>Wybicie (Kolano) {get_icon(ek_status)}</h4>
                        <p>{ek_msg}</p>
                    </div>
                </div>
            </div>
        """.replace('\n', ''), unsafe_allow_html=True)
    else:
        st.warning("Nie udało się jednoznacznie wykryć momentu wyrzutu piłki (Brak wygenerowanego raportu dla łokcia).")

if __name__ == "__main__":
    main()