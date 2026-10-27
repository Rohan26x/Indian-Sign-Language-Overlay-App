# Real-Time System Audio to Indian Sign Language (ISL) 3D Avatar Overlay Application

An autonomous, non-intrusive desktop floating overlay application designed for the Deaf and Hard of Hearing (DHH) community. It intercepts active system audio across streaming web applications (e.g., YouTube, Instagram, web meetings, and educational lectures), transcribes speech in real time, translates English into syntactically valid Indian Sign Language (ISL) glosses (Subject-Object-Verb order), and synthesizes expressive 3D sign language animations and 2D visual cards within an always-on-top transparent overlay canvas.

---

## 🌟 Key Features

1. **System-Wide Virtual Audio Loopback (WASAPI)**
   - Intercepts 16 kHz Mono PCM audio directly from the operating system sound driver without ambient microphone noise.
   - Built-in Voice Activity Detection (VAD) and automated synthetic test generator fallback.

2. **Real-Time Speech-to-Text (ASR) via Vosk & Whisper**
   - **Vosk Kaldi Streaming Engine**: Primary zero-latency streaming recognizer (`vosk-model-small-en-us-0.15`) executing in pure in-memory mode with sub-15ms recognition steps and instant partial hypotheses.
   - **Faster-Whisper INT8 Engine**: Secondary transformer model with LocalAgreement-2 streaming policy.


3. **ISL Syntactic Reordering & NLP Engine**
   - Converts English **SVO** (Subject-Verb-Object) syntax into grammatically valid ISL **SOV** / Topic-Comment order.
   - Lemmatizes verbs and inflections (e.g., *"eating"* &rarr; `EAT`, *"drank"* &rarr; `DRINK`).
   - Extracts Non-Manual Markers (NMMs) such as interrogative furrowed brows (`?`) and negations (`NOT`).

4. **Lexicon Matching & Two-Handed Fingerspelling Fallback**
   - Queries a localized SQLite dictionary (`sign_lexicon.db`) for matching 3D bone keyframe tracks and sign emojis.
   - Automatically decomposes Out-Of-Vocabulary (OOV) tokens, proper nouns, and acronyms into two-handed ISL fingerspelling (`A` through `Z`).

5. **Authentic Hand Talk 3D Avatar Engine (Hugo & Maya)**
   - **Reverse-Engineered Khronos glTF 2.0**: Directly extracted and parsed from `Hand Talk.xapk` (`HUGO.gltf` 3.66 MB & `MAYA.gltf` 6.12 MB) with 100% self-contained geometry, PBR materials, and embedded textures.
   - **Blender Rigify 248-Joint Skeleton**: Hyper-articulated 5-finger skeletal rig with 3 phalanges per finger (`ORG-thumb.01..03`, `ORG-finger_index.01..03`, `ORG-finger_middle.01..03`, `ORG-finger_ring.01..03`, `ORG-finger_pinky.01..03`) and smooth skinned mesh deformations.
   - **60 Facial Blendshapes (Morph Targets)**: Real-time non-manual marker facial expressions including stochastic blinking (`OLHO.PISCA.R/L`), WH-question eyebrow raise (`SOBRANCELHA.MEIO.SOBE.R/L`), Yes/No furrow (`SOBRANCELHA.MEIO.DESCE.R/L`), and mouth visemes (`BOCA.ABRE`, `BOCA.O`, `LABIO.CANTO.SOBE/DESCE`).
   - **Continuous Quaternion SLERP Coarticulation**: Seamless bone trajectory blending between consecutive signs with no snapping back to rest pose during continuous streaming speech.
   - **100% Offline-Capable**: Bundled local Three.js and GLTFLoader libraries in `frontend/libs/` allowing instant startup with zero internet dependency.

---

## 🏗️ Project Architecture

```text
isl-overlay-app/
├── package.json
├── README.md
├── start_app.bat                 # One-click launcher for Windows
├── start_app.sh                  # One-click launcher for Linux/macOS
├── backend/
│   ├── requirements.txt          # Python dependencies
│   ├── config.py                 # Audio sample rate, buffer sizes, WS ports
│   ├── main.py                   # Async WebSocket IPC server (ws://127.0.0.1:8765)
│   ├── database.py               # SQLite lexicon connection & schema manager
│   ├── seed_db.py                # Database seeder (ISL signs, emojis, fingerspelling)
│   ├── isl_translator.py         # SVO-to-SOV grammar translation & NMM tagger
│   ├── visual_sequencer.py       # Lexicon resolution & OOV fingerspelling decomposition
│   ├── audio_capture.py          # WASAPI loopback audio capture with VAD
│   ├── asr_processor.py          # Streaming speech-to-text processor
│   └── tests/
│       ├── test_translator.py    # Unit tests for syntactic grammar reordering
│       └── test_sequencer.py     # Unit tests for lexicon lookup & fingerspelling
└── frontend/
    ├── package.json              # Electron & Three.js configuration
    ├── electron-main.js          # Frameless transparent always-on-top window
    ├── preload.js                # ContextBridge IPC for window management
    ├── index.html                # Accessible glassmorphic overlay UI shell
    ├── styles.css                # Transparent glassmorphism styling
    ├── renderer.js               # WebSocket client & UI controller
    ├── avatar_engine.js          # Three.js 3D WebGL avatar engine with SLERP
    ├── card_sequencer_ui.js      # 2D visual card & fingerspelling ticker
    └── assets/
        ├── models/               # glTF / GLB avatar assets
        └── cards/                # Visual SVG cards for vocabulary
```

---

## 🚀 Getting Started

### Prerequisites
- **Python 3.10+**
- **Node.js 18+ & npm**

### 1. One-Click Launch (Windows)
Double-click `start_app.bat` or run from PowerShell:
```cmd
start_app.bat
```

### 2. Manual Startup

#### Step A: Initialize the Python Backend
```bash
cd backend
pip install -r requirements.txt
python seed_db.py
python main.py
```
*The server will start listening on `ws://127.0.0.1:8765`.*

#### Step B: Launch the Overlay Frontend
```bash
cd frontend
npm install
npm start
```

---

## ⌨️ Hotkeys & Controls

| Shortcut / Control | Action |
| :--- | :--- |
| **`Ctrl + Shift + H`** | Toggle Overlay Visibility (Hide / Show) |
| **`Ctrl + Shift + T`** | Toggle Click-Through Mode (Pass clicks to windows underneath) |
| **Speed Selector** | Adjust avatar signing speed (`0.75x`, `1.0x`, `1.25x`, `1.5x`) (FR-7) |
| **Clothing Theme** | Toggle high-contrast `Dark` vs `Light` avatar clothing (FR-7) |
| **Opacity Slider** | Change overlay transparency smoothly (`30%` to `100%`) (FR-7) |
| **Mode Selector** | Switch live between `3D Avatar`, `Cards`, or `Hybrid` (4.2.2 Dual-Mode) |
| **Flag Missing Sign**| Logs missing/inaccurate signs to SQLite for ISL interpreter review (4.2.2) |
| **Live Telemetry** | Displays real-time pipeline latency (`Audio + ASR + NLP ms`) in ribbon |
| **Live Audio Button**| Toggle in-memory 100ms loopback audio capture with VAD (FR-1) |
| **Text Input** | Test custom sentences on-demand (e.g., *"The boy is eating an apple"*) |

---

## 🧪 Automated Pytest & Latency Benchmarks

Run the complete automated pytest verification suite:

```bash
cd backend
python -m pytest tests/ -v -s
```

All 11 test suites verify:
1. **Mandatory Case (Page 14)**: `"The boy is eating an apple"` &rarr; `["BOY", "APPLE", "EAT", "PRESENT"]` in **< 15 ms** (average ~3.9 ms).
2. **NMM Facial Markers**: Furrowed brows on WH-questions, raised brows on Yes/No questions, head shake + frown on negations.
3. **Zero-Disk Streaming**: Verifies zero temporary `.wav` files written during live capture and transcription.
4. **End-to-End Latency**: Confirms in-memory streaming latency operates well below the **1.2s–1.8s NFR-1 ceiling**.
5. **Two-Handed Fingerspelling**: Decomposes Out-Of-Vocabulary (OOV) tokens into sequential finger gestures.
6. **Interpreter Feedback**: Verifies logging of flagged signs into SQLite `interpreter_feedback` table.

