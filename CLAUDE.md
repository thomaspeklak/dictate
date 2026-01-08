# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

Speech-to-text dictation tool for Linux/Wayland. Records audio via toggle (keyboard shortcut), transcribes with faster-whisper, cleans up text with Claude CLI (Haiku), copies to clipboard. Shows progress via system notifications.

## Usage

```bash
./dictate.py           # Start recording (English)
./dictate.py           # Run again to stop → transcribe → process → clipboard
./dictate.py -l de     # German transcription
```

Toggle mechanism uses PID file (`/tmp/dictate.pid`) and SIGUSR1 signaling.

## Architecture

```
dictate.py              # Entry point, toggle logic, pipeline orchestration
dictate/
├── recorder.py         # PyAudio recording, resamples to 16kHz
├── transcriber.py      # faster-whisper wrapper
├── agent.py            # Claude CLI (haiku) for text cleanup
├── clipboard.py        # wl-copy wrapper
├── notifier.py         # notify-send with --replace-id for updates
└── config.py           # TOML config loading
```

Key design: Heavy imports deferred until after toggle check (line 74-80 in dictate.py) for fast response when just signaling stop.

## Dependencies

System: `portaudio-devel`, `wl-clipboard`, `libnotify`, `claude` CLI

Python: `faster-whisper`, `pyaudio`, `numpy`

## Configuration

Edit `config.toml` for whisper model, language, audio device, custom prompt template.
