import os
import uuid
import logging
import subprocess
from pathlib import Path

logger = logging.getLogger(__name__)

UPLOAD_DIR = Path("audio_uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

SUPPORTED_FORMATS = [".mp3", ".wav", ".ogg", ".m4a", ".flac", ".webm"]
MAX_FILE_SIZE_MB = 25  # HuggingFace API limit


def save_audio_file(file) -> str:
    """Save uploaded audio file and return path."""
    try:
        ext = Path(file.filename).suffix.lower()

        if ext not in SUPPORTED_FORMATS:
            raise ValueError(
                f"Unsupported format: '{ext}'. "
                f"Supported: {SUPPORTED_FORMATS}"
            )

        filename  = f"{uuid.uuid4()}{ext}"
        filepath  = UPLOAD_DIR / filename

        file.save(str(filepath))

        # ✅ Check file size after saving (HF API limit = 25MB)
        size_mb = os.path.getsize(filepath) / (1024 * 1024)
        if size_mb > MAX_FILE_SIZE_MB:
            os.remove(filepath)
            raise ValueError(
                f"File too large: {size_mb:.1f}MB. "
                f"Max allowed: {MAX_FILE_SIZE_MB}MB."
            )

        logger.info(f"Audio saved: {filepath} ({size_mb:.1f}MB)")
        return str(filepath)

    except Exception as e:
        logger.error(f"Failed to save audio: {e}")
        raise


def convert_to_wav(input_path: str) -> str:
    """
    Convert any audio format to 16kHz mono WAV.
    Uses ffmpeg — no librosa or soundfile needed.
    """
    try:
        output_path = str(input_path).replace(
            Path(input_path).suffix, "_converted.wav"
        )

        command = [
            "ffmpeg",
            "-i", input_path,   # Input file
            "-ar", "16000",     # Resample to 16kHz
            "-ac", "1",         # Mono channel
            "-acodec", "pcm_s16le",  # ✅ 16-bit PCM (best for STT models)
            "-y",               # Overwrite if exists
            output_path,
        ]

        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            logger.error(f"ffmpeg error: {result.stderr}")
            raise RuntimeError(f"Audio conversion failed: {result.stderr}")

        # ✅ Verify output file was actually created
        if not os.path.exists(output_path):
            raise RuntimeError("ffmpeg ran but output file was not created.")

        size_mb = os.path.getsize(output_path) / (1024 * 1024)
        logger.info(f"Converted to WAV 16kHz: {output_path} ({size_mb:.1f}MB)")
        return output_path

    except FileNotFoundError:
        logger.error("ffmpeg not found!")
        raise RuntimeError(
            "ffmpeg is not installed.\n"
            "Linux  : sudo apt install ffmpeg -y\n"
            "Mac    : brew install ffmpeg\n"
            "Windows: winget install ffmpeg"
        )

    except Exception as e:
        logger.error(f"Audio conversion failed: {e}")
        raise


def cleanup_audio(filepath: str):
    """Delete temp audio files after processing."""
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
            logger.info(f"Cleaned up: {filepath}")

        converted = str(filepath).replace(
            Path(filepath).suffix, "_converted.wav"
        )
        if os.path.exists(converted):
            os.remove(converted)
            logger.info(f"Cleaned up converted: {converted}")

    except Exception as e:
        logger.warning(f"Cleanup failed: {e}")


def get_audio_info(filepath: str) -> dict:
    """✅ NEW: Get audio file info using ffmpeg."""
    try:
        command = [
            "ffprobe",
            "-v", "quiet",
            "-print_format", "json",
            "-show_format",
            "-show_streams",
            filepath,
        ]
        result = subprocess.run(command, capture_output=True, text=True)

        if result.returncode == 0:
            import json
            info = json.loads(result.stdout)
            fmt  = info.get("format", {})
            return {
                "filename" : fmt.get("filename", ""),
                "duration" : round(float(fmt.get("duration", 0)), 2),
                "size_mb"  : round(int(fmt.get("size", 0)) / (1024*1024), 2),
                "format"   : fmt.get("format_name", ""),
            }
    except Exception as e:
        logger.warning(f"Could not get audio info: {e}")

    return {}