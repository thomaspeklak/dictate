"""Configuration loading for dictate."""

import tomllib
from dataclasses import dataclass, field
from pathlib import Path


DEFAULT_PROMPT = """Clean up this dictated text. Fix grammar and punctuation. Keep the natural sentence structure - only use bullet points if the content is clearly a list.

CRITICAL: Output ONLY the cleaned text. No commentary, no translations, no explanations. Keep the original language. Minimal changes.

{text}"""


@dataclass
class Config:
    """Configuration for the dictate tool."""

    model_size: str = "base"
    device: str = "cpu"
    compute_type: str = "int8"
    language: str = "en"
    audio_device: int | None = None
    prompt_template: str = field(default=DEFAULT_PROMPT)

    @classmethod
    def load(cls, path: Path | None = None) -> "Config":
        """Load configuration from TOML file."""
        if path is None:
            path = Path(__file__).parent.parent / "config.toml"

        if not path.exists():
            return cls()

        with open(path, "rb") as f:
            data = tomllib.load(f)

        whisper = data.get("whisper", {})
        audio = data.get("audio", {})
        agent = data.get("agent", {})

        return cls(
            model_size=whisper.get("model_size", "base"),
            device=whisper.get("device", "cpu"),
            compute_type=whisper.get("compute_type", "int8"),
            language=whisper.get("language", "en"),
            audio_device=audio.get("device"),
            prompt_template=agent.get("prompt_template", DEFAULT_PROMPT),
        )
