# 🎙️ ElevenLabs AI Text-to-Speech Studio

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io)
[![Python Version](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.14-blue.svg)](https://www.python.org/)
[![ElevenLabs API](https://img.shields.io/badge/ElevenLabs-API%20v2.5-purple.svg)](https://elevenlabs.io)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A modern, high-fidelity **Text-to-Speech (TTS) Web Application** built with **Streamlit** and the official **ElevenLabs API**. Convert any written text or story into lifelike, emotionally nuanced speech across dozens of languages and voices.

Designed to be uploaded to **GitHub** and deployed directly to **Streamlit Community Cloud** with zero configuration headaches.

---

## ✨ Features

- 🔊 **Studio-Quality Voice Synthesis**: Powered by ElevenLabs' `eleven_multilingual_v2` and ultra-low latency `eleven_flash_v2_5` models.
- 🎧 **Interactive Voice Library**: Browse and preview premade voices (Rachel, Adam, Antoni, Bella, Charlie, George, etc.) or your custom cloned voices.
- 🎛️ **Granular Voice Tuning**:
  - Stability slider
  - Clarity & Similarity Boost
  - Style Exaggeration
  - Speech Speed Multiplier (0.7x – 1.5x)
  - Speaker Boost toggle
- 🎼 **Multiple Audio Output Formats**:
  - MP3 (128 kbps, 192 kbps studio quality, 64 kbps, 32 kbps)
  - PCM / WAV (16 kHz, 24 kHz, 44.1 kHz lossless)
- 📝 **Sample Prompt Library**: Instant one-click presets for storytelling, tech product demos, commercials, news anchors, and motivational speeches.
- 🕒 **Session History**: Track, re-listen, and download any generated audio clip during your session.
- 📊 **Live Account Quota Monitoring**: See your active ElevenLabs plan tier (Free / Starter / Creator) and character count consumption.
- 🔒 **Flexible & Secure Secrets Handling**: Enter your API key via the web interface, local `.env`, or `.streamlit/secrets.toml` without ever risking your credentials on Git.

---

## 📁 Repository Structure

```
elevenlabs-tts-studio/
├── .streamlit/
│   ├── config.toml               # Streamlit theme & server configuration
│   └── secrets.toml.example      # Template for Streamlit secrets
├── utils/
│   ├── __init__.py
│   └── eleven_service.py         # ElevenLabs API client & fallback services
├── .env.example                  # Environment variable template
├── .gitignore                    # Git ignore file protecting keys & temp files
├── app.py                        # Main Streamlit application
├── requirements.txt              # Production dependencies for pip & Streamlit Cloud
└── README.md                     # Documentation & setup guide
```

---

## 🚀 Quick Start (Local Setup)

### 1. Clone or Open the Project
```bash
cd "eleven labs"
```

### 2. Create a Virtual Environment (Recommended)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Your ElevenLabs API Key
You can obtain a free API key at [ElevenLabs](https://elevenlabs.io/app/settings/api-keys).

Choose **one** of the following options:

- **Option A (Streamlit Secrets)**:
  Copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml` and add your key:
  ```toml
  ELEVENLABS_API_KEY = "your_actual_elevenlabs_api_key_here"
  ```

- **Option B (.env file)**:
  Copy `.env.example` to `.env` and add:
  ```env
  ELEVENLABS_API_KEY=your_actual_elevenlabs_api_key_here
  ```

- **Option C (In the App)**:
  Simply paste your API key in the sidebar when the app starts.

### 5. Launch the Streamlit App
```bash
streamlit run app.py
```
Your default browser will open automatically at `http://localhost:8501`.

---

## 📤 How to Upload to GitHub

Follow these steps to push this project to your GitHub account:

1. **Initialize Git** in the project directory:
   ```bash
   git init
   ```

2. **Stage files and commit**:
   ```bash
   git add .
   git commit -m "feat: initial commit of ElevenLabs TTS Streamlit app"
   ```

3. **Rename default branch to `main`**:
   ```bash
   git branch -M main
   ```

4. **Create a new repository on GitHub**:
   - Go to [GitHub New Repository](https://github.com/new).
   - Name it `elevenlabs-tts-studio`.
   - Do **NOT** initialize with a README or .gitignore (we already have them).

5. **Link and push**:
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/elevenlabs-tts-studio.git
   git push -u origin main
   ```

*(Note: The provided `.gitignore` automatically prevents your `.env` and `.streamlit/secrets.toml` files from being committed.)*

---

## 🌐 How to Deploy to Streamlit Community Cloud (Free)

Deploy your application publicly in under 2 minutes:

1. Visit **[share.streamlit.io](https://share.streamlit.io/)** and sign in with your GitHub account.
2. Click the **"New app"** button.
3. Configure the deployment settings:
   - **Repository**: `YOUR_USERNAME/elevenlabs-tts-studio`
   - **Branch**: `main`
   - **Main file path**: `app.py`
4. Expand **Advanced settings** and click **Secrets**:
   Add your ElevenLabs API Key:
   ```toml
   ELEVENLABS_API_KEY = "your_actual_elevenlabs_api_key_here"
   ```
5. Click **Deploy!**
6. Streamlit Cloud will automatically install `requirements.txt` and launch your live application with a public sharing link! 🎉

---

## 🛠️ Supported ElevenLabs Models

| Model | Code | Description |
|---|---|---|
| **Eleven Multilingual v2** | `eleven_multilingual_v2` | Best quality and emotional nuance across 29 languages. |
| **Eleven Flash v2.5** | `eleven_flash_v2_5` | Ultra-low latency (~75ms) model for real-time applications. |
| **Eleven Turbo v2.5** | `eleven_turbo_v2_5` | High quality with fast generation speed. |
| **Eleven Monolingual v1** | `eleven_monolingual_v1` | Classic English narration model. |

---

## ❓ Troubleshooting & FAQ

#### 1. "Invalid API Key" or 401 Unauthorized Error
- Verify that your key was copied completely from [ElevenLabs API Keys](https://elevenlabs.io/app/settings/api-keys).
- Ensure no accidental trailing spaces were included.

#### 2. "Character quota exceeded" or 429 Error
- The free ElevenLabs plan provides 10,000 characters per month. Check your remaining quota in the app's sidebar or on your ElevenLabs dashboard.

#### 3. Secrets Not Loading on Streamlit Cloud
- Make sure the secret key name is exactly `ELEVENLABS_API_KEY` (all uppercase) in the Streamlit Cloud Dashboard under **Settings > Secrets**.

---

## 📜 License

This project is licensed under the **MIT License**. Feel free to customize and integrate it into your own commercial or open-source projects.
