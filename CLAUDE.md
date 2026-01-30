# CLAUDE.md

Speech-to-text dictation tool for Linux/Wayland. See README.md for user documentation.

## Architecture

```
dictate.py              # Entry point, toggle logic (PID file + SIGUSR1), pipeline orchestration
dictate/
├── recorder.py         # PyAudio recording with callback, resamples to 16kHz
├── transcriber.py      # faster-whisper wrapper
├── agent.py            # Claude CLI (haiku) for text cleanup, uses stdin for long text
├── clipboard.py        # wl-copy + wtype wrappers
├── notifier.py         # notify-send with --replace-id for updating notifications
└── config.py           # TOML config loading, DEFAULT_PROMPT
```

## Key Implementation Details

- Heavy imports deferred until after toggle check (line ~90) for fast response when signaling stop
- Recording uses PyAudio callback mode with thread-safe buffer
- Claude prompt passed via stdin to handle long dictations
