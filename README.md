# SC2 - Shooting Coach 2.0

## About the Project

**SC2 (Shooting Coach 2.0)** is an AI-powered analytical engine that breaks down your basketball jump shot frame by frame. The app eliminates the need for expensive wearable sensors or body markers. Instead, it utilizes advanced Computer Vision to map your skeleton and calculate precise joint angles in 2D space.

The extracted data (e.g., elbow and knee flexion angles) is compared in real-time against the biomechanical models of elite NBA players (such as Damian Lillard, Kevin Durant, Klay Thompson, and Stephen Curry) to generate a personalized correction report tailored to your shooting mechanics.

## How Does the Algorithm Understand Your Shot?

The system tracks your wrist trajectory and skeletal keypoints, categorizing each shot into **4 physical phases**:

1. **READY:** Static position. You are preparing for the shot, and your body is relaxed.
2. **PREPARATION (*Dip*):** You lower your center of gravity (knee angle decreases), and your wrists bring the ball down. This is the crucial moment of loading kinetic energy from the floor.
3. **EXECUTION (*Release*):** An explosive upward movement. You open your elbow angle and transfer power from your legs to your hand. The algorithm looks for maximum fluidity and optimal energy transfer (*One-Motion*).
4. **FOLLOW THROUGH (*Swan Neck*):** The famous "swan neck." Your arm is fully extended after releasing the ball, and your wrist flops down loosely, giving the ball the proper backspin.

## Requirements & Technologies

This project was built using the following Python libraries:

* **Streamlit:** Framework for building the User Interface (UI) and displaying the analytics.
* **MediaPipe:** A powerful Machine Learning (ML) tool by Google for highly accurate body keypoint detection (Skeleton/Pose Tracking).
* **OpenCV (`cv2`):** Library for image and video frame processing.
* **NumPy:** Advanced mathematical computing for geometric analytics.

## Setting Things Up

1. **Clone the repo** to your local machine:

```bash
   git clone https://github.com/nastyCoder6/shooting-coach-2.0.git
   cd shooting-coach-2.0
```

2. **Create a virtual environment**:

```bash
   python -m venv .venv
   
   # on Windows:
   .venv\Scripts\activate
   
   # on Linux/macOS:
   source .venv/bin/activate
```

3. **Install packages** from `requirements.txt`:

```bash
   pip install -r requirements.txt
```

## Running the App

Once all dependencies are installed, run the application by typing the following into your terminal:

```bash
streamlit run app.py
```

The app should automatically open in your default web browser at `http://localhost:8501`.

## How to Use

1. Open the sidebar panel **"Konfiguracja Treningu"**.
2. **Upload a video** of your jump shot. Supported formats are `.mp4` and `.mkv`. Keep in mind that a full side-profile recording works best.
3. **Select a technical benchmark** – the biomechanical model of the player you want to compare your form (arms and legs positioning) against.
4. Specify your **shooting hand** (Right or Left).
5. Click the **"Analizuj Rzut"** button.
6. Use the slider available on the main page to review the **Frame-by-Frame Analysis**, and scroll down to the bottom to read your generated **Correction Report**.

## Project Structure

* `app.py` - Main application script responsible for the Streamlit view.
* `requirements.txt` - List of dependencies and packages to install.
* `pipeline/` - Directory containing the `shooting_pipeline.py` script (manages the video analysis pipeline based on detection and profiles).
* `core/` - Core modules: video handling (`video.py`), keypoint detection (`detector.py`), and geometric measurements (`geometry.py`).
* `logic/` - Logic for profiling (`profiler.py`), feedback (`feedback.py`), model handling (`models.py`), and shot cycle state management (`state_manager.py`).
* `models/` - JSON reference database (contains settings for Damian Lillard, Kevin Durant, Klay Thompson) and the detection engine.
