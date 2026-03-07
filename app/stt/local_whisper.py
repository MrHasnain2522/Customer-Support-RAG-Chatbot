import logging
from .model_loader import get_whisper_model
from .audio_processor import convert_to_wav

logger = logging.getLogger(__name__)

SUPPORTED_LANGUAGES = [
    "english", "urdu", "arabic", "french",
    "spanish", "german", "chinese", "japanese",
    "hindi", "portuguese", "russian", "auto"
]


def transcribe_with_whisper(
    audio_path: str,
    model_size: str = "base",
    language: str = "english"
) -> str:
    """
    Transcribe audio using HuggingFace Whisper API.
    No local model. Sends audio to HF server.

    Args:
        audio_path  : Path to audio file
        model_size  : tiny | base | small | medium | large-v3
        language    : Language of audio or 'auto' to detect

    Returns:
        Transcribed text string
    """
    try:
        # Validate language
        if language.lower() not in SUPPORTED_LANGUAGES:
            logger.warning(
                f"Language '{language}' not in supported list. "
                f"Supported: {SUPPORTED_LANGUAGES}. Defaulting to 'english'."
            )
            language = "english"

        # Convert audio to 16kHz WAV (required by Whisper)
        wav_path = convert_to_wav(audio_path)

        # Get API callable (no local download)
        transcribe = get_whisper_model(model_size)

        logger.info(f"Transcribing with HF API whisper-{model_size}, language={language}")

        # Call HuggingFace API
        # NOTE: language param handled server-side by HF
        # 'auto' = let HF Whisper detect language automatically
        result = transcribe(wav_path, language=language)

        transcript = result.get("text", "").strip()
        logger.info(f"Transcription complete: {len(transcript)} characters")
        return transcript

    except Exception as e:
        logger.error(f"Whisper API transcription failed: {e}")
        raise