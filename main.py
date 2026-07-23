

import streamlit as st
import cv2
import mediapipe as mp
import numpy as np
from collections import defaultdict, Counter
from openai import OpenAI
import tempfile
import os
from dotenv import load_dotenv

print(mp.__file__)


load_dotenv()
client = OpenAI(
    api_key=os.environ["OPENAI_API_KEY"],
    base_url="https://api.deepseek.com/v1"  
)
mp_holistic = mp.solutions.holistic

POSTURE_MEANINGS = {
    "arms_crossed": "defensive or closed-off",
    "touching_ear": "boredom, reminiscence, or fabrication",
    "touching_hair": "anxiety or nervousness",
    "hand_on_chin": "deep thought or evaluation",
    "open_arms": "confidence, openness, or determination",
    "hands_clasped": "self-soothing or patience",
    "head_down": "submission, sadness, or defeat",
    "head_tilted": "curiosity or engagement",
    "hand_behind_head": "confidence or relaxation",
    "fidgeting": "restlessness or anxiety",
}

# ============ HELPERS ============
def dist(p1, p2):
    return np.linalg.norm(np.array(p1) - np.array(p2))

def get_xy(landmark, w, h):
    return (landmark.x * w, landmark.y * h)

def detect_postures(results, w, h, prev_left_hand=None, prev_right_hand=None):
    """
    Detect 10 postures from MediaPipe Holistic results.
    Returns: list of posture strings, updated hand positions
    """
    detected = set()
    if not results.pose_landmarks:
        return list(detected), prev_left_hand, prev_right_hand

    pl = results.pose_landmarks.landmark

    # Key body points
    nose = get_xy(pl[mp_holistic.PoseLandmark.NOSE], w, h)
    left_shoulder = get_xy(pl[mp_holistic.PoseLandmark.LEFT_SHOULDER], w, h)
    right_shoulder = get_xy(pl[mp_holistic.PoseLandmark.RIGHT_SHOULDER], w, h)
    left_elbow = get_xy(pl[mp_holistic.PoseLandmark.LEFT_ELBOW], w, h)
    right_elbow = get_xy(pl[mp_holistic.PoseLandmark.RIGHT_ELBOW], w, h)
    left_wrist = get_xy(pl[mp_holistic.PoseLandmark.LEFT_WRIST], w, h)
    right_wrist = get_xy(pl[mp_holistic.PoseLandmark.RIGHT_WRIST], w, h)
    left_ear = get_xy(pl[mp_holistic.PoseLandmark.LEFT_EAR], w, h)
    right_ear = get_xy(pl[mp_holistic.PoseLandmark.RIGHT_EAR], w, h)
    left_eye = get_xy(pl[mp_holistic.PoseLandmark.LEFT_EYE], w, h)
    right_eye = get_xy(pl[mp_holistic.PoseLandmark.RIGHT_EYE], w, h)
    mouth_left = get_xy(pl[mp_holistic.PoseLandmark.MOUTH_LEFT], w, h)
    mouth_right = get_xy(pl[mp_holistic.PoseLandmark.MOUTH_RIGHT], w, h)
    mouth_center = ((mouth_left[0] + mouth_right[0]) / 2, (mouth_left[1] + mouth_right[1]) / 2)

    shoulder_y = (left_shoulder[1] + right_shoulder[1]) / 2
    shoulder_width = dist(left_shoulder, right_shoulder)

    # 1. ARMS CROSSED
    if dist(left_wrist, right_elbow) < shoulder_width * 0.4 and dist(right_wrist, left_elbow) < shoulder_width * 0.4:
        if left_wrist[0] > right_shoulder[0] and right_wrist[0] < left_shoulder[0]:
            detected.add("arms_crossed")

    # 2. OPEN ARMS
    if dist(left_wrist, right_wrist) > shoulder_width * 1.8:
        if left_wrist[1] < shoulder_y and right_wrist[1] < shoulder_y:
            detected.add("open_arms")

    # 3. HANDS CLASPED
    if dist(left_wrist, right_wrist) < shoulder_width * 0.3:
        if left_wrist[1] > shoulder_y and right_wrist[1] > shoulder_y:
            detected.add("hands_clasped")

    # 4. HEAD DOWN
    if nose[1] > shoulder_y + shoulder_width * 0.15:
        detected.add("head_down")

    # 5. HEAD TILTED
    ear_height_diff = abs(left_ear[1] - right_ear[1])
    if ear_height_diff > shoulder_width * 0.15:
        detected.add("head_tilted")

    # Hand-related postures
    for hand_idx, (hand_landmarks, wrist, side) in enumerate([
        (results.left_hand_landmarks, left_wrist, "left"),
        (results.right_hand_landmarks, right_wrist, "right")
    ]):
        if not hand_landmarks:
            continue
        hand = hand_landmarks.landmark
        middle_tip = get_xy(hand[mp_holistic.HandLandmark.MIDDLE_FINGER_TIP], w, h)
        hand_center = get_xy(hand[mp_holistic.HandLandmark.MIDDLE_FINGER_MCP], w, h)

        # 6. TOUCHING EAR
        if min(dist(hand_center, left_ear), dist(hand_center, right_ear)) < shoulder_width * 0.25:
            detected.add("touching_ear")

        # 7. TOUCHING HAIR / HEAD
        forehead = ((left_eye[0] + right_eye[0]) / 2, ((left_eye[1] + right_eye[1]) / 2) - shoulder_width * 0.3)
        if dist(hand_center, forehead) < shoulder_width * 0.3:
            detected.add("touching_hair")

        # 8. HAND ON CHIN
        if dist(hand_center, mouth_center) < shoulder_width * 0.25:
            detected.add("hand_on_chin")

        # 9. HAND BEHIND HEAD
        back_of_head = ((left_ear[0] + right_ear[0]) / 2, (left_ear[1] + right_ear[1]) / 2 - shoulder_width * 0.1)
        if dist(hand_center, back_of_head) < shoulder_width * 0.3:
            detected.add("hand_behind_head")

        # 10. FIDGETING (rapid hand movement)
        prev = prev_left_hand if side == "left" else prev_right_hand
        if prev is not None:
            movement = dist(hand_center, prev)
            if movement > shoulder_width * 0.35:
                detected.add("fidgeting")

        # Update previous hand position
        if side == "left":
            prev_left_hand = hand_center
        else:
            prev_right_hand = hand_center

    return list(detected), prev_left_hand, prev_right_hand


def generate_narrative(posture_counts, duration_sec):
    """Send aggregated posture data to GPT-4o-mini for narrative generation."""
    if not posture_counts:
        return "No significant postural behaviors were detected in this video."

    lines = []
    for posture, count in posture_counts.most_common():
        meaning = POSTURE_MEANINGS.get(posture, "unknown behavior")
        freq = "frequently" if count > 5 else "occasionally"
        lines.append(f"- {posture.replace('_', ' ').title()} ({freq}, ~{count} detections): suggests {meaning}")

    prompt = f"""You are a behavioral psychology assistant analyzing a video of {duration_sec:.0f} seconds.
The following postures were detected:
{chr(10).join(lines)}

Write a concise 3-4 sentence psychological profile of the subject. Be speculative but grounded in body language research. Do not list the postures again; synthesize them into a coherent narrative about the person's mental state."""

    try:
        r = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=250,
            temperature=0.7,
        )
        return r.choices[0].message.content
    except Exception as e:
        return f"[LLM Error: {e}] Fallback: The subject showed signs of {', '.join([p.replace('_', ' ') for p in posture_counts.keys()])}."


# ============ STREAMLIT UI ============
st.set_page_config(page_title="Psychological Behavior Analyzer", layout="wide")
st.title("🧠 Psychological Behavior Analyzer")
st.caption("Mid-term MVP: 10-posture rule-based detection + LLM narrative generation")

uploaded = st.file_uploader("Upload interview video (MP4/MOV)", type=["mp4", "mov", "avi"])

if uploaded:
    # Save temp file
    tfile = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
    tfile.write(uploaded.read())
    video_path = tfile.name

    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration_sec = total_frames / fps

    st.info(f"Video loaded: {duration_sec:.1f}s @ {fps:.1f} FPS. Processing every 10th frame for speed...")

    posture_timeline = []
    posture_counts = Counter()
    prev_lh, prev_rh = None, None

    progress_bar = st.progress(0)
    frame_placeholder = st.empty()

    with mp_holistic.Holistic(static_image_mode=False, model_complexity=1) as holistic:
        frame_idx = 0
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            # Process every 10th frame (~3x speedup)
            if frame_idx % 10 == 0:
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = holistic.process(rgb)
                h, w = frame.shape[:2]

                postures, prev_lh, prev_rh = detect_postures(results, w, h, prev_lh, prev_rh)
                timestamp = frame_idx / fps

                for p in postures:
                    posture_timeline.append((timestamp, p))
                    posture_counts[p] += 1

                # Draw skeleton for preview (optional)
                annotated = rgb.copy()
                if results.pose_landmarks:
                    mp.solutions.drawing_utils.draw_landmarks(
                        annotated, results.pose_landmarks, mp_holistic.POSE_CONNECTIONS
                    )

                frame_placeholder.image(annotated, caption=f"Frame {frame_idx} | Detected: {postures}", use_container_width=True)

            frame_idx += 1
            progress_bar.progress(min(frame_idx / total_frames, 1.0))

        cap.release()

    os.unlink(video_path)

    # ============ RESULTS ============
    st.divider()
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📊 Detected Postures")
        if posture_counts:
            st.bar_chart({k.replace("_", " ").title(): v for k, v in posture_counts.most_common()})
        else:
            st.warning("No postures detected. Try a video with clearer body visibility.")

        st.subheader("⏱️ Timeline (first 20 events)")
        st.write(posture_timeline[:20])

    with col2:
        st.subheader("📝 Psychological Analysis")
        with st.spinner("Generating narrative via LLM..."):
            narrative = generate_narrative(posture_counts, duration_sec)
        st.success(narrative)

    # Export JSON
    import json
    export = {
        "video_duration_sec": duration_sec,
        "posture_counts": dict(posture_counts),
        "timeline": [{"time_sec": round(t, 1), "posture": p} for t, p in posture_timeline],
        "narrative": narrative,
    }
    st.download_button("Download JSON Report", json.dumps(export, indent=2), "report.json", "application/json")
