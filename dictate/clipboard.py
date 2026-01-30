"""Clipboard operations using wl-copy (Wayland)."""

import subprocess


def copy_to_clipboard(text: str) -> None:
    """Copy text to clipboard using wl-copy."""
    subprocess.run(
        ["wl-copy"],
        input=text.encode("utf-8"),
        check=True,
    )


def type_text(text: str) -> None:
    """Type text at cursor using wtype."""
    subprocess.run(
        ["wtype", "--", text],
        check=True,
    )
