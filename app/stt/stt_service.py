import logging
from .local_whisper import transcribe_with_whisper
from .local_wav2vec2 import transcribe_with_wav2vec2
from .audio_processor import cleanup_audio
from .model_loader import WHISPER_MODELS, WAV2VEC2_MODELS

logger = logging.getLogger(__name__)


class STTService:
    """
    Main Speech-to-Text service.
    Sends audio to HuggingFace API.
    Chooses correct model and returns transcript.
    """

    def _resolve_model_name(self, model_type: str, model_size: str) -> str:
        """Get full HuggingFace model name from type and size."""
        if model_type == "wav2vec2":
            return WAV2VEC2_MODELS.get(model_size, WAV2VEC2_MODELS["base"])
        return WHISPER_MODELS.get(model_size, WHISPER_MODELS["base"])

    def transcribe(
        self,
        audio_path: str,
        model_type: str = "whisper",
        model_size: str = "base",
        language: str = "english",
    ) -> dict:
        """
        Transcribe audio file to text via HuggingFace API.

        Args:
            audio_path  : Path to uploaded audio file
            model_type  : "whisper" or "wav2vec2"
            model_size  : tiny | base | small | medium | large-v3
            language    : Language (whisper only, wav2vec2 is English only)

        Returns:
            dict with transcript, model_used, language, status, error
        """
        # ✅ Resolve full model name upfront (fixes error case showing wrong name)
        model_used = self._resolve_model_name(model_type, model_size)

        try:
            logger.info(
                f"STT Request → model={model_used}, "
                f"lang={language}, file={audio_path}"
            )

            if model_type == "wav2vec2":
                transcript = transcribe_with_wav2vec2(
                    audio_path=audio_path,
                    model_size=model_size,
                )
                language = "english"    # wav2vec2 is English only

            else:
                # Default: Whisper (supports 100+ languages)
                transcript = transcribe_with_whisper(
                    audio_path=audio_path,
                    model_size=model_size,
                    language=language,
                )

            logger.info(f"STT Success → {len(transcript)} characters")

            return {
                "transcript": transcript,
                "model_used": model_used,   # ✅ always full HF name
                "language":   language,
                "status":     "success",
                "error":       None,
            }

        except Exception as e:
            logger.error(f"STT Service error: {e}")
            return {
                "transcript": "",
                "model_used": model_used,   # ✅ fixed: was "whisper-tiny" now "openai/whisper-tiny"
                "language":   language,
                "status":     "error",
                "error":      str(e),
            }

        finally:
            # Always clean up temp audio files
            cleanup_audio(audio_path)