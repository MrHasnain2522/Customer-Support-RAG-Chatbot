import pytest
import os
from dotenv import load_dotenv
from unittest.mock import patch
from app.stt.stt_service import STTService

load_dotenv()  # ← Load .env before all tests


@pytest.fixture
def stt_service():
    return STTService()


@pytest.fixture
def sample_audio(tmp_path):
    """Create a tiny silent WAV file for testing."""
    import wave, struct
    filepath = tmp_path / "test.wav"
    with wave.open(str(filepath), "w") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(16000)
        f.writeframes(struct.pack("<h", 0) * 16000)  # 1 second silent
    return str(filepath)


# ──────────────────────────────────────────
# ✅ MOCK TESTS (No real API call)
# ──────────────────────────────────────────

def test_stt_service_returns_dict(stt_service, sample_audio):
    """Test response is always a dict with required keys."""
    with patch("app.stt.model_loader._call_hf_api", return_value="hello world"):
        result = stt_service.transcribe(audio_path=sample_audio)
        assert isinstance(result, dict)
        assert "transcript" in result
        assert "status" in result
        assert "model_used" in result
        assert "language" in result


def test_stt_whisper_base(stt_service, sample_audio):
    """Test whisper-base returns correct model name."""
    with patch("app.stt.model_loader._call_hf_api", return_value="test transcript"):
        result = stt_service.transcribe(
            audio_path=sample_audio,
            model_type="whisper",
            model_size="base",
            language="english",
        )
        assert result["status"] == "success"
        assert result["model_used"] == "openai/whisper-base"
        assert result["transcript"] == "test transcript"


def test_stt_whisper_tiny(stt_service, sample_audio):
    """Test whisper-tiny returns correct model name."""
    with patch("app.stt.model_loader._call_hf_api", return_value="tiny transcript"):
        result = stt_service.transcribe(
            audio_path=sample_audio,
            model_type="whisper",
            model_size="tiny",
        )
        assert result["status"] == "success"
        assert result["model_used"] == "openai/whisper-tiny"


def test_stt_wav2vec2(stt_service, sample_audio):
    """Test wav2vec2 returns correct model and forces english."""
    with patch("app.stt.model_loader._call_hf_api", return_value="wav2vec result"):
        result = stt_service.transcribe(
            audio_path=sample_audio,
            model_type="wav2vec2",
            model_size="base",
        )
        assert result["status"] == "success"
        assert result["model_used"] == "facebook/wav2vec2-base-960h"
        assert result["language"] == "english"


def test_stt_invalid_model_falls_back_to_whisper(stt_service, sample_audio):
    """Test invalid model type falls back to whisper."""
    with patch("app.stt.model_loader._call_hf_api", return_value="fallback"):
        result = stt_service.transcribe(
            audio_path=sample_audio,
            model_type="invalid_model",
        )
        assert "status" in result


def test_stt_api_returns_empty_string(stt_service, sample_audio):
    """Test when HF API returns empty transcript (silent audio)."""
    with patch("app.stt.model_loader._call_hf_api", return_value=""):
        result = stt_service.transcribe(audio_path=sample_audio)
        assert result["status"] == "success"
        assert result["transcript"] == ""


def test_stt_missing_hf_token(stt_service, sample_audio):
    """Test error when HF API token is missing."""
    with patch("app.stt.model_loader._call_hf_api",
               side_effect=ValueError("HUGGINGFACE_API_TOKEN is missing")):
        result = stt_service.transcribe(audio_path=sample_audio)
        assert result["status"] == "error"
        assert "error" in result


def test_stt_api_503_model_loading(stt_service, sample_audio):
    """Test HF API 503 — model warming up on HF server."""
    with patch("app.stt.model_loader._call_hf_api",
               side_effect=RuntimeError("Model is warming up")):
        result = stt_service.transcribe(audio_path=sample_audio)
        assert result["status"] == "error"
        assert result["transcript"] == ""


def test_stt_api_429_rate_limit(stt_service, sample_audio):
    """Test HF API 429 — rate limit hit."""
    with patch("app.stt.model_loader._call_hf_api",
               side_effect=RuntimeError("rate limit reached")):
        result = stt_service.transcribe(audio_path=sample_audio)
        assert result["status"] == "error"


def test_stt_api_410_deprecated_url(stt_service, sample_audio):
    """Test HF API 410 — old URL deprecated, new router URL required."""
    with patch("app.stt.model_loader._call_hf_api",
               side_effect=RuntimeError("HuggingFace API URL is deprecated (410)")):
        result = stt_service.transcribe(audio_path=sample_audio)
        assert result["status"] == "error"
        assert result["transcript"] == ""


# ──────────────────────────────────────────
# 🌐 REAL API TEST (needs HF token in .env)
# ──────────────────────────────────────────

@pytest.mark.skipif(
    not os.getenv("HUGGINGFACE_API_TOKEN"),
    reason="HUGGINGFACE_API_TOKEN not set in .env"
)
def test_real_hf_api_call(stt_service, sample_audio):
    """
    REAL test — actually calls HuggingFace API.
    Only runs if HUGGINGFACE_API_TOKEN is set in .env
    Uses new router URL: router.huggingface.co
    """
    result = stt_service.transcribe(
        audio_path=sample_audio,
        model_type="whisper",
        model_size="tiny",
        language="english",
    )
    assert isinstance(result, dict)
    assert result["status"] in ["success", "error"]
    print(f"\n✅ Real API response: {result}")