import logging
from .model_loader import get_wav2vec2_model
from .audio_processor import convert_to_wav

logger = logging.getLogger(__name__)


def transcribe_with_wav2vec2(audio_path: str, model_size: str = "base") -> str:
    """
    Transcribe audio using HuggingFace Wav2Vec2 API.
    NOTE: Wav2Vec2 supports English only.

    Args:
        audio_path  : Path to audio file
        model_size  : base | large

    Returns:
        Transcribed text string
    """
    try:
        # Convert to 16kHz WAV (required by Wav2Vec2)
        wav_path = convert_to_wav(audio_path)

        # Get API callable (no local download)
        transcribe = get_wav2vec2_model(model_size)

        logger.info(f"Transcribing with HF API wav2vec2-{model_size}")

        # Call HuggingFace API
        result = transcribe(wav_path)

        transcript = result.get("text", "").strip().lower()
        logger.info(f"Transcription complete: {len(transcript)} characters")
        return transcript

    except Exception as e:
        logger.error(f"Wav2Vec2 API transcription failed: {e}")
        raise