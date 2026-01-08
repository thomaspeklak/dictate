"""Audio recording using PyAudio."""

import numpy as np
import pyaudio
import threading


class Recorder:
    """Record audio from microphone."""

    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1

    def __init__(self):
        self.audio = pyaudio.PyAudio()
        self.buffer = bytearray()
        self.is_recording = False
        self.sample_rate: int | None = None
        self._lock = threading.Lock()

    def _get_device_sample_rate(self, device_index: int | None) -> int:
        """Get the best supported sample rate for a device."""
        common_rates = [44100, 48000, 22050, 16000, 8000]

        for rate in common_rates:
            try:
                if device_index is None:
                    test_stream = self.audio.open(
                        format=self.FORMAT,
                        channels=self.CHANNELS,
                        rate=rate,
                        input=True,
                        frames_per_buffer=self.CHUNK,
                    )
                    test_stream.close()
                    return rate
                else:
                    if self.audio.is_format_supported(
                        rate,
                        input_device=device_index,
                        input_channels=self.CHANNELS,
                        input_format=self.FORMAT,
                    ):
                        return rate
            except Exception:
                continue

        return 44100  # Fallback

    def _audio_callback(self, in_data, frame_count, time_info, status):
        """Callback for audio stream."""
        with self._lock:
            if self.is_recording:
                self.buffer.extend(in_data)
        return (in_data, pyaudio.paContinue)

    def start(self, device_index: int | None = None) -> None:
        """Start recording audio."""
        self.sample_rate = self._get_device_sample_rate(device_index)
        self.buffer = bytearray()
        self.is_recording = True

        self.stream = self.audio.open(
            format=self.FORMAT,
            channels=self.CHANNELS,
            rate=self.sample_rate,
            input=True,
            input_device_index=device_index,
            frames_per_buffer=self.CHUNK,
            stream_callback=self._audio_callback,
        )
        self.stream.start_stream()

    def stop(self) -> np.ndarray:
        """Stop recording and return audio as numpy array."""
        self.is_recording = False

        if hasattr(self, "stream"):
            self.stream.stop_stream()
            self.stream.close()

        # Convert to numpy array
        with self._lock:
            audio_data = bytes(self.buffer)

        audio_np = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0

        # Resample to 16kHz if needed (Whisper expects 16kHz)
        if self.sample_rate and self.sample_rate != 16000:
            target_length = int(len(audio_np) * 16000 / self.sample_rate)
            if target_length > 0:
                audio_np = np.interp(
                    np.linspace(0, len(audio_np), target_length, endpoint=False),
                    np.arange(len(audio_np)),
                    audio_np,
                )

        return audio_np.astype(np.float32)

    def terminate(self) -> None:
        """Clean up PyAudio resources."""
        self.audio.terminate()

    def list_devices(self) -> list[dict]:
        """List available audio input devices."""
        devices = []
        for i in range(self.audio.get_device_count()):
            info = self.audio.get_device_info_by_index(i)
            if info["maxInputChannels"] > 0:
                devices.append(
                    {
                        "index": i,
                        "name": info["name"],
                        "channels": info["maxInputChannels"],
                    }
                )
        return devices
