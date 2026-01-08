#!/usr/bin/env python3
"""Dictate - Speech-to-text with agent processing.

Toggle recording with keyboard shortcut (via GNOME keybinding).
First invocation starts recording, second stops and processes.
"""

import argparse
import os
import signal
import sys
import time

PID_FILE = "/tmp/dictate.pid"


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Speech-to-text with agent processing"
    )
    parser.add_argument(
        "-l", "--language",
        default=None,
        help="Language code (e.g., 'de' for German). Default: en",
    )
    parser.add_argument(
        "-r", "--raw",
        action="store_true",
        help="Skip Claude processing, output raw transcription",
    )
    return parser.parse_args()


def is_running() -> int | None:
    """Check if another instance is recording.

    Returns:
        PID of running instance, or None if not running.
    """
    if os.path.exists(PID_FILE):
        try:
            with open(PID_FILE) as f:
                pid = int(f.read().strip())
            # Check if process exists
            os.kill(pid, 0)
            return pid
        except (OSError, ValueError):
            # Process doesn't exist or invalid PID - clean up stale file
            try:
                os.unlink(PID_FILE)
            except OSError:
                pass
    return None


def cleanup_pid_file() -> None:
    """Remove PID file."""
    try:
        os.unlink(PID_FILE)
    except OSError:
        pass


def main() -> int:
    """Main entry point."""
    args = parse_args()

    # Check if another instance is running
    existing_pid = is_running()
    if existing_pid:
        # Signal existing process to stop recording
        try:
            os.kill(existing_pid, signal.SIGUSR1)
        except OSError:
            pass
        return 0

    # Import here to avoid slow startup when just signaling
    from dictate.agent import Agent
    from dictate.clipboard import copy_to_clipboard
    from dictate.config import Config
    from dictate.notifier import Notifier
    from dictate.recorder import Recorder
    from dictate.transcriber import Transcriber

    # Write PID file
    with open(PID_FILE, "w") as f:
        f.write(str(os.getpid()))

    # Track if we should stop
    should_stop = False

    def handle_stop_signal(signum, frame):
        nonlocal should_stop
        should_stop = True

    signal.signal(signal.SIGUSR1, handle_stop_signal)

    recorder = None
    try:
        # Load configuration
        config = Config.load()

        # Reset notification ID for fresh session
        Notifier.reset()

        # Start recording
        Notifier.recording()
        recorder = Recorder()
        recorder.start(device_index=config.audio_device)

        # Wait for stop signal
        while not should_stop:
            time.sleep(0.1)

        # Stop recording and get audio
        audio = recorder.stop()

        # Check if recording is too short
        if len(audio) < 16000:  # Less than 1 second at 16kHz
            Notifier.error("Recording too short")
            return 1

        # Transcribe
        Notifier.transcribing()
        transcriber = Transcriber(
            model_size=config.model_size,
            device=config.device,
            compute_type=config.compute_type,
        )
        language = args.language or config.language
        text = transcriber.transcribe(audio, language=language)

        if not text.strip():
            Notifier.error("No speech detected")
            return 1

        # Process with Claude (unless --raw)
        if args.raw:
            processed = text
        else:
            Notifier.processing()
            agent = Agent(prompt_template=config.prompt_template)
            try:
                processed = agent.process(text)
            except Exception as e:
                # Fallback to raw transcription if Claude fails
                processed = text
                Notifier.notify("Warning", f"Claude failed, using raw text: {e}", "dialog-warning")

        # Copy to clipboard
        copy_to_clipboard(processed)
        Notifier.done(processed)

        return 0

    except Exception as e:
        Notifier.error(str(e))
        return 1

    finally:
        if recorder:
            recorder.terminate()
        cleanup_pid_file()


if __name__ == "__main__":
    sys.exit(main())
