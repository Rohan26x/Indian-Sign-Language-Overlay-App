import time
import queue
import threading
from collections import deque
from typing import Optional, Callable
import numpy as np
from config import SAMPLE_RATE, CHANNELS, CHUNK_SAMPLES, VAD_ENERGY_THRESHOLD, CHUNK_DURATION_MS

class AudioCaptureEngine:
    """
    AudioCaptureEngine (FR-1, Objective 1):
    Captures live operating system audio output directly from active desktop speakers/headphones
    using Windows WASAPI loopback (soundcard / pyaudiowpatch / sounddevice) at 16 kHz mono float32 PCM
    in 100 ms chunks (1,600 samples) with <200 ms capture latency.
    Zero disk I/O, zero temporary .wav files.
    """

    def __init__(self, callback: Optional[Callable[[np.ndarray, bool], None]] = None):
        self.callback = callback
        self.running = False
        self.chunk_samples = CHUNK_SAMPLES # 1,600 samples @ 16kHz (100ms)
        self.ring_buffer = deque(maxlen=30) # Ring buffer storing last 3 seconds of 100ms chunks
        self.audio_queue = queue.Queue(maxsize=100)
        self._thread: Optional[threading.Thread] = None
        self.capture_source = "None"
        self.is_synthetic_mode = False
        self._stop_event = threading.Event()

    def _enqueue_chunk(self, chunk: np.ndarray, speech_detected: bool) -> None:
        self.ring_buffer.append(chunk)
        try:
            self.audio_queue.put_nowait((chunk, speech_detected))
        except queue.Full:
            try:
                self.audio_queue.get_nowait()
            except queue.Empty:
                pass
            try:
                self.audio_queue.put_nowait((chunk, speech_detected))
            except queue.Full:
                pass

        if self.callback:
            try:
                self.callback(chunk, speech_detected)
            except Exception as e:
                print(f"AudioCaptureEngine: callback exception: {e}")

    def calculate_rms(self, audio_data: np.ndarray) -> float:
        """Calculates Root-Mean-Square energy of the 100ms audio chunk for VAD."""
        if len(audio_data) == 0:
            return 0.0
        return float(np.sqrt(np.mean(np.square(audio_data))))

    def is_speech(self, audio_data: np.ndarray, threshold: float = VAD_ENERGY_THRESHOLD) -> bool:
        """Determines if the 100ms chunk exceeds the VAD energy floor."""
        return self.calculate_rms(audio_data) > threshold

    def start(self) -> None:
        """Starts real-time 100ms system audio loopback capture in a background thread."""
        if self.running:
            return
        self.running = True
        self._stop_event.clear()

        # Try WASAPI loopback drivers in priority order
        if self._start_soundcard_loopback():
            return
        if self._start_pyaudiowpatch_loopback():
            return
        if self._start_sounddevice_loopback():
            return

        print("AudioCaptureEngine: Hardware loopback drivers unavailable. Starting synthetic generator fallback.")
        self.is_synthetic_mode = True
        self.capture_source = "Synthetic Generator Fallback"
        self._thread = threading.Thread(target=self._synthetic_loop, daemon=True)
        self._thread.start()

    def _start_soundcard_loopback(self) -> bool:
        """Primary loopback method: soundcard WASAPI loopback."""
        try:
            import soundcard as sc
            default_spk = sc.default_speaker()
            if not default_spk:
                return False

            loopback_mic = sc.get_microphone(id=str(default_spk.name), include_loopback=True)
            if not loopback_mic:
                return False

            self.capture_source = f"soundcard (WASAPI Loopback: {default_spk.name})"
            print(f"AudioCaptureEngine: Connected to system audio loopback: {default_spk.name}")

            def loopback_worker():
                try:
                    with loopback_mic.recorder(samplerate=SAMPLE_RATE, channels=1, blocksize=self.chunk_samples) as rec:
                        while not self._stop_event.is_set():
                            data = rec.record(numframes=self.chunk_samples)
                            chunk = data.squeeze().astype(np.float32)
                            if chunk.ndim == 0:
                                chunk = np.array([chunk], dtype=np.float32)

                            self._enqueue_chunk(chunk, self.is_speech(chunk))
                except Exception as ex:
                    print(f"AudioCaptureEngine: soundcard worker stopped ({ex})")

            self._thread = threading.Thread(target=loopback_worker, daemon=True)
            self._thread.start()
            return True
        except Exception as e:
            print(f"AudioCaptureEngine: soundcard loopback initialization note: {e}")
            return False

    def _start_pyaudiowpatch_loopback(self) -> bool:
        """Secondary loopback method: pyaudiowpatch WASAPI loopback."""
        try:
            import pyaudiowpatch as pyaudio
            p = pyaudio.PyAudio()
            wasapi_info = p.get_host_api_info_by_type(pyaudio.paWASAPI)
            default_spk = p.get_device_info_by_index(wasapi_info["defaultOutputDevice"])
            
            loopback = None
            for loopback_dev in p.get_loopback_device_info_generator():
                if default_spk["name"] in loopback_dev["name"]:
                    loopback = loopback_dev
                    break
            if not loopback:
                loopback = p.get_default_wasapi_loopback()

            if not loopback:
                p.terminate()
                return False

            self.capture_source = f"pyaudiowpatch (WASAPI: {loopback['name']})"
            native_rate = int(loopback["defaultSampleRate"])
            channels = min(loopback["maxInputChannels"], 2)

            def pyaudio_worker():
                stream = p.open(
                    format=pyaudio.paFloat32,
                    channels=channels,
                    rate=native_rate,
                    input=True,
                    input_device_index=loopback["index"],
                    frames_per_buffer=int(native_rate * 0.1)
                )
                try:
                    while not self._stop_event.is_set():
                        raw_data = stream.read(int(native_rate * 0.1), exception_on_overflow=False)
                        arr = np.frombuffer(raw_data, dtype=np.float32)
                        if channels > 1:
                            arr = arr.reshape(-1, channels)[:, 0]

                        # Resample to 16kHz if needed
                        if native_rate != SAMPLE_RATE:
                            resampled_indices = np.linspace(0, len(arr) - 1, self.chunk_samples).astype(int)
                            chunk = arr[resampled_indices]
                        else:
                            chunk = arr[:self.chunk_samples]

                        chunk = chunk.astype(np.float32)
                        self._enqueue_chunk(chunk, self.is_speech(chunk))
                finally:
                    stream.stop_stream()
                    stream.close()
                    p.terminate()

            self._thread = threading.Thread(target=pyaudio_worker, daemon=True)
            self._thread.start()
            return True
        except Exception as e:
            print(f"AudioCaptureEngine: pyaudiowpatch initialization note: {e}")
            return False

    def _start_sounddevice_loopback(self) -> bool:
        """Tertiary loopback method: sounddevice Stereo Mix."""
        try:
            import sounddevice as sd
            devices = sd.query_devices()
            stereo_mix_idx = None
            for idx, dev in enumerate(devices):
                name = dev.get("name", "").lower()
                if dev.get("max_input_channels", 0) > 0 and ("stereo mix" in name or "loopback" in name):
                    stereo_mix_idx = idx
                    break

            if stereo_mix_idx is None:
                return False

            self.capture_source = f"sounddevice (Stereo Mix: {devices[stereo_mix_idx]['name']})"

            def sd_callback(indata, frames, time_info, status):
                if self._stop_event.is_set():
                    return
                data = indata[:, 0].copy() if indata.ndim > 1 else indata.copy()
                chunk = data.astype(np.float32)
                self._enqueue_chunk(chunk, self.is_speech(chunk))

            self.sd_stream = sd.InputStream(
                samplerate=SAMPLE_RATE,
                channels=CHANNELS,
                blocksize=self.chunk_samples,
                device=stereo_mix_idx,
                callback=sd_callback,
                dtype="float32"
            )
            self.sd_stream.start()
            return True
        except Exception as e:
            print(f"AudioCaptureEngine: sounddevice initialization note: {e}")
            return False

    def _synthetic_loop(self) -> None:
        """In-memory synthetic audio generator emitting 100ms chunks simulating natural speech."""
        t = 0.0
        dt = 1.0 / SAMPLE_RATE
        chunk_sec = self.chunk_samples / SAMPLE_RATE # 0.1s = 100ms
        
        while not self._stop_event.is_set():
            samples = self.chunk_samples
            time_vector = np.linspace(t, t + chunk_sec, samples, endpoint=False)
            t += chunk_sec

            carrier = np.sin(2 * np.pi * 320 * time_vector)
            modulator = 0.5 + 0.5 * np.sin(2 * np.pi * 4 * time_vector)
            chunk = (0.04 * carrier * modulator).astype(np.float32)

            self._enqueue_chunk(chunk, self.is_speech(chunk))

            time.sleep(chunk_sec)

    def stop(self) -> None:
        """Halts the in-memory capture pipeline and releases device streams."""
        self.running = False
        self._stop_event.set()
        if hasattr(self, "sd_stream") and self.sd_stream:
            try:
                self.sd_stream.stop()
                self.sd_stream.close()
            except Exception:
                pass
            self.sd_stream = None
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1.0)
        print("AudioCaptureEngine: Audio capture stopped cleanly.")
