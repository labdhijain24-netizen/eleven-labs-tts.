"""
ElevenLabs AI Text-to-Speech Studio
A Streamlit web application for hyper-realistic speech synthesis powered by ElevenLabs.
Deployable on Streamlit Community Cloud & GitHub.
"""

import os
import io
import time
from datetime import datetime
import streamlit as st
from dotenv import load_dotenv

# Load local environment variables if present
load_dotenv()

# Ensure the current directory is in sys.path so 'utils' can be imported regardless of execution directory
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app_utils.eleven_service import (
    validate_api_key,
    fetch_all_voices,
    generate_speech,
    DEFAULT_VOICES,
    AVAILABLE_MODELS,
    OUTPUT_FORMATS,
    SAMPLE_PROMPTS,
)

# ---------------------------------------------------------
# Page Configuration
# ---------------------------------------------------------
st.set_page_config(
    page_title="ElevenLabs TTS Studio",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------
# Custom Modern CSS Styling
# ---------------------------------------------------------
CUSTOM_CSS = """
<style>
/* Main theme overrides */
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
}

/* Glassmorphism Header Card */
.header-container {
    background: linear-gradient(135deg, rgba(99, 102, 241, 0.15) 0%, rgba(168, 85, 247, 0.15) 100%);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 18px;
    padding: 24px 28px;
    margin-bottom: 24px;
    backdrop-filter: blur(12px);
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.25);
}

.header-title {
    font-size: 2.1rem;
    font-weight: 800;
    background: linear-gradient(135deg, #A5B4FC 0%, #C084FC 50%, #F472B6 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0;
    display: flex;
    align-items: center;
    gap: 12px;
}

.header-subtitle {
    color: #94A3B8;
    font-size: 1.0rem;
    margin-top: 6px;
    margin-bottom: 0px;
}

/* Card Styling */
.custom-card {
    background: #1E293B;
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 14px;
    padding: 20px;
    margin-bottom: 18px;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
}

.badge {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.badge-primary {
    background: rgba(99, 102, 241, 0.2);
    color: #818CF8;
    border: 1px solid rgba(99, 102, 241, 0.4);
}

.badge-success {
    background: rgba(16, 185, 129, 0.2);
    color: #34D399;
    border: 1px solid rgba(16, 185, 129, 0.4);
}

.badge-warning {
    background: rgba(245, 158, 11, 0.2);
    color: #FBBF24;
    border: 1px solid rgba(245, 158, 11, 0.4);
}

/* Voice Card */
.voice-card {
    background: rgba(30, 41, 59, 0.7);
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 12px;
    padding: 14px;
    margin-bottom: 12px;
    transition: transform 0.15s ease, border-color 0.15s ease;
}

.voice-card:hover {
    border-color: rgba(99, 102, 241, 0.5);
    transform: translateY(-2px);
}

.voice-name {
    font-size: 1.05rem;
    font-weight: 700;
    color: #F8FAFC;
    margin-bottom: 4px;
}

.voice-meta {
    font-size: 0.8rem;
    color: #94A3B8;
}

/* Audio Player Container */
.audio-result-box {
    background: linear-gradient(135deg, rgba(30, 41, 59, 0.9) 0%, rgba(15, 23, 42, 0.95) 100%);
    border: 1px solid rgba(99, 102, 241, 0.3);
    border-radius: 16px;
    padding: 24px;
    margin-top: 16px;
    margin-bottom: 20px;
    box-shadow: 0 10px 25px -5px rgba(99, 102, 241, 0.15);
}

/* Character counter */
.char-counter {
    font-size: 0.82rem;
    color: #94A3B8;
    text-align: right;
    margin-top: -12px;
    margin-bottom: 12px;
}

/* Buttons */
.stButton > button {
    border-radius: 10px;
    font-weight: 600;
    transition: all 0.2s ease;
}

.stButton > button:hover {
    box-shadow: 0 4px 14px rgba(99, 102, 241, 0.4);
    transform: translateY(-1px);
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# ---------------------------------------------------------
# Session State Initialization
# ---------------------------------------------------------
if "history" not in st.session_state:
    st.session_state.history = []

if "api_key" not in st.session_state:
    # Priority: Streamlit secrets -> .env / environment variable -> empty
    secret_key = ""
    try:
        secret_key = st.secrets.get("ELEVENLABS_API_KEY", "")
    except Exception:
        pass
    if not secret_key:
        secret_key = os.getenv("ELEVENLABS_API_KEY", "")
    st.session_state.api_key = secret_key

if "validated" not in st.session_state:
    st.session_state.validated = False

if "account_info" not in st.session_state:
    st.session_state.account_info = None

if "voices" not in st.session_state:
    st.session_state.voices = DEFAULT_VOICES


# ---------------------------------------------------------
# Sidebar: API Key, Account Quota & Navigation
# ---------------------------------------------------------
with st.sidebar:
    st.image(
        "https://elevenlabs.io/favicon.ico",
        width=42,
    )
    st.title("Settings & API")

    # API Key Input
    api_key_input = st.text_input(
        "ElevenLabs API Key",
        value=st.session_state.api_key,
        type="password",
        help="Paste your API key from https://elevenlabs.io/app/settings/api-keys",
        placeholder="sk_...",
    )

    col_btn1, col_btn2 = st.columns([1, 1])
    with col_btn1:
        verify_clicked = st.button("🔌 Verify Key", use_container_width=True)
    with col_btn2:
        clear_clicked = st.button("🧹 Clear Key", use_container_width=True)

    if clear_clicked:
        st.session_state.api_key = ""
        st.session_state.validated = False
        st.session_state.account_info = None
        st.session_state.voices = DEFAULT_VOICES
        st.rerun()

    # Automatically verify on initial load if secret key exists
    if api_key_input and (verify_clicked or (st.session_state.api_key and not st.session_state.validated)):
        st.session_state.api_key = api_key_input.strip()
        with st.spinner("Validating with ElevenLabs..."):
            valid, msg, info = validate_api_key(st.session_state.api_key)
            if valid:
                st.session_state.validated = True
                st.session_state.account_info = info
                # Fetch account-specific voices
                voices = fetch_all_voices(st.session_state.api_key)
                st.session_state.voices = voices
                st.success("API Key authenticated!")
            else:
                st.session_state.validated = False
                st.session_state.account_info = None
                st.error(f"Error: {msg}")

    # Display API Connection Status Card
    if st.session_state.validated and st.session_state.account_info:
        acc = st.session_state.account_info
        used = acc.get("character_count", 0)
        limit = acc.get("character_limit", 10000)
        tier = acc.get("tier", "Free").title()
        pct = min(100, int((used / limit) * 100)) if limit > 0 else 0

        st.markdown(
            f"""
            <div class="custom-card" style="padding: 14px; margin-top: 14px;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                    <span style="font-weight: 700; color: #F8FAFC;">Plan: {tier}</span>
                    <span class="badge badge-success">Active</span>
                </div>
                <div style="font-size: 0.8rem; color: #94A3B8; margin-bottom: 6px;">
                    Usage: <b>{used:,}</b> / <b>{limit:,}</b> chars ({pct}%)
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.progress(pct / 100.0)
    else:
        st.markdown(
            """
            <div class="custom-card" style="padding: 14px; margin-top: 14px; border-color: rgba(245, 158, 11, 0.3);">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                    <span style="font-weight: 600; color: #FBBF24;">🔑 API Key Required</span>
                    <span class="badge badge-warning">Demo Mode</span>
                </div>
                <p style="font-size: 0.8rem; color: #94A3B8; margin: 0;">
                    Audio generation requires an ElevenLabs API key.
                    <a href="https://elevenlabs.io/app/sign-up" target="_blank" style="color: #818CF8;">Get a free key here</a>.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.divider()

    # Useful Resource Links
    st.markdown("### 📚 Quick Links")
    st.markdown("- [ElevenLabs Dashboard](https://elevenlabs.io)")
    st.markdown("- [Get ElevenLabs API Key](https://elevenlabs.io/app/settings/api-keys)")
    st.markdown("- [API Documentation](https://elevenlabs.io/docs)")
    st.markdown("- [Streamlit Documentation](https://docs.streamlit.io)")

    st.divider()
    if st.button("🗑️ Clear Generation History", use_container_width=True):
        st.session_state.history = []
        st.toast("History cleared!", icon="🧹")


# ---------------------------------------------------------
# Main Page Header
# ---------------------------------------------------------
st.markdown(
    """
    <div class="header-container">
        <h1 class="header-title">
            <span>🎙️ ElevenLabs TTS Studio</span>
            <span class="badge badge-primary">v2.5 AI Speech</span>
        </h1>
        <p class="header-subtitle">
            Generate lifelike, emotionally rich, studio-quality speech with ElevenLabs' cutting-edge neural voice models.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------
# Main Tabs: Generator, Voice Library, History, Deployment Guide
# ---------------------------------------------------------
tab_generator, tab_voices, tab_history, tab_deploy = st.tabs([
    "✨ Generate Speech",
    "🎧 Voice Library",
    "🕒 Generation History",
    "🚀 GitHub & Streamlit Deploy Guide",
])


# =========================================================
# TAB 1: GENERATE SPEECH
# =========================================================
with tab_generator:
    col_input, col_config = st.columns([1.5, 1.0], gap="large")

    with col_input:
        st.markdown("### ✍️ Text Input")

        # Preset Prompts Dropdown
        selected_preset = st.selectbox(
            "Load a Sample Prompt (optional):",
            ["Custom Text (Write your own)"] + list(SAMPLE_PROMPTS.keys()),
            help="Choose a pre-written prompt or type your custom script below.",
        )

        initial_text = ""
        if selected_preset != "Custom Text (Write your own)":
            initial_text = SAMPLE_PROMPTS[selected_preset]
        else:
            initial_text = (
                "Artificial intelligence is transforming how stories are told and experienced. "
                "With ElevenLabs, every syllable carries emotion, cadence, and human warmth."
            )

        text_prompt = st.text_area(
            "Script to Synthesize",
            value=initial_text,
            height=210,
            placeholder="Type or paste the text you want the voice to read out loud...",
            help="Supports punctuation, natural pauses, commas, exclamation marks, and questions.",
        )

        char_len = len(text_prompt)
        st.markdown(f'<div class="char-counter">Character count: <b>{char_len}</b> chars</div>', unsafe_allow_html=True)

        # Quick Preset Buttons
        st.markdown("<p style='font-size:0.85rem; color:#94A3B8; margin-bottom: 6px;'>Quick templates:</p>", unsafe_allow_html=True)
        col_t1, col_t2, col_t3 = st.columns(3)
        with col_t1:
            if st.button("🎙️ Storytelling", use_container_width=True):
                st.session_state["_quick_text"] = SAMPLE_PROMPTS["Storytelling"]
                st.rerun()
        with col_t2:
            if st.button("📢 Commercial Ad", use_container_width=True):
                st.session_state["_quick_text"] = SAMPLE_PROMPTS["Commercial Ad"]
                st.rerun()
        with col_t3:
            if st.button("🚀 Tech Demo", use_container_width=True):
                st.session_state["_quick_text"] = SAMPLE_PROMPTS["Tech Product Demo"]
                st.rerun()

    with col_config:
        st.markdown("### 🎛️ Voice & Model Controls")

        # Voice Selector
        voice_options = {
            f"{v['name']} ({(v.get('labels') or {}).get('accent', 'Neutral').title()} • {(v.get('labels') or {}).get('gender', 'Voice').title()})": v["voice_id"]
            for v in st.session_state.voices
        }
        selected_voice_label = st.selectbox(
            "Select Voice",
            options=list(voice_options.keys()),
            index=0,
            help="Choose from ElevenLabs premade or custom voices in your library.",
        )
        selected_voice_id = voice_options[selected_voice_label]

        # Model Selector
        model_options = {f"{m['name']} — {m['badge']}": m["id"] for m in AVAILABLE_MODELS}
        selected_model_label = st.selectbox(
            "Neural Model",
            options=list(model_options.keys()),
            index=0,
            help="Select the AI architecture. Eleven Multilingual v2 offers the highest realism.",
        )
        selected_model_id = model_options[selected_model_label]

        # Output Audio Format Selector
        format_options = {meta["label"]: key for key, meta in OUTPUT_FORMATS.items()}
        selected_format_label = st.selectbox(
            "Output Quality & Format",
            options=list(format_options.keys()),
            index=0,
            help="Select the audio bitrate or uncompressed PCM/WAV format.",
        )
        selected_format_id = format_options[selected_format_label]

        # Advanced Voice Settings Expander
        with st.expander("⚙️ Fine-Tune Voice Settings (Sliders)", expanded=False):
            stability = st.slider(
                "Stability",
                min_value=0.0,
                max_value=1.0,
                value=0.5,
                step=0.05,
                help="Higher values make speech more consistent; lower values make it more emotionally variable.",
            )
            similarity = st.slider(
                "Clarity + Similarity Boost",
                min_value=0.0,
                max_value=1.0,
                value=0.75,
                step=0.05,
                help="Enhances resemblance to original voice and reduces artifacts.",
            )
            style = st.slider(
                "Style Exaggeration",
                min_value=0.0,
                max_value=1.0,
                value=0.0,
                step=0.05,
                help="Amplifies stylistic emotion (recommended 0.0 - 0.2 for natural speech).",
            )
            speed = st.slider(
                "Speed Multiplier",
                min_value=0.7,
                max_value=1.5,
                value=1.0,
                step=0.05,
                help="Controls speech rate (1.0 = normal pacing).",
            )
            speaker_boost = st.checkbox(
                "Enable Speaker Boost",
                value=True,
                help="Boosts voice similarity to the target speaker.",
            )

    st.markdown("<hr style='margin: 16px 0; border-color: rgba(255,255,255,0.08);'>", unsafe_allow_html=True)

    # Big Action Button
    generate_btn = st.button(
        "🚀 Generate High-Fidelity Audio",
        type="primary",
        use_container_width=True,
        help="Synthesizes the text using the selected voice and ElevenLabs model.",
    )

    if generate_btn:
        active_key = (st.session_state.api_key or "").strip()

        if not active_key:
            st.error("🔑 Please enter your ElevenLabs API Key in the sidebar to generate speech.")
        elif not text_prompt.strip():
            st.warning("⚠️ Please provide some text to convert to speech.")
        else:
            with st.spinner("Synthesizing audio with ElevenLabs..."):
                start_time = time.time()
                try:
                    audio_bytes, mime_type, file_ext = generate_speech(
                        api_key=active_key,
                        text=text_prompt.strip(),
                        voice_id=selected_voice_id,
                        model_id=selected_model_id,
                        stability=stability,
                        similarity_boost=similarity,
                        style=style,
                        use_speaker_boost=speaker_boost,
                        speed=speed,
                        output_format=selected_format_id,
                    )
                    latency = time.time() - start_time
                    kb_size = len(audio_bytes) / 1024.0

                    voice_name_clean = selected_voice_label.split(" (")[0]
                    timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    file_name = f"elevenlabs_{voice_name_clean.lower()}_{int(time.time())}.{file_ext}"

                    # Store in generation history
                    gen_entry = {
                        "timestamp": timestamp_str,
                        "voice_name": voice_name_clean,
                        "model_id": selected_model_id,
                        "text": text_prompt,
                        "audio_bytes": audio_bytes,
                        "mime": mime_type,
                        "filename": file_name,
                        "size_kb": kb_size,
                        "latency": latency,
                    }
                    st.session_state.history.insert(0, gen_entry)

                    # Update account info quota
                    if st.session_state.account_info:
                        st.session_state.account_info["character_count"] += len(text_prompt)

                    # Audio Player Display Card
                    st.markdown(
                        f"""
                        <div class="audio-result-box">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                                <div>
                                    <span style="font-size: 1.15rem; font-weight: 700; color: #F8FAFC;">🎧 Generated Speech</span>
                                    <span style="color: #94A3B8; font-size: 0.85rem; margin-left: 8px;">— Voice: <b>{voice_name_clean}</b></span>
                                </div>
                                <div>
                                    <span class="badge badge-primary">{latency:.2f}s latency</span>
                                    <span class="badge badge-success">{kb_size:.1f} KB</span>
                                </div>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                    st.audio(audio_bytes, format=mime_type)

                    col_dl, col_space = st.columns([1, 2])
                    with col_dl:
                        st.download_button(
                            label=f"📥 Download Audio ({file_ext.upper()})",
                            data=audio_bytes,
                            file_name=file_name,
                            mime=mime_type,
                            use_container_width=True,
                        )

                    st.success(f"Generated successfully in {latency:.2f} seconds!")

                except PermissionError as pe:
                    st.error(f"Authentication Error: {str(pe)}")
                    st.info("Tip: Double-check that your API key is copied correctly from https://elevenlabs.io/app/settings/api-keys")
                except RuntimeError as re:
                    st.error(f"Generation Failed: {str(re)}")
                except Exception as ex:
                    st.error(f"Unexpected error: {str(ex)}")


# =========================================================
# TAB 2: VOICE LIBRARY EXPLORER
# =========================================================
with tab_voices:
    st.markdown("### 🎧 Explore Voices")
    st.markdown(
        "Preview samples and discover voices for narration, commercials, video games, and audiobooks."
    )

    # Search filter
    search_query = st.text_input(
        "🔍 Search voices by name, accent, or use-case:",
        placeholder="e.g. Rachel, American, Storytelling, British...",
    ).strip().lower()

    filtered_voices = [
        v for v in st.session_state.voices
        if (
            search_query in v["name"].lower()
            or search_query in v.get("description", "").lower()
            or search_query in str(v.get("labels", {})).lower()
        )
    ]

    st.markdown(f"Showing **{len(filtered_voices)}** of **{len(st.session_state.voices)}** voices:")

    cols = st.columns(2)
    for idx, voice in enumerate(filtered_voices):
        col = cols[idx % 2]
        with col:
            labels = voice.get("labels") or {}
            gender = labels.get("gender", "Voice").title()
            accent = labels.get("accent", "").title()
            use_case = labels.get("use_case", "").title()
            desc = voice.get("description", "ElevenLabs neural voice model.")

            preview_url = voice.get("preview_url")

            with st.container():
                st.markdown(
                    f"""
                    <div class="voice-card">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <span class="voice-name">{voice['name']}</span>
                            <span class="badge badge-primary">{voice.get('category', 'premade')}</span>
                        </div>
                        <div class="voice-meta">
                            {f'<span>🏷️ {gender}</span> • ' if gender else ''}
                            {f'<span>🌍 {accent}</span> • ' if accent else ''}
                            {f'<span>🎯 {use_case}</span>' if use_case else ''}
                        </div>
                        <p style="font-size: 0.85rem; color: #CBD5E1; margin: 8px 0 10px 0;">
                            {desc}
                        </p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                if preview_url:
                    st.audio(preview_url)
                st.caption(f"Voice ID: `{voice['voice_id']}`")
                st.divider()


# =========================================================
# TAB 3: GENERATION HISTORY
# =========================================================
with tab_history:
    st.markdown("### 🕒 Recent Generations")
    st.markdown("Review and download audio clips generated during this session.")

    if not st.session_state.history:
        st.info("No audio generated yet in this session. Create your first clip in the **Generate Speech** tab!")
    else:
        for idx, item in enumerate(st.session_state.history):
            with st.expander(f"🎵 Take #{len(st.session_state.history) - idx} — {item['voice_name']} ({item['timestamp']})", expanded=(idx == 0)):
                st.markdown(f"**Prompt text:**")
                st.write(item["text"])

                st.markdown(
                    f"""
                    <div style="display:flex; gap: 10px; margin: 8px 0;">
                        <span class="badge badge-primary">Model: {item['model_id']}</span>
                        <span class="badge badge-success">{item['size_kb']:.1f} KB</span>
                        <span class="badge badge-warning">{item['latency']:.2f}s generation</span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                st.audio(item["audio_bytes"], format=item["mime"])

                st.download_button(
                    label=f"📥 Download {item['filename']}",
                    data=item["audio_bytes"],
                    file_name=item["filename"],
                    mime=item["mime"],
                    key=f"dl_history_{idx}",
                )


# =========================================================
# TAB 4: GITHUB & STREAMLIT CLOUD DEPLOYMENT GUIDE
# =========================================================
with tab_deploy:
    st.markdown("### 🚀 How to Upload to GitHub and Deploy to Streamlit Cloud")

    col_gh, col_st = st.columns(2, gap="large")

    with col_gh:
        st.markdown("#### 1. Push Code to GitHub")
        st.markdown(
            """
            Open your terminal in this project directory and run:
            """
        )
        st.code(
            """# 1. Initialize git repository
git init

# 2. Stage all files (respects .gitignore)
git add .

# 3. Create your initial commit
git commit -m "feat: initial commit of ElevenLabs TTS Streamlit app"

# 4. Rename default branch to main
git branch -M main

# 5. Link to your new GitHub repository (replace with your repo URL)
git remote add origin https://github.com/YOUR_USERNAME/elevenlabs-tts-studio.git

# 6. Push code to GitHub
git push -u origin main""",
            language="bash",
        )

    with col_st:
        st.markdown("#### 2. Deploy on Streamlit Community Cloud")
        st.markdown(
            """
            1. Visit **[share.streamlit.io](https://share.streamlit.io/)** and sign in with GitHub.
            2. Click **New app**.
            3. Select your repository: `YOUR_USERNAME/elevenlabs-tts-studio`.
            4. Branch: `main`.
            5. Main file path: `app.py`.
            6. Click **Advanced Settings** -> **Secrets**.
            7. Paste your ElevenLabs key into the secrets box:
            """
        )
        st.code(
            """ELEVENLABS_API_KEY = "your_actual_elevenlabs_api_key_here" """,
            language="toml",
        )
        st.markdown(
            """
            8. Click **Deploy!** Your app will be live with a public URL in 1–2 minutes! 🎉
            """
        )

    st.markdown("<hr style='margin: 20px 0; border-color: rgba(255,255,255,0.08);'>", unsafe_allow_html=True)
    st.markdown("#### 🔒 Security Note")
    st.info(
        "Never commit your real ElevenLabs API key into GitHub. The included `.gitignore` already protects `.env` and `.streamlit/secrets.toml`. "
        "Use Streamlit Secrets or provide the key through the sidebar."
    )
