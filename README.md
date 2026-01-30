# Dictate

Speech-to-text dictation tool for Linux/Wayland, designed to run via keyboard shortcut. Press your hotkey to start recording, press again to stop. Your speech is transcribed locally using [faster-whisper](https://github.com/SYSTRAN/faster-whisper), optionally cleaned up by Claude, and copied to your clipboard.

## Features

- **Toggle-based recording**: First invocation starts recording, second stops and processes
- **Local transcription**: Uses faster-whisper (Whisper implementation in CTranslate2) - no cloud API for transcription
- **AI text cleanup**: Optional grammar and punctuation cleanup via Claude CLI
- **Direct typing**: Optionally type text directly at cursor position (in addition to clipboard)
- **Multi-language support**: Transcribe in any language Whisper supports
- **Desktop notifications**: Progress updates via system notifications
- **Configurable**: Customize Whisper model, audio device, and prompt template

## Requirements

### System Dependencies

Install these via your package manager:

```bash
# Fedora
sudo dnf install portaudio-devel wl-clipboard libnotify

# For --type flag (optional)
sudo dnf install wtype

# Ubuntu/Debian
sudo apt install portaudio19-dev wl-clipboard libnotify-bin

# For --type flag (optional)
sudo apt install wtype
```

### Claude CLI

The [Claude CLI](https://docs.anthropic.com/en/docs/claude-cli) is required for text cleanup (unless using `--raw` mode):

```bash
# Install via npm
npm install -g @anthropic-ai/claude-code

# Authenticate
claude login
```

### Python

Python 3.11+ is required. Using [uv](https://docs.astral.sh/uv/) is recommended.

## Installation

Clone the repository:

```bash
git clone https://github.com/yourusername/dictate.git
cd dictate
```

No additional installation steps needed - `uv` handles Python dependencies automatically.

## Usage

**This tool is designed to be triggered via a keyboard shortcut** (see [Setting Up a Keyboard Shortcut](#setting-up-a-keyboard-shortcut) below). The same shortcut both starts and stops recording.

### How the Toggle Works

1. **First press**: Starts recording (shows notification)
2. **Second press**: Stops recording → transcribes → processes → copies to clipboard

### Testing from the Shell

When testing from a terminal, run in the background with `&` (otherwise Ctrl+C would kill the recording process):

```bash
# Start recording
uv run ./dictate.py &

# Stop and process (run again in any terminal)
uv run ./dictate.py
```

### Command-Line Arguments

| Argument | Short | Description |
|----------|-------|-------------|
| `--language` | `-l` | Language code for transcription (e.g., `de`, `fr`, `es`). Default: `en` |
| `--raw` | `-r` | Skip Claude processing, output raw transcription only |
| `--type` | `-t` | Type text at cursor position via `wtype` (in addition to clipboard) |

### Examples

```bash
# Transcribe in German
uv run ./dictate.py -l de

# Raw transcription without AI cleanup
uv run ./dictate.py --raw

# Type directly at cursor AND copy to clipboard
uv run ./dictate.py --type

# Combine flags
uv run ./dictate.py -l de -r -t
```

## Setting Up a Keyboard Shortcut

### Hyprland

Add to your `hyprland.conf` or keybinds config:

```bash
# Dictate - English (Super+Ctrl+Alt+E to toggle)
bind = $mainMod CTRL ALT, e, exec, uv run ~/code/dictate/dictate.py --type

# Dictate - German
bind = $mainMod CTRL ALT, d, exec, uv run ~/code/dictate/dictate.py --type -l de

# Raw mode (no Claude processing)
bind = $mainMod SHIFT CTRL ALT, e, exec, uv run ~/code/dictate/dictate.py --type --raw
```

### Sway

Add to your `~/.config/sway/config`:

```bash
# Dictate - English (Super+Ctrl+Alt+E to toggle)
bindsym $mod+Ctrl+Alt+e exec uv run ~/code/dictate/dictate.py --type

# Dictate - German
bindsym $mod+Ctrl+Alt+d exec uv run ~/code/dictate/dictate.py --type -l de
```

### GNOME

1. Open **Settings** → **Keyboard** → **Keyboard Shortcuts** → **View and Customize Shortcuts**
2. Scroll to **Custom Shortcuts** and click **+**
3. Set:
   - Name: `Dictate`
   - Command: `uv run /full/path/to/dictate.py --type`
   - Shortcut: Your preferred key (e.g., `Super+Ctrl+Alt+E`)

### Other Desktop Environments

Configure your DE's keybinding system to run the script. The same shortcut toggles recording on/off.

## Configuration

Create or edit `config.toml` in the project directory:

```toml
[whisper]
model_size = "base"    # tiny, base, small, medium, large-v2, large-v3
device = "cpu"         # cpu or cuda
compute_type = "int8"  # int8, int16, float16, float32
language = "en"        # Default language

[audio]
# Uncomment to specify a specific audio input device index
# device = 0

[agent]
# Custom prompt template (uses {text} placeholder)
# prompt_template = """Your custom prompt here: {text}"""
```

### Whisper Models

| Model | Size | Speed | Accuracy |
|-------|------|-------|----------|
| `tiny` | 75 MB | Fastest | Lower |
| `base` | 142 MB | Fast | Good |
| `small` | 466 MB | Medium | Better |
| `medium` | 1.5 GB | Slower | High |
| `large-v3` | 3 GB | Slowest | Highest |

For CUDA acceleration, set `device = "cuda"` and use `compute_type = "float16"`.

## How It Works

1. **First run**: Creates a PID file (`/tmp/dictate.pid`) and starts recording audio
2. **Second run**: Detects running instance via PID file, sends `SIGUSR1` signal to stop
3. **Processing pipeline**:
   - Audio is resampled to 16kHz
   - faster-whisper transcribes the audio locally
   - Claude CLI cleans up grammar/punctuation (unless `--raw`)
   - Result is copied to clipboard (and typed if `--type`)
4. **Notifications**: Desktop notifications show progress at each stage

## Troubleshooting

### No audio input detected

List available audio devices and set the correct index in `config.toml`:

```python
import pyaudio
p = pyaudio.PyAudio()
for i in range(p.get_device_count()):
    info = p.get_device_info_by_index(i)
    if info["maxInputChannels"] > 0:
        print(f"{i}: {info['name']}")
```

### Claude CLI errors

Ensure you're authenticated: `claude login`

Use `--raw` mode to bypass Claude processing entirely.

### CUDA not detected

Install CUDA-compatible versions:

```bash
uv pip install nvidia-cublas-cu12 nvidia-cudnn-cu12
```

## License

MIT
