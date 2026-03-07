from pydantic import BaseModel, field_validator
from typing import Optional, Literal


class STTRequest(BaseModel):
    model_type: Optional[Literal["whisper", "wav2vec2"]] = "whisper"
    model_size: Optional[str] = "base"
    language: Optional[str] = "english"

    @field_validator("model_size")
    @classmethod
    def validate_model_size(cls, v, info):
        model_type = info.data.get("model_type", "whisper")

        whisper_sizes  = ["tiny", "base", "small", "medium", "large-v3"]
        wav2vec2_sizes = ["base", "large"]

        if model_type == "whisper" and v not in whisper_sizes:
            raise ValueError(
                f"Invalid whisper size: '{v}'. "
                f"Choose from: {whisper_sizes}"
            )

        if model_type == "wav2vec2" and v not in wav2vec2_sizes:
            raise ValueError(
                f"Invalid wav2vec2 size: '{v}'. "
                f"Choose from: {wav2vec2_sizes}"
            )

        return v

    @field_validator("language")
    @classmethod
    def validate_language(cls, v):
        supported = [
            "english", "urdu", "arabic", "french",
            "spanish", "german", "chinese", "japanese",
            "hindi", "portuguese", "russian", "auto"
        ]
        if v.lower() not in supported:
            raise ValueError(
                f"Unsupported language: '{v}'. "
                f"Supported: {supported}"
            )
        return v.lower()


class STTResponse(BaseModel):
    transcript: str
    model_used: str
    language: str
    status: Literal["success", "error"] = "success"
    error: Optional[str] = None

    model_config = {"json_schema_extra": {
        "example": {
            "transcript": "Hello this is a test",
            "model_used": "openai/whisper-base",
            "language":   "english",
            "status":     "success",
            "error":       None,
        }
    }}