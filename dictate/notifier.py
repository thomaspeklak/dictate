"""System notifications with update/replace support."""

import subprocess


class Notifier:
    """Handle system notifications with replacement capability."""

    _notification_id: int | None = None
    APP_NAME = "Dictate"

    @classmethod
    def notify(
        cls,
        title: str,
        body: str = "",
        icon: str = "audio-input-microphone",
    ) -> None:
        """Show or update a notification."""
        cmd = [
            "notify-send",
            "--app-name",
            cls.APP_NAME,
            "--icon",
            icon,
        ]

        if cls._notification_id is not None:
            cmd.extend(["--replace-id", str(cls._notification_id)])

        cmd.extend(["--print-id", title])
        if body:
            cmd.append(body)

        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0 and result.stdout.strip():
            try:
                cls._notification_id = int(result.stdout.strip())
            except ValueError:
                pass

    @classmethod
    def recording(cls) -> None:
        """Show recording started notification."""
        cls.notify("Recording...", "Press hotkey again to stop", "audio-input-microphone")

    @classmethod
    def transcribing(cls) -> None:
        """Show transcribing notification."""
        cls.notify("Transcribing...", "Processing audio with Whisper", "system-run")

    @classmethod
    def processing(cls) -> None:
        """Show processing with Claude notification."""
        cls.notify("Processing...", "Formatting with Claude", "system-run")

    @classmethod
    def done(cls, preview: str = "") -> None:
        """Show completion notification."""
        body = preview[:100] + "..." if len(preview) > 100 else preview
        cls.notify("Copied to clipboard", body, "edit-paste")

    @classmethod
    def error(cls, message: str) -> None:
        """Show error notification."""
        cls.notify("Dictation Error", message, "dialog-error")

    @classmethod
    def reset(cls) -> None:
        """Reset notification ID for fresh session."""
        cls._notification_id = None
