import os
import logging
import requests
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# ─── Your HuggingFace API Token from .env ───
HF_API_TOKEN = os.getenv("HUGGINGFACE_API_TOKEN", "")

# ─── HuggingFace Inference Router URL (2025) ───
HF_API_URL = "https://router.huggingface.co/hf-inference/models"

# ─── Model name mapping ───
WHISPER_MODELS = {
    "tiny":     "openai/whisper-large-v3-turbo",  # ✅ free tier
    "base":     "openai/whisper-large-v3-turbo",  # ✅ free tier
    "small":    "openai/whisper-small",
    "medium":   "openai/whisper-medium",
    "large-v3": "openai/whisper-large-v3",
}

WAV2VEC2_MODELS = {
    "base":  "facebook/wav2vec2-base-960h",
    "large": "facebook/wav2vec2-large-960h",
}


def _get_headers(content_type: str = "audio/wav"):
    """Build authorization headers."""
    if not HF_API_TOKEN:
        raise ValueError(
            "HUGGINGFACE_API_TOKEN is missing! Add it to your .env file.\n"
            "Get your token: https://huggingface.co/settings/tokens"
        )
    return {
        "Authorization": f"Bearer {HF_API_TOKEN}",
        "Content-Type": content_type,
    }


def _call_hf_api(model_name: str, audio_bytes: bytes) -> str:
    """
    Send audio bytes to HuggingFace Inference Router.
    Returns transcript text.
    """
    # ✅ FIXED: no task suffix — just model name
    url = f"{HF_API_URL}/{model_name}"
    headers = _get_headers("audio/wav")

    logger.info(f"Calling HuggingFace Router: {url}")

    response = requests.post(
        url,
        headers=headers,
        data=audio_bytes,
        timeout=60,
    )

    logger.info(f"Response status: {response.status_code}")

    if response.status_code == 503:
        try:
            error = response.json()
            wait_time = error.get("estimated_time", 20)
        except Exception:
            wait_time = 20
        logger.warning(f"Model warming up, wait: {wait_time}s")
        raise RuntimeError(
            f"Model warming up on HuggingFace server. "
            f"Wait ~{wait_time:.0f}s and retry."
        )

    if response.status_code == 410:
        raise RuntimeError(
            "HuggingFace API URL deprecated (410).\n"
            "Old: api-inference.huggingface.co  ❌\n"
            "New: router.huggingface.co/hf-inference/models  ✅"
        )

    if response.status_code == 404:
        raise RuntimeError(
            f"Model not found (404): {model_name}\n"
            f"URL tried: {url}\n"
            f"Check model name at huggingface.co/models"
        )

    if response.status_code == 401:
        raise ValueError(
            "Invalid HuggingFace API token (401).\n"
            "Check HUGGINGFACE_API_TOKEN in your .env file."
        )

    if response.status_code == 429:
        raise RuntimeError(
            "HuggingFace API rate limit reached (429).\n"
            "Wait a moment and retry."
        )

    if response.status_code != 200:
        raise RuntimeError(
            f"HuggingFace API error {response.status_code}: {response.text}"
        )

    result = response.json()

    # Response format: {"text": "transcript here"}
    if isinstance(result, dict):
        return result.get("text", "").strip()

    # Sometimes returns list
    if isinstance(result, list) and len(result) > 0:
        return result[0].get("text", "").strip()

    return ""


def get_whisper_model(model_size: str = "base"):
    """
    Returns a callable that sends audio to HuggingFace Whisper API.
    No download. No local model.

    Sizes: tiny, base, small, medium, large-v3
    """
    model_name = WHISPER_MODELS.get(model_size, WHISPER_MODELS["base"])
    logger.info(f"Using HuggingFace API model: {model_name}")

    def transcribe(audio_path: str, **kwargs) -> dict:
        with open(audio_path, "rb") as f:
            audio_bytes = f.read()
        transcript = _call_hf_api(model_name, audio_bytes)
        return {"text": transcript}

    return transcribe


def get_wav2vec2_model(model_size: str = "base"):
    """
    Returns a callable that sends audio to HuggingFace Wav2Vec2 API.
    No download. No local model. English only.

    Sizes: base, large
    """
    model_name = WAV2VEC2_MODELS.get(model_size, WAV2VEC2_MODELS["base"])
    logger.info(f"Using HuggingFace API model: {model_name}")

    def transcribe(audio_path: str, **kwargs) -> dict:
        with open(audio_path, "rb") as f:
            audio_bytes = f.read()
        transcript = _call_hf_api(model_name, audio_bytes)
        return {"text": transcript}

    return transcribe


def clear_model_cache():
    """No local cache to clear when using API."""
    logger.info("Using HuggingFace API — no local cache to clear.")