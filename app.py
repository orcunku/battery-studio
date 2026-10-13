import json
from pathlib import Path
import streamlit as st
from coach import get_ai_coach_advice
from visualizer import render_drum_visualizer

st.set_page_config(page_title="Battery Studio", page_icon="🥁", layout="wide")

st.title("🥁 Battery Studio")
st.caption("Interactive Drum Practice & Spotlight Studio Engine")

# 1. Sidebar Song Selection
st.sidebar.header("🎵 Song Selection")
song_option = st.sidebar.selectbox(
    "Select Track",
    ["Seven Nation Army (Easy)", "Empire State of Mind (Medium)", "Titans Tread (Medium)"]
)

file_map = {
    "Seven Nation Army (Easy)": "seven_nation.json",
    "Empire State of Mind (Medium)": "empire_state.json",
    "Titans Tread (Medium)": "titans_tread.json",
}

# 2. Load Selected Track Data
json_path = f"data/{file_map[song_option]}"
with open(json_path, "r") as f:
    song_data = json.load(f)

# 3. Track Metadata
col1, col2, col3 = st.columns(3)
col1.metric("Track", song_data["title"])
col2.metric("Artist", song_data["artist"])
col3.metric("Tempo", f"{song_data['bpm']} BPM")

st.markdown("---")

# 4. SEPARATE BUTTON / PLAYER: Full Song Audio (Start to End)
st.subheader("🎧 1. Full Song Audio Player (Start to End)")
st.caption("Listen to the complete original audio track uninterrupted from start to finish.")

audio_url = song_data.get("audioUrl", "")
audio_path = Path(audio_url)
if audio_url.startswith(("http://", "https://")):
    st.audio(audio_url, format="audio/mp3")
elif audio_path.is_file():
    st.audio(str(audio_path), format="audio/mp3")
else:
    st.info("Audio file is not bundled. The full-length drum arrangement is available on the stage.")

st.markdown("---")

# 5. Interactive Visualizer Stage Controls
st.subheader("🥁 2. Interactive Drum Studio Stage")
st.caption("Click 'Play Studio Practice' inside the canvas below to sync the drum spotlights with the beat.")

render_drum_visualizer(song_data)

# 6. AI Practice Coach Sidebar
st.sidebar.markdown("---")
st.sidebar.header("🤖 AI Practice Coach")
if st.sidebar.button("Get Practice Advice"):
    with st.sidebar.spinner("Analyzing rhythm patterns..."):
        advice = get_ai_coach_advice(song_data)
        st.sidebar.info(advice)