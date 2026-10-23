/**
 * Main UI Controller & WebSocket Client for ISL Overlay Application.
 */

let socket = null;
let avatarEngine = null;
let cardSequencer = null;
let isRecordingAudio = false;
let currentMode = 'hybrid'; // 'avatar', 'card', 'hybrid'

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
  const opacitySelect = document.getElementById('opacity-select');

  // Initialize Rendering Engines
  avatarEngine = new AvatarEngine(canvas);
  cardSequencer = new CardSequencerUI(cardStage, ribbonBadges);

  // Set initial display mode
  setMode('hybrid');

  // Window Controls
  document.getElementById('btn-minimize').addEventListener('click', () => {
    if (window.electronAPI) window.electronAPI.minimizeApp();
  });

  document.getElementById('btn-close').addEventListener('click', () => {
    if (window.electronAPI) window.electronAPI.closeApp();
  });

  // Speed Adjustment
  speedSelect.addEventListener('change', (e) => {
    const spd = parseFloat(e.target.value);
    avatarEngine.setSpeed(spd);
    cardSequencer.setSpeed(spd);
  });

  // Opacity Adjustment
  if (opacitySelect) {
    opacitySelect.addEventListener('change', (e) => {
      const op = parseFloat(e.target.value);
      if (window.electronAPI) window.electronAPI.setOpacity(op);
    });
  }

  // Mode Selection (Avatar / Cards / Hybrid)
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

  // Send Direct Text
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

  // Audio Toggle
  audioToggleBtn.addEventListener('click', () => {
    if (!socket || socket.readyState !== WebSocket.OPEN) return;
    if (!isRecordingAudio) {
      socket.send(JSON.stringify({ type: 'start_audio' }));
    } else {
      socket.send(JSON.stringify({ type: 'stop_audio' }));
    }
  });

  // Connect WebSocket to Python Backend
  connectWebSocket();

  function connectWebSocket() {
    socket = new WebSocket('ws://127.0.0.1:8765');

    socket.onopen = () => {
      statusDot.classList.remove('disconnected');
      statusDot.title = 'Connected to Backend';
    };

    socket.onclose = () => {
      statusDot.classList.add('disconnected');
      statusDot.title = 'Disconnected (Reconnecting...)';
      setTimeout(connectWebSocket, 2000);
    };

    socket.onerror = () => {
      statusDot.classList.add('disconnected');
    };

    socket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);

        if (data.type === 'isl_translation') {
          // Update transcription ribbon
          transcriptionPreview.textContent = `"${data.original_text}"`;

          // Feed sequence to 2D card sequencer
          cardSequencer.enqueueSequence(data.sequence);

          // Feed bone tracks to 3D avatar engine
          data.sequence.forEach((item) => {
            if (item.keyframe_track) {
              avatarEngine.playSequence(item.keyframe_track, data.nmm);
            }
          });
        } else if (data.type === 'audio_status') {
          isRecordingAudio = (data.status === 'recording');
          if (isRecordingAudio) {
            audioToggleBtn.classList.add('recording');
            audioToggleBtn.innerHTML = '<span>⏹️</span> Stop Audio';
          } else {
            audioToggleBtn.classList.remove('recording');
            audioToggleBtn.innerHTML = '<span>🎙️</span> Live Audio';
          }
        }
      } catch (err) {
        console.error('Failed to parse incoming payload:', err);
      }
    };
  }
});
