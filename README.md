# Real-Time System Audio to Indian Sign Language (ISL) 3D Avatar Overlay Application

An autonomous, non-intrusive desktop floating overlay application designed for the Deaf and Hard of Hearing (DHH) community. It intercepts active system audio across streaming web applications (e.g., YouTube, Instagram, web meetings, and educational lectures), transcribes speech in real time, translates English into syntactically valid Indian Sign Language (ISL) glosses (Subject-Object-Verb order), and synthesizes expressive 3D sign language animations and 2D visual cards within an always-on-top transparent overlay canvas.

---

## 🌟 Key Features

1. **System-Wide Virtual Audio Loopback (WASAPI)**
   - Intercepts 16 kHz Mono PCM audio directly from the operating system sound driver without ambient microphone noise.
   - Built-in Voice Activity Detection (VAD) and automated synthetic test generator fallback.

2. **Real-Time Speech-to-Text (ASR)**
   - Streaming quantized speech recognition (faster-whisper INT8 / Vosk) delivering low-latency English transcripts.

3. **ISL Syntactic Reordering & NLP Engine**
   - Converts English **SVO** (Subject-Verb-Object) syntax into grammatically valid ISL **SOV** / Topic-Comment order.
   - Lemmatizes verbs and inflections (e.g., *"eating"* &rarr; `EAT`, *"drank"* &rarr; `DRINK`).
   - Extracts Non-Manual Markers (NMMs) such as interrogative furrowed brows (`?`) and negations (`NOT`).

4. **Lexicon Matching & Two-Handed Fingerspelling Fallback**
   - Queries a localized SQLite dictionary (`sign_lexicon.db`) for matching 3D bone keyframe tracks and sign emojis.
   - Automatically decomposes Out-Of-Vocabulary (OOV) tokens, proper nouns, and acronyms into two-handed ISL fingerspelling (`A` through `Z`).

5. **Unified Dual-Mode WebGL & Electron Overlay**
   - **3D Avatar Mode**: Procedural humanoid skeleton with Three.js bone rigging, Quaternion SLERP coarticulation, and facial NMM morph targets.
   - **Card/Emoji Mode**: 2D visual cards and emoji sequence display for instant recognition.
   - **Hybrid Mode**: Synchronized 3D Avatar gestures with live gloss/emoji subtitle ribbons.
   - Frameless, transparent, draggable, and click-through capable.

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
| **Speed Selector** | Adjust avatar signing speed (`0.75x`, `1.0x`, `1.25x`, `1.5x`) |
| **Opacity Selector** | Change overlay transparency (`100%`, `85%`, `65%`) |
| **Mode Buttons** | Switch between `3D Avatar`, `Cards`, or `Hybrid` |
| **Live Audio Button**| Toggle continuous system audio transcription |
| **Text Input** | Type custom English sentences and click `Sign` to test immediately |

---

## 🧪 Running Automated Tests

Run backend test suites verifying the grammar translation and fingerspelling decomposition:

```bash
cd backend
python tests/test_translator.py
python tests/test_sequencer.py
```
*(Both test suites assert correct Subject-Object-Verb syntactic ordering, lemmatization, NMM interrogative classification, lexicon matching, and OOV character decomposition).*
