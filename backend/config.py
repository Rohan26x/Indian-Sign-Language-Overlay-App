import os
from pathlib import Path

# Base Paths
BACKEND_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BACKEND_DIR.parent
DB_PATH = BACKEND_DIR / "sign_lexicon.db"

# Audio Capture Settings (FR-1, NFR-1)
SAMPLE_RATE = 16000              # 16 kHz Mono PCM
CHANNELS = 1
CHUNK_DURATION_MS = 100          # 100 ms audio chunks (1,600 samples)
CHUNK_SAMPLES = int(SAMPLE_RATE * (CHUNK_DURATION_MS / 1000.0))  # 1600 samples
SLIDING_WINDOW_MS = 250          # Rolling evaluation window every 250ms
MICRO_PAUSE_MS = 300             # 300 ms micro-pause commit threshold
VAD_ENERGY_THRESHOLD = 0.003     # Sensitive RMS energy floor for desktop system audio loopback
LOCAL_AGREEMENT_COUNT = 2        # LocalAgreement-2 streaming policy count

# IPC WebSocket Server
WS_HOST = "127.0.0.1"
WS_PORT = 8765

# ASR Engine Settings (FR-2, NFR-1)
DEFAULT_ASR_ENGINE = "vosk"       # "vosk" (zero-latency streaming Kaldi) | "whisper"
VOSK_MODEL_NAME = "vosk-model-small-en-us-0.15"
WHISPER_MODEL_SIZE = "tiny.en"

# Model Flags
DEFAULT_PLAYBACK_SPEED = 1.0
MIN_PLAYBACK_SPEED = 0.75
MAX_PLAYBACK_SPEED = 1.5
BACKPRESSURE_QUEUE_THRESHOLD = 4 # Accelerate playback if >= 4 signs buffered


