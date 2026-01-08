"""Agent processing using Claude CLI."""

import subprocess

from .config import DEFAULT_PROMPT


class Agent:
    """Process text through Claude CLI."""

    def __init__(self, prompt_template: str | None = None, model: str = "haiku"):
        self.prompt_template = prompt_template or DEFAULT_PROMPT
        self.model = model

    def process(self, text: str, timeout: int = 120) -> str:
        """Process text through Claude CLI.

        Args:
            text: Raw transcribed text to process
            timeout: Timeout in seconds for Claude CLI

        Returns:
            Processed/structured text

        Raises:
            RuntimeError: If Claude CLI fails
            subprocess.TimeoutExpired: If processing times out
        """
        prompt = self.prompt_template.format(text=text)

        result = subprocess.run(
            ["claude", "-p", "--model", self.model, prompt],
            capture_output=True,
            text=True,
            timeout=timeout,
        )

        if result.returncode != 0:
            raise RuntimeError(f"Claude CLI failed: {result.stderr}")

        return result.stdout.strip()
