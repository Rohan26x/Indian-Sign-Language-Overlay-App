import time
import queue
import threading
import numpy as np
from typing import Optional, Callable
from config import SAMPLE_RATE, CHANNELS, CHUNK_SAMPLES, VAD_ENERGY_THRESHOLD

class AudioCaptureEngine:
    """
    Captures live system audio output at 16 kHz mono PCM using WASAPI Loopback (Windows)
    or sounddevice. Includes a synthetic fallback generator for testing and offline environments.
    """

    def __init__(self, callback: Optional[Callable[[np.ndarray], None]] = None):
        self.callback = callback
        self.running = False
        self.audio_queue = queue.Queue(maxsize=100)
        self._thread: Optional[threading.Thread] = None
        self.is_synthetic_mode = False

    def calculate_rms(self, audio_data: np.ndarray) -> float:
        """Calculates Root-Mean-Square energy of the audio chunk for VAD."""
        if len(audio_data) == 0:
            return 0.0
        return float(np.sqrt(np.mean(np.square(audio_data))))

    def is_speech(self, audio_data: np.ndarray, threshold: float = VAD_ENERGY_THRESHOLD) -> bool:
        """Determines if the audio buffer contains speech above the energy floor."""
        return self.calculate_rms(audio_data) > threshold

    def start(self) -> None:
        """Starts real-time audio capture in a background worker thread."""
        if self.running:
            return
        self.running = True

        # Attempt to initialize hardware sounddevice loopback
        started_device = False
        try:
            import sounddevice as sd
            # Check for WASAPI loopback device on Windows or default input
            devices = sd.query_devices()
            wasapi_device_id = None
            for idx, dev in enumerate(devices):
                if dev.get("max_input_channels", 0) > 0 and ("Stereo Mix" in dev["name"] or "Loopback" in dev["name"]):
                    wasapi_device_id = idx
                    break

            device_to_use = wasapi_device_id if wasapi_device_id is not None else None
            
            def sd_callback(indata, frames, time_info, status):
                if status:
                    pass
                data = indata[:, 0].copy() if indata.ndim > 1 else indata.copy()
                if self.is_speech(data):
                    self.audio_queue.put(data)
                    if self.callback:
                        self.callback(data)

            self.stream = sd.InputStream(
                samplerate=SAMPLE_RATE,
                channels=CHANNELS,
                blocksize=CHUNK_SAMPLES,
                device=device_to_use,
                callback=sd_callback,
                dtype="float32"
            )
            self.stream.start()
            started_device = True
            print("AudioCaptureEngine: Hardware audio stream successfully started.")
        except Exception as e:
            print(f"AudioCaptureEngine: Hardware audio device unavailable ({e}). Starting synthetic generator fallback.")
            self.is_synthetic_mode = True

        if not started_device:
            self._thread = threading.Thread(target=self._synthetic_loop, daemon=True)
            self._thread.start()

    def _synthetic_loop(self) -> None:
        """Generates periodic synthetic audio buffers to simulate streaming audio input."""
        t = 0.0
        dt = 1.0 / SAMPLE_RATE
        while self.running:
            # Generate 1-second chunks with gentle modulated tone simulating speech
            samples = CHUNK_SAMPLES
            time_vector = np.linspace(t, t + CHUNK_SAMPLES * dt, samples, endpoint=False)
            t += CHUNK_SAMPLES * dt

            # Modulated speech-like waveform
            chunk = 0.05 * np.sin(2 * np.pi * 440 * time_vector) * (0.5 + 0.5 * np.sin(2 * np.pi * 3 * time_vector))
            chunk = chunk.astype(np.float32)

            if self.is_speech(chunk):
                self.audio_queue.put(chunk)
                if self.callback:
                    self.callback(chunk)

            time.sleep(CHUNK_SAMPLES / SAMPLE_RATE)

    def stop(self) -> None:
        """Stops the audio ingestion thread and releases device streams."""
        self.running = False
        if hasattr(self, "stream") and self.stream:
            try:
                self.stream.stop()
                self.stream.close()
            except Exception:
                pass
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1.0)
        print("AudioCaptureEngine: Audio capture stopped.")
