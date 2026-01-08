"""Clipboard operations using wl-copy (Wayland)."""

import subprocess


def copy_to_clipboard(text: str) -> None:
    """Copy text to clipboard using wl-copy."""
    subprocess.run(
        ["wl-copy"],
        input=text.encode("utf-8"),
        check=True,
    )
