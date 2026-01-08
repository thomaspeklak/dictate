"""Speech-to-text transcription using faster-whisper."""

import numpy as np
from faster_whisper import WhisperModel


class Transcriber:
    """Transcribe audio using faster-whisper."""

    def __init__(
        self,
        model_size: str = "base",
        device: str = "cpu",
        compute_type: str = "int8",
    ):
        """Initialize the transcriber.

        Args:
            model_size: "tiny", "base", "small", "medium", "large-v2", "large-v3"
            device: "cpu" or "cuda"
            compute_type: "int8", "int16", "float16", "float32"
        """
        self.model = WhisperModel(model_size, device=device, compute_type=compute_type)

    def transcribe(self, audio: np.ndarray, language: str = "en") -> str:
        """Transcribe audio array to text.

        Args:
            audio: Audio data as float32 numpy array (16kHz)
            language: Language code (e.g., "en", "de") or None for auto-detection

        Returns:
            Transcribed text
        """
        if len(audio) < 1600:  # Less than 0.1 seconds
            return ""

        segments, _ = self.model.transcribe(
            audio,
            language=language,
            beam_size=5,
            vad_filter=True,
            vad_parameters={"min_silence_duration_ms": 500},
            condition_on_previous_text=False,
        )

        text_parts = [segment.text.strip() for segment in segments]
        return " ".join(text_parts)
