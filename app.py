"""Streamlit entrypoint: upload a video, run the mid-term detection pipeline, show results."""

from __future__ import annotations

import os
import tempfile
from collections import Counter

import mediapipe as mp
import streamlit as st
from dotenv import load_dotenv

from src.capture.video import sampled_frames, video_duration_sec
from src.detection.holistic import HolisticDetector
from src.export.report import build_report, report_to_json
from src.narrative.generator import generate_narrative
from src.taxonomy.detector import MotionState, detect_postures

load_dotenv()

_mp_holistic = mp.solutions.holistic

st.set_page_config(page_title="Psychological Behavior Analyzer", layout="wide")
st.title("Psychological Behavior Analyzer")
st.caption("40-posture rule-based detection (body, hand, head) + LLM narrative generation")
st.warning("Heuristic course demo — not a clinically validated behavioral assessment tool.")

uploaded = st.file_uploader("Upload interview video (MP4/MOV/AVI)", type=["mp4", "mov", "avi"])

if uploaded:
    tfile = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
    tfile.write(uploaded.read())
    tfile.close()
    video_path = tfile.name

    try:
        duration_sec, fps = video_duration_sec(video_path)
        st.info(
            f"Video loaded: {duration_sec:.1f}s @ {fps:.1f} FPS. Processing every 10th frame..."
        )

        posture_timeline: list[tuple[float, str]] = []
        posture_counts: Counter = Counter()
        prev_state = MotionState()

        progress_bar = st.progress(0)
        frame_placeholder = st.empty()

        with HolisticDetector() as detector:
            for frame_idx, timestamp, frame in sampled_frames(video_path, every_n=10):
                detections = detector.process(frame)
                labels, prev_state = detect_postures(
                    detections.pose, detections.left_hand, detections.right_hand, prev_state
                )
                for label in labels:
                    posture_timeline.append((timestamp, label))
                    posture_counts[label] += 1

                annotated = frame[:, :, ::-1].copy()
                if detections.raw_pose_landmarks:
                    mp.solutions.drawing_utils.draw_landmarks(
                        annotated, detections.raw_pose_landmarks, _mp_holistic.POSE_CONNECTIONS
                    )
                frame_placeholder.image(
                    annotated,
                    caption=f"Frame {frame_idx} | Detected: {sorted(labels)}",
                    use_container_width=True,
                )
                progress_bar.progress(min(timestamp / duration_sec, 1.0) if duration_sec else 1.0)

        st.divider()
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Detected Postures")
            if posture_counts:
                st.bar_chart(
                    {k.replace("_", " ").title(): v for k, v in posture_counts.most_common()}
                )
            else:
                st.warning("No postures detected. Try a video with clearer body visibility.")

            st.subheader("Timeline (first 20 events)")
            st.write(posture_timeline[:20])

        with col2:
            st.subheader("Psychological Analysis")
            with st.spinner("Generating narrative via Gemini..."):
                narrative = generate_narrative(posture_counts, duration_sec)
            st.success(narrative)

        report = build_report(duration_sec, posture_counts, posture_timeline, narrative)
        st.download_button(
            "Download JSON Report", report_to_json(report), "report.json", "application/json"
        )
    finally:
        os.unlink(video_path)
