"""
ElevenLabs API Service Module
Handles authentication, voice retrieval, speech synthesis, and account details.
"""

from typing import List, Dict, Any, Tuple, Optional
import os
import requests
from elevenlabs.client import ElevenLabs
from elevenlabs import VoiceSettings
from elevenlabs.core.api_error import ApiError


# Curated list of high-quality standard ElevenLabs voices for offline/preview fallback
DEFAULT_VOICES: List[Dict[str, Any]] = [
    {
        "voice_id": "21m00Tcm4TlvDq8ikWAM",
        "name": "Rachel",
        "category": "premade",
        "description": "Calm, warm, articulate American female. Perfect for narration and audiobooks.",
        "labels": {"gender": "female", "accent": "american", "age": "young", "use_case": "narration"},
        "preview_url": "https://storage.googleapis.com/eleven-public-prod/premade/voices/21m00Tcm4TlvDq8ikWAM/df6788f9-196e-47de-a315-50801160913d.mp3",
    },
    {
        "voice_id": "pNInz6obpgDQGcFmaJgB",
        "name": "Adam",
        "category": "premade",
        "description": "Deep, confident, engaging American male voice. Ideal for deep narration & ads.",
        "labels": {"gender": "male", "accent": "american", "age": "middle-aged", "use_case": "narration"},
        "preview_url": "https://storage.googleapis.com/eleven-public-prod/premade/voices/pNInz6obpgDQGcFmaJgB/6734d75e-5fd8-45ee-9043-73aa0d0bb2c6.mp3",
    },
    {
        "voice_id": "EXAVITQu4vr4xnSDxMaL",
        "name": "Bella",
        "category": "premade",
        "description": "Soft, expressive, emotional young American female voice.",
        "labels": {"gender": "female", "accent": "american", "age": "young", "use_case": "expressive"},
        "preview_url": "https://storage.googleapis.com/eleven-public-prod/premade/voices/EXAVITQu4vr4xnSDxMaL/01d5ee4a-6213-44f2-959c-6a3f651fb023.mp3",
    },
    {
        "voice_id": "ErXwobaYiN019PkySvjV",
        "name": "Antoni",
        "category": "premade",
        "description": "Balanced, versatile, well-rounded American male voice.",
        "labels": {"gender": "male", "accent": "american", "age": "young", "use_case": "narration"},
        "preview_url": "https://storage.googleapis.com/eleven-public-prod/premade/voices/ErXwobaYiN019PkySvjV/38d8f8f0-0b3f-4653-8222-4b1c5fa90591.mp3",
    },
    {
        "voice_id": "IKne3meq5aSn9XLyUdCD",
        "name": "Charlie",
        "category": "premade",
        "description": "Casual, natural Australian male voice. Great for friendly conversations.",
        "labels": {"gender": "male", "accent": "australian", "age": "middle-aged", "use_case": "conversational"},
        "preview_url": "https://storage.googleapis.com/eleven-public-prod/premade/voices/IKne3meq5aSn9XLyUdCD/102de6f2-22ed-410e-939a-aa7b600802b0.mp3",
    },
    {
        "voice_id": "JBFqnCBsd6RMkjVDRZzb",
        "name": "George",
        "category": "premade",
        "description": "Warm, captivating British male voice. Classic British storyteller accent.",
        "labels": {"gender": "male", "accent": "british", "age": "middle-aged", "use_case": "storytelling"},
        "preview_url": "https://storage.googleapis.com/eleven-public-prod/premade/voices/JBFqnCBsd6RMkjVDRZzb/e6206d1a-0721-47bc-8025-1b8fa0b74102.mp3",
    },
    {
        "voice_id": "Xb7hH8MSUJpSbSDYk0k2",
        "name": "Alice",
        "category": "premade",
        "description": "Clear, confident British female voice. Perfect for news & corporate presentations.",
        "labels": {"gender": "female", "accent": "british", "age": "middle-aged", "use_case": "news"},
        "preview_url": "https://storage.googleapis.com/eleven-public-prod/premade/voices/Xb7hH8MSUJpSbSDYk0k2/d10f7534-11f6-41fe-a012-2de1e466d313.mp3",
    },
    {
        "voice_id": "TxGEqnHWrfWFTfGW9XjX",
        "name": "Josh",
        "category": "premade",
        "description": "Deep, resonant, relaxed American male voice. Excellent for video voiceovers.",
        "labels": {"gender": "male", "accent": "american", "age": "young", "use_case": "narration"},
        "preview_url": "https://storage.googleapis.com/eleven-public-prod/premade/voices/TxGEqnHWrfWFTfGW9XjX/33866a1c-3b4e-4f54-b52e-0a562095f32a.mp3",
    },
    {
        "voice_id": "MF3mGyEYCl7XYWbV9V6O",
        "name": "Elli",
        "category": "premade",
        "description": "Emotional, expressive young American female voice.",
        "labels": {"gender": "female", "accent": "american", "age": "young", "use_case": "expressive"},
        "preview_url": "https://storage.googleapis.com/eleven-public-prod/premade/voices/MF3mGyEYCl7XYWbV9V6O/29e47522-6ab5-4937-97fe-ee4fb0e260e8.mp3",
    },
    {
        "voice_id": "yoZ06aMxZJJ28mfd3POQ",
        "name": "Sam",
        "category": "premade",
        "description": "Dynamic, raspy, energetic American male voice.",
        "labels": {"gender": "male", "accent": "american", "age": "young", "use_case": "dynamic"},
        "preview_url": "https://storage.googleapis.com/eleven-public-prod/premade/voices/yoZ06aMxZJJ28mfd3POQ/1c4d417c-834c-42e9-bc66-ae5604b36077.mp3",
    },
]

AVAILABLE_MODELS = [
    {
        "id": "eleven_multilingual_v2",
        "name": "Eleven Multilingual v2",
        "badge": "Highest Quality",
        "description": "State-of-the-art emotional depth & natural pauses across 29 languages.",
    },
    {
        "id": "eleven_flash_v2_5",
        "name": "Eleven Flash v2.5",
        "badge": "Fastest (~75ms)",
        "description": "Ultra-low latency model optimized for interactive real-time apps in 32 languages.",
    },
    {
        "id": "eleven_turbo_v2_5",
        "name": "Eleven Turbo v2.5",
        "badge": "Speed & Quality",
        "description": "High quality with low latency across 32 languages.",
    },
    {
        "id": "eleven_monolingual_v1",
        "name": "Eleven Monolingual v1",
        "badge": "English Classic",
        "description": "The classic groundbreaking model for standard English speech synthesis.",
    },
]

OUTPUT_FORMATS = {
    "mp3_44100_128": {"label": "MP3 • 44.1 kHz, 128 kbps (Standard)", "mime": "audio/mp3", "ext": "mp3"},
    "mp3_44100_192": {"label": "MP3 • 44.1 kHz, 192 kbps (Studio Quality)", "mime": "audio/mp3", "ext": "mp3"},
    "mp3_44100_64": {"label": "MP3 • 44.1 kHz, 64 kbps (Fast / Compact)", "mime": "audio/mp3", "ext": "mp3"},
    "mp3_22050_32": {"label": "MP3 • 22.05 kHz, 32 kbps (Ultra Light)", "mime": "audio/mp3", "ext": "mp3"},
    "pcm_16000": {"label": "PCM / WAV • 16 kHz (Raw telephony/speech)", "mime": "audio/wav", "ext": "wav"},
    "pcm_24000": {"label": "PCM / WAV • 24 kHz (Broadcast standard)", "mime": "audio/wav", "ext": "wav"},
    "pcm_44100": {"label": "PCM / WAV • 44.1 kHz (Lossless uncompressed)", "mime": "audio/wav", "ext": "wav"},
}


SAMPLE_PROMPTS = {
    "Storytelling": (
        "The old lighthouse had stood upon the cliff for more than a hundred years, "
        "defying every tempest the Atlantic dared to summon. Tonight, as the sea churned into silver foam, "
        "its golden beam cut through the darkness with unwavering resolve."
    ),
    "Tech Product Demo": (
        "Welcome to the next chapter of synthetic audio. With ElevenLabs, developers and creators "
        "can produce cinematic voiceovers with pinpoint emotional nuance and lifelike cadence, in over 29 languages."
    ),
    "Commercial Ad": (
        "Are you ready to elevate your creative workflow? Meet the all-new cloud workspace designed "
        "for high-velocity teams. Fast, collaborative, and shockingly intuitive. Start your free trial today."
    ),
    "Motivational Quote": (
        "Every great journey begins not with a bold declaration, but with a quiet decision to take one single step. "
        "Trust the discipline over the mood, and let your consistency speak for itself."
    ),
    "News Anchor": (
        "Good evening. Astronomers announced a historic discovery today after detecting repeating atmospheric "
        "signals from an exoplanet situated forty light-years away in the constellation Aquarius."
    ),
}


def get_client(api_key: str) -> ElevenLabs:
    """Initialize an ElevenLabs client instance."""
    return ElevenLabs(api_key=api_key.strip())


def validate_api_key(api_key: str) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
    """
    Validate the ElevenLabs API key and fetch subscription / quota metrics.
    Returns: (is_valid, message, account_info)
    """
    if not api_key or not api_key.strip():
        return False, "API key is empty.", None

    clean_key = api_key.strip()
    try:
        client = get_client(clean_key)
        # Fetch subscription info
        sub = client.user.subscription.get()
        user = client.user.get()

        info = {
            "tier": getattr(sub, "tier", "Unknown"),
            "character_count": getattr(sub, "character_count", 0),
            "character_limit": getattr(sub, "character_limit", 10000),
            "status": getattr(sub, "status", "active"),
            "first_name": getattr(user, "first_name", "") or "",
        }
        return True, "API Key is valid and active!", info

    except ApiError as e:
        status_code = getattr(e, "status_code", None)
        body = getattr(e, "body", str(e))
        if status_code == 401 or "invalid_api_key" in str(body).lower():
            return False, "Invalid ElevenLabs API Key. Please verify your credentials.", None
        return False, f"API Error ({status_code}): {body}", None
    except Exception as ex:
        # Fallback to direct HTTP check in case SDK raises networking error
        try:
            resp = requests.get(
                "https://api.elevenlabs.io/v1/user/subscription",
                headers={"xi-api-key": clean_key},
                timeout=10,
            )
            if resp.status_code == 200:
                data = resp.json()
                return True, "API Key is valid!", {
                    "tier": data.get("tier", "Unknown"),
                    "character_count": data.get("character_count", 0),
                    "character_limit": data.get("character_limit", 10000),
                    "status": data.get("status", "active"),
                    "first_name": "",
                }
            elif resp.status_code == 401:
                return False, "Invalid ElevenLabs API Key (401 Unauthorized).", None
            else:
                return False, f"Verification failed with status code {resp.status_code}: {resp.text}", None
        except Exception as req_ex:
            return False, f"Connection failed: {str(req_ex)}", None


def fetch_all_voices(api_key: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Fetch voices from ElevenLabs API if key is available.
    Falls back cleanly to DEFAULT_VOICES if no key or on error.
    """
    if not api_key or not api_key.strip():
        return DEFAULT_VOICES

    try:
        client = get_client(api_key)
        response = client.voices.get_all()
        voices_list = []

        for v in response.voices:
            labels_dict = getattr(v, "labels", {}) or {}
            preview = getattr(v, "preview_url", None)
            desc = getattr(v, "description", None) or f"{labels_dict.get('gender', '')} {labels_dict.get('accent', '')} voice".strip()

            voices_list.append({
                "voice_id": v.voice_id,
                "name": v.name,
                "category": getattr(v, "category", "premade"),
                "description": desc or "Custom or community ElevenLabs voice",
                "labels": labels_dict,
                "preview_url": preview,
            })

        if voices_list:
            return voices_list
        return DEFAULT_VOICES

    except Exception:
        # HTTP fallback
        try:
            resp = requests.get(
                "https://api.elevenlabs.io/v1/voices",
                headers={"xi-api-key": api_key.strip()},
                timeout=10,
            )
            if resp.status_code == 200:
                data = resp.json()
                raw_voices = data.get("voices", [])
                result = []
                for v in raw_voices:
                    result.append({
                        "voice_id": v.get("voice_id"),
                        "name": v.get("name"),
                        "category": v.get("category") or "premade",
                        "description": v.get("description") or "",
                        "labels": v.get("labels") or {},
                        "preview_url": v.get("preview_url"),
                    })
                if result:
                    return result
        except Exception:
            pass

        return DEFAULT_VOICES


def generate_speech(
    api_key: str,
    text: str,
    voice_id: str,
    model_id: str = "eleven_multilingual_v2",
    stability: float = 0.5,
    similarity_boost: float = 0.75,
    style: float = 0.0,
    use_speaker_boost: bool = True,
    speed: float = 1.0,
    output_format: str = "mp3_44100_128",
) -> Tuple[bytes, str, str]:
    """
    Synthesize speech using ElevenLabs API.
    Returns: (audio_bytes, mime_type, file_extension)
    """
    if not api_key or not api_key.strip():
        raise ValueError("Please provide an ElevenLabs API key to generate speech.")

    if not text or not text.strip():
        raise ValueError("Text input cannot be empty.")

    clean_key = api_key.strip()
    fmt_meta = OUTPUT_FORMATS.get(output_format, OUTPUT_FORMATS["mp3_44100_128"])

    # Attempt primary via official SDK
    try:
        client = get_client(clean_key)
        voice_settings = VoiceSettings(
            stability=float(stability),
            similarity_boost=float(similarity_boost),
            style=float(style),
            use_speaker_boost=bool(use_speaker_boost),
            speed=float(speed) if speed != 1.0 else None,
        )

        audio_generator = client.text_to_speech.convert(
            voice_id=voice_id,
            text=text,
            model_id=model_id,
            voice_settings=voice_settings,
            output_format=output_format,
        )

        audio_bytes = b"".join(chunk for chunk in audio_generator if chunk)
        if not audio_bytes:
            raise RuntimeError("Received empty audio stream from ElevenLabs.")

        return audio_bytes, fmt_meta["mime"], fmt_meta["ext"]

    except ApiError as err:
        status_code = getattr(err, "status_code", None)
        body = getattr(err, "body", str(err))
        if status_code == 401:
            raise PermissionError("Authentication failed (401). Check if your ElevenLabs API key is correct.")
        elif status_code == 429 or "quota_exceeded" in str(body).lower():
            raise RuntimeError("Character quota exceeded or rate limit reached on your ElevenLabs tier.")
        elif status_code == 400:
            raise ValueError(f"Bad Request (400): {body}")
        else:
            raise RuntimeError(f"ElevenLabs API Error ({status_code}): {body}")

    except Exception as exc:
        # Fallback to direct REST API if SDK fails or raises unexpected iterator error
        try:
            url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}?output_format={output_format}"
            headers = {
                "xi-api-key": clean_key,
                "Content-Type": "application/json",
            }
            payload = {
                "text": text,
                "model_id": model_id,
                "voice_settings": {
                    "stability": float(stability),
                    "similarity_boost": float(similarity_boost),
                    "style": float(style),
                    "use_speaker_boost": bool(use_speaker_boost),
                },
            }
            if speed != 1.0:
                payload["voice_settings"]["speed"] = float(speed)

            resp = requests.post(url, headers=headers, json=payload, timeout=60)
            if resp.status_code == 200:
                return resp.content, fmt_meta["mime"], fmt_meta["ext"]
            elif resp.status_code == 401:
                raise PermissionError("Invalid ElevenLabs API key (401 Unauthorized).")
            elif resp.status_code == 429:
                raise RuntimeError("Quota limit reached or too many requests (429).")
            else:
                raise RuntimeError(f"ElevenLabs API HTTP {resp.status_code}: {resp.text}")
        except Exception as req_err:
            raise RuntimeError(f"Generation error: {str(req_err)}") from exc
