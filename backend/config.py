import os
from pathlib import Path

# Base Paths
BACKEND_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BACKEND_DIR.parent
DB_PATH = BACKEND_DIR / "sign_lexicon.db"

# Audio Capture Settings
SAMPLE_RATE = 16000          # 16 kHz Mono PCM
CHANNELS = 1
CHUNK_DURATION_SEC = 1.0     # 1 second rolling buffer
CHUNK_SAMPLES = int(SAMPLE_RATE * CHUNK_DURATION_SEC)
VAD_ENERGY_THRESHOLD = 0.012 # RMS energy floor for speech detection

# IPC WebSocket Server
WS_HOST = "127.0.0.1"
WS_PORT = 8765

# Model Flags
USE_SYNTHETIC_AUDIO_FALLBACK = True
DEFAULT_PLAYBACK_SPEED = 1.0
MIN_PLAYBACK_SPEED = 0.75
MAX_PLAYBACK_SPEED = 1.5
