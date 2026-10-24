/**
 * Main UI Controller & Real-Time WebSocket Client for ISL Overlay Application (FR-6, FR-7).
 */

let socket = null;
let avatarEngine = null;
let cardSequencer = null;
let isRecordingAudio = false;
let isClickThrough = false;
let currentMode = 'hybrid'; // 'avatar', 'card', 'hybrid'
let lastTranslatedGlosses = [];
let lastCommittedText = "";

document.addEventListener('DOMContentLoaded', () => {
  const canvas = document.getElementById('avatar-canvas');
  const cardStage = document.getElementById('card-stage');
  const ribbonBadges = document.getElementById('gloss-badges');
  const statusDot = document.getElementById('status-dot');
  const transcriptionPreview = document.getElementById('transcription-preview');
  const textInput = document.getElementById('text-input');
  const sendBtn = document.getElementById('send-btn');
  const audioToggleBtn = document.getElementById('audio-toggle-btn');
  const speedSelect = document.getElementById('speed-select');
  const avatarSelect = document.getElementById('avatar-select');
  const themeSelect = document.getElementById('theme-select');
  const brightnessSlider = document.getElementById('brightness-slider');
  const opacitySlider = document.getElementById('opacity-slider');

  const btnClickthrough = document.getElementById('btn-clickthrough');
  const btnFeedback = document.getElementById('btn-feedback');
  const feedbackToast = document.getElementById('feedback-toast');
  const metricTotal = document.getElementById('metric-total');
  const metricNlp = document.getElementById('metric-nlp');

  // Initialize Rendering Engines
  avatarEngine = new AvatarEngine(canvas);
  cardSequencer = new CardSequencerUI(cardStage, ribbonBadges);

  // Set initial display mode (Dual-Mode: Hybrid)
  setMode('hybrid');

  // Window Controls
  document.getElementById('btn-minimize').addEventListener('click', () => {
    if (window.electronAPI) window.electronAPI.minimizeApp();
  });

  document.getElementById('btn-close').addEventListener('click', () => {
    if (window.electronAPI) window.electronAPI.closeApp();
  });

  // Click-Through Toggle
  btnClickthrough.addEventListener('click', () => {
    isClickThrough = !isClickThrough;
    if (window.electronAPI) {
      window.electronAPI.setClickThrough(isClickThrough);
    }
    btnClickthrough.style.color = isClickThrough ? '#06b6d4' : '';
    showToast(isClickThrough ? 'Click-through enabled' : 'Click-through disabled');
  });

  if (window.electronAPI && window.electronAPI.onClickThroughToggled) {
    window.electronAPI.onClickThroughToggled((enabled) => {
      isClickThrough = enabled;
      btnClickthrough.style.color = enabled ? '#06b6d4' : '';
      showToast(enabled ? 'Click-through enabled (Ctrl+Shift+T)' : 'Click-through disabled');
    });
  }

  // Speed Control (FR-7)
  speedSelect.addEventListener('change', (e) => {
    const spd = parseFloat(e.target.value);
    avatarEngine.setSpeed(spd);
    cardSequencer.setSpeed(spd);
  });

  // Avatar Character Switcher (Hugo / Maya - Hand Talk Architecture)
  if (avatarSelect) {
    avatarSelect.addEventListener('change', (e) => {
      const char = e.target.value;
      avatarEngine.setCharacter(char);
      showToast(`Avatar changed to ${char.toUpperCase()}`);
    });
  }

  // Clothing Theme Toggle (FR-7)
  themeSelect.addEventListener('change', (e) => {
    const theme = e.target.value;
    avatarEngine.setClothingTheme(theme);
  });


  // Model Brightness Slider
  if (brightnessSlider) {
    brightnessSlider.addEventListener('input', (e) => {
      const val = parseFloat(e.target.value);
      avatarEngine.setBrightness(val);
    });
  }

  // Window Opacity Slider (FR-7)
  opacitySlider.addEventListener('input', (e) => {
    const val = parseFloat(e.target.value);
    if (window.electronAPI) {
      window.electronAPI.setOpacity(val);
    }
  });

  // Flag Missing Sign / Interpreter Feedback (Section 4.2.2)
  btnFeedback.addEventListener('click', () => {
    if (!socket || socket.readyState !== WebSocket.OPEN) return;
    const glossToFlag = lastTranslatedGlosses.length > 0 ? lastTranslatedGlosses.join(' ') : 'MANUAL_FLAG';
    socket.send(JSON.stringify({
      type: 'flag_missing_sign',
      gloss: glossToFlag,
      original_phrase: lastCommittedText || textInput.value,
      notes: 'Flagged by user from overlay feedback button'
    }));
  });

  function showToast(message) {
    feedbackToast.textContent = message;
    feedbackToast.classList.add('show');
    setTimeout(() => {
      feedbackToast.classList.remove('show');
    }, 2400);
  }

  // Display Mode Selection (3D Avatar / Cards / Hybrid)
  document.querySelectorAll('.segment-btn').forEach((btn) => {
    btn.addEventListener('click', (e) => {
      document.querySelectorAll('.segment-btn').forEach(b => b.classList.remove('active'));
      e.target.classList.add('active');
      setMode(e.target.dataset.mode);
    });
  });

  function setMode(mode) {
    currentMode = mode;
    if (mode === 'avatar') {
      canvas.style.display = 'block';
      cardStage.style.display = 'none';
    } else if (mode === 'card') {
      canvas.style.display = 'none';
      cardStage.style.display = 'flex';
    } else { // hybrid
      canvas.style.display = 'block';
      cardStage.style.display = 'flex';
    }
  }

  // Submit Text Input
  function submitText() {
    const text = textInput.value.trim();
    if (text && socket && socket.readyState === WebSocket.OPEN) {
      socket.send(JSON.stringify({
        type: 'translate_text',
        text: text
      }));
      textInput.value = '';
    }
  }

  sendBtn.addEventListener('click', submitText);
  textInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') submitText();
  });

  // Audio Capture Toggle (FR-1)
  audioToggleBtn.addEventListener('click', () => {
    if (!socket || socket.readyState !== WebSocket.OPEN) return;
    if (!isRecordingAudio) {
      socket.send(JSON.stringify({ type: 'start_audio' }));
    } else {
      socket.send(JSON.stringify({ type: 'stop_audio' }));
    }
  });

  // Connect WebSocket to Python Streaming Backend
  connectWebSocket();

  function connectWebSocket() {
    socket = new WebSocket('ws://127.0.0.1:8765');

    socket.onopen = () => {
      statusDot.classList.remove('disconnected');
      statusDot.title = 'Connected to ISL Streaming Pipeline';
    };

    socket.onclose = () => {
      statusDot.classList.add('disconnected');
      statusDot.title = 'Disconnected (Reconnecting...)';
      setTimeout(connectWebSocket, 1500);
    };

    socket.onerror = () => {
      statusDot.classList.add('disconnected');
    };

    socket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);

        if (data.type === 'system_status') {
          statusDot.title = `Connected (${data.asr_engine || 'VOSK'} Engine, ${data.vocabulary_count || 51} signs)`;
        } else if (data.type === 'partial_transcription') {
          // Zero-latency streaming subtitle ticker
          transcriptionPreview.textContent = `"${data.text}..."`;

        } else if (data.type === 'isl_translation') {
          lastCommittedText = data.original_text;
          lastTranslatedGlosses = data.isl_glosses || [];

          // Update subtitle ribbon with committed utterance
          transcriptionPreview.textContent = `"${data.original_text}"`;

          // Update live telemetry metrics
          if (data.telemetry) {
            metricTotal.textContent = data.telemetry.total_pipeline_ms || '0';
            metricNlp.textContent = data.telemetry.nlp_ms || '0';
          }

          // Feed sequence to 2D card sequencer
          cardSequencer.enqueueSequence(data.sequence);

          // Feed keyframe tracks to 3D avatar engine with NMM payload
          if (data.sequence) {
            data.sequence.forEach((item, idx) => {
              const tokenNmm = (data.token_nmms && data.token_nmms[idx]) ? data.token_nmms[idx] : data.nmm;
              if (item.keyframe_track) {
                avatarEngine.playSequence(item.keyframe_track, tokenNmm);
              }
            });
          }
        } else if (data.type === 'feedback_ack') {
          showToast(`Missing sign '${data.gloss}' recorded in SQLite!`);
        } else if (data.type === 'audio_status') {
          isRecordingAudio = (data.status === 'recording');
          if (isRecordingAudio) {
            audioToggleBtn.classList.add('recording');
            audioToggleBtn.innerHTML = '<span>⏹️</span> Stop Audio';
            if (data.source) {
              audioToggleBtn.title = `Capturing System Audio: ${data.source}`;
              showToast(`Active: ${data.source}`);
            }
          } else {
            audioToggleBtn.classList.remove('recording');
            audioToggleBtn.innerHTML = '<span>🎙️</span> System Audio';
            audioToggleBtn.title = 'Capture desktop system audio loopback';
          }
        }

      } catch (err) {
        console.error('Failed to parse incoming payload:', err);
      }
    };
  }
});
