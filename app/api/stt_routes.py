from flask import Blueprint, request, jsonify
from app.stt.stt_service import STTService
from app.stt.audio_processor import save_audio_file, get_audio_info
from app.stt.model_loader import WHISPER_MODELS, WAV2VEC2_MODELS
import logging

logger = logging.getLogger(__name__)
stt_bp = Blueprint("stt", __name__, url_prefix="/api/stt")
stt_service = STTService()


@stt_bp.route("/transcribe", methods=["POST"])
def transcribe_audio():
    """
    POST /api/stt/transcribe
    Upload audio → get transcript back

    Form Data:
        audio       : Audio file (mp3, wav, ogg, m4a, flac, webm)
        model_type  : "whisper" or "wav2vec2"  (default: whisper)
        model_size  : tiny/base/small/medium/large-v3 (default: base)
        language    : Language string  (default: english)
    """
    try:
        # ── Validate file exists ──────────────────────────
        if "audio" not in request.files:
            return jsonify({
                "error": "No audio file provided.",
                "hint" : "Use form-data key: 'audio'"
            }), 400

        audio_file = request.files["audio"]

        if not audio_file.filename:
            return jsonify({
                "error": "Empty filename.",
                "hint" : "Make sure a file is selected."
            }), 400

        # ── Validate model params ─────────────────────────
        model_type = request.form.get("model_type", "whisper").lower()
        model_size = request.form.get("model_size", "base").lower()
        language   = request.form.get("language",   "english").lower()

        if model_type not in ["whisper", "wav2vec2"]:
            return jsonify({
                "error": f"Invalid model_type: '{model_type}'.",
                "hint" : "Use 'whisper' or 'wav2vec2'."
            }), 400

        # ── Save uploaded file ────────────────────────────
        audio_path = save_audio_file(audio_file)

        # ── Log audio info ────────────────────────────────
        info = get_audio_info(audio_path)
        if info:
            logger.info(
                f"Audio info → duration={info.get('duration')}s, "
                f"size={info.get('size_mb')}MB, "
                f"format={info.get('format')}"
            )

        # ── Transcribe ────────────────────────────────────
        result = stt_service.transcribe(
            audio_path=audio_path,
            model_type=model_type,
            model_size=model_size,
            language=language,
        )

        if result["status"] == "error":
            return jsonify(result), 500

        return jsonify(result), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    except Exception as e:
        logger.error(f"STT route error: {e}")
        return jsonify({"error": "Internal server error", "detail": str(e)}), 500


@stt_bp.route("/models", methods=["GET"])
def list_models():
    """GET /api/stt/models — List all supported HF API models."""
    return jsonify({
        "note": "All models run via HuggingFace API — no local download needed.",
        "whisper": {
            "models": [
                {
                    "size":  "tiny",
                    "hf_id": "openai/whisper-tiny",
                    "speed": "fastest",
                    "best_for": "quick transcription, low accuracy"
                },
                {
                    "size":  "base",
                    "hf_id": "openai/whisper-base",
                    "speed": "fast",
                    "best_for": "general use, good balance"
                },
                {
                    "size":  "small",
                    "hf_id": "openai/whisper-small",
                    "speed": "medium",
                    "best_for": "better accuracy"
                },
                {
                    "size":  "medium",
                    "hf_id": "openai/whisper-medium",
                    "speed": "slow",
                    "best_for": "high accuracy"
                },
                {
                    "size":  "large-v3",
                    "hf_id": "openai/whisper-large-v3",
                    "speed": "slowest",
                    "best_for": "best accuracy, production use"
                },
            ],
            "languages": "100+ languages + auto detect",
        },
        "wav2vec2": {
            "models": [
                {
                    "size":  "base",
                    "hf_id": "facebook/wav2vec2-base-960h",
                    "speed": "fast",
                    "best_for": "English, lightweight"
                },
                {
                    "size":  "large",
                    "hf_id": "facebook/wav2vec2-large-960h",
                    "speed": "medium",
                    "best_for": "English, higher accuracy"
                },
            ],
            "languages": "English only",
        },
    }), 200


@stt_bp.route("/health", methods=["GET"])
def stt_health():
    """GET /api/stt/health — Check STT service health."""
    import os
    from dotenv import load_dotenv
    load_dotenv()

    token = os.getenv("HUGGINGFACE_API_TOKEN", "")

    return jsonify({
        "status":        "ok",
        "service":       "Speech-to-Text",
        "provider":      "HuggingFace Inference API",
        "router_url":    "https://router.huggingface.co/hf-inference/models",
        "token_set":     bool(token),
        "token_preview": f"{token[:8]}..." if token else "NOT SET ❌",
    }), 200