import time
import json
from typing import Optional, Dict, Any, List, Callable
import numpy as np
from config import (
    SAMPLE_RATE,
    SLIDING_WINDOW_MS,
    MICRO_PAUSE_MS,
    VAD_ENERGY_THRESHOLD,
    LOCAL_AGREEMENT_COUNT,
    DEFAULT_ASR_ENGINE,
    VOSK_MODEL_NAME,
    WHISPER_MODEL_SIZE
)

class ASRProcessor:
    """
    ASRProcessor (FR-2, NFR-1):
    High-performance, zero-latency streaming speech-to-text processor.
    Implements Vosk Kaldi streaming recognizer as primary zero-latency engine,
    with faster-whisper (quantized INT8 CTranslate2) and simulated stream fallbacks.
    """

    def __init__(
        self,
        engine: str = DEFAULT_ASR_ENGINE,
        model_size: str = WHISPER_MODEL_SIZE,
        vosk_model_name: str = VOSK_MODEL_NAME,
        on_partial: Optional[Callable[[str], None]] = None,
        on_commit: Optional[Callable[[str], None]] = None
    ):
        self.engine_type = engine.lower() # "vosk" | "whisper"
        self.model_size = model_size
        self.vosk_model_name = vosk_model_name
        self.on_partial = on_partial
        self.on_commit = on_commit

        # Engines
        self.vosk_model = None
        self.vosk_recognizer = None
        self.whisper_model = None

        # Tracking state
        self.audio_buffer: List[np.ndarray] = []
        self.last_eval_time = time.time()
        self.eval_interval_sec = SLIDING_WINDOW_MS / 1000.0
        self.consecutive_silence_chunks = 0
        self.silence_chunk_threshold = int(MICRO_PAUSE_MS / 100) # 3 chunks = 300ms
        self.last_partial_text = ""

        # LocalAgreement-2 tracking for whisper fallback
        self.previous_hypothesis_words: List[str] = []
        self.committed_words: List[str] = []

        # Synthetic test rotation
        self.synthetic_corpus = [
            "The boy is eating an apple.",
            "What are you reading today?",
            "Good morning! Welcome to Indian Sign Language.",
            "Please help the student at school.",
            "I do not drink cold water."
        ]
        self._corpus_idx = 0
        self._token_step = 0

        self._init_engines()

    def _init_engines(self) -> None:
        """Initializes Vosk and/or faster-whisper engines."""
        # Try initializing Vosk
        try:
            import vosk
            vosk.SetLogLevel(-1) # Suppress verbose kaldi C logs
            print(f"ASRProcessor: Initializing Vosk model ('{self.vosk_model_name}')...")
            self.vosk_model = vosk.Model(model_name=self.vosk_model_name)
            self.vosk_recognizer = vosk.KaldiRecognizer(self.vosk_model, SAMPLE_RATE)
            self.vosk_recognizer.SetWords(True)
            print("ASRProcessor: Vosk Kaldi streaming recognizer successfully loaded.")
        except Exception as e:
            print(f"ASRProcessor: Vosk initialization note ({e}).")
            self.vosk_model = None
            self.vosk_recognizer = None

        # Try initializing faster-whisper
        try:
            from faster_whisper import WhisperModel
            self.whisper_model = WhisperModel(self.model_size, device="cpu", compute_type="int8")
            print(f"ASRProcessor: faster-whisper ({self.model_size} INT8) loaded successfully.")
        except Exception as e:
            print(f"ASRProcessor: faster-whisper initialization note ({e}).")
            self.whisper_model = None

        # Set active engine
        if self.engine_type == "vosk" and self.vosk_recognizer is not None:
            self.active_engine = "vosk"
        elif self.whisper_model is not None:
            self.active_engine = "whisper"
        elif self.vosk_recognizer is not None:
            self.active_engine = "vosk"
        else:
            self.active_engine = "simulator"

        print(f"ASRProcessor: Active streaming ASR engine is [{self.active_engine.upper()}].")

    def set_engine(self, engine_name: str) -> bool:
        """Switches active engine between 'vosk' and 'whisper'."""
        eng = engine_name.lower()
        if eng == "vosk" and self.vosk_recognizer is not None:
            self.active_engine = "vosk"
            self.reset_state()
            return True
        elif eng == "whisper" and self.whisper_model is not None:
            self.active_engine = "whisper"
            self.reset_state()
            return True
        return False

    def ingest_chunk(self, chunk: np.ndarray, is_speech: bool) -> Optional[Dict[str, Any]]:
        """
        Ingests a single 100ms audio chunk (1,600 samples float32).
        Dispatches streaming partial hypotheses and commits to downstream translator.
        """
        if self.active_engine == "vosk" and self.vosk_recognizer is not None:
            return self._ingest_vosk(chunk, is_speech)
        else:
            return self._ingest_sliding_window(chunk, is_speech)

    def _ingest_vosk(self, chunk: np.ndarray, is_speech: bool) -> Optional[Dict[str, Any]]:
        """Zero-latency streaming ingestion via Vosk Kaldi engine with continuous waveform feeding."""
        now = time.time()

        if is_speech:
            self.consecutive_silence_chunks = 0
        else:
            self.consecutive_silence_chunks += 1

        # Convert float32 [-1.0, 1.0] to 16-bit signed PCM byte stream
        pcm_bytes = (chunk * 32767).clip(-32768, 32767).astype(np.int16).tobytes()

        # Always feed continuous audio into Vosk recognizer so kaldi acoustic model stays continuous
        if self.vosk_recognizer.AcceptWaveform(pcm_bytes):
            res = json.loads(self.vosk_recognizer.Result())
            committed_text = res.get("text", "").strip()
            self.last_partial_text = ""
            if committed_text:
                if self.on_commit:
                    self.on_commit(committed_text)
                return {
                    "type": "commit",
                    "clause": committed_text,
                    "engine": "vosk",
                    "is_pause": False
                }
        else:
            res = json.loads(self.vosk_recognizer.PartialResult())
            partial = res.get("partial", "").strip()
            if partial:
                if partial != self.last_partial_text:
                    self.last_partial_text = partial
                    if self.on_partial:
                        self.on_partial(partial)
                    return {
                        "type": "partial",
                        "partial": partial,
                        "engine": "vosk"
                    }

        # Check for 300ms micro-pause to commit stabilized residual partial
        if self.consecutive_silence_chunks >= self.silence_chunk_threshold and self.last_partial_text:
            text = self.last_partial_text
            self.last_partial_text = ""
            self.consecutive_silence_chunks = 0
            # Reset Kaldi recognizer stream state for fresh clause
            import vosk
            self.vosk_recognizer = vosk.KaldiRecognizer(self.vosk_model, SAMPLE_RATE)
            self.vosk_recognizer.SetWords(True)
            if self.on_commit:
                self.on_commit(text)
            return {
                "type": "commit",
                "clause": text,
                "engine": "vosk",
                "is_pause": True
            }

        return None

    def _ingest_sliding_window(self, chunk: np.ndarray, is_speech: bool) -> Optional[Dict[str, Any]]:
        """Sliding-window evaluation with LocalAgreement-2 policy (Whisper & Simulator fallback)."""
        now = time.time()

        if is_speech:
            self.consecutive_silence_chunks = 0
            self.audio_buffer.append(chunk)
        else:
            self.consecutive_silence_chunks += 1

        is_micro_pause = (self.consecutive_silence_chunks >= self.silence_chunk_threshold) and (len(self.audio_buffer) > 0)
        is_eval_tick = (now - self.last_eval_time) >= self.eval_interval_sec

        if is_eval_tick or is_micro_pause:
            self.last_eval_time = now
            return self._evaluate_rolling_window(force_commit=is_micro_pause)

        return None

    def _evaluate_rolling_window(self, force_commit: bool = False) -> Optional[Dict[str, Any]]:
        """Runs ASR inference across buffered 100ms frames."""
        if not self.audio_buffer:
            return None

        concatenated_audio = np.concatenate(self.audio_buffer)
        raw_text = self._transcribe_audio(concatenated_audio)
        if not raw_text:
            return None

        current_words = raw_text.strip().split()
        if not current_words:
            return None

        partial_text = " ".join(current_words)
        if self.on_partial:
            self.on_partial(partial_text)

        commit_words = []

        if force_commit:
            uncommitted = [w for w in current_words if w not in self.committed_words]
            if uncommitted:
                commit_words = uncommitted
            self.audio_buffer.clear()
            self.previous_hypothesis_words = []
            self.committed_words.clear()
        else:
            agreement_len = 0
            min_len = min(len(current_words), len(self.previous_hypothesis_words))
            for i in range(min_len):
                if current_words[i].lower() == self.previous_hypothesis_words[i].lower():
                    agreement_len += 1
                else:
                    break

            if agreement_len >= 3:
                stable_words = current_words[:agreement_len]
                new_commit = [w for w in stable_words if w not in self.committed_words]
                if new_commit:
                    commit_words = new_commit
                    self.committed_words.extend(new_commit)

            self.previous_hypothesis_words = current_words

        if commit_words:
            committed_clause = " ".join(commit_words)
            if self.on_commit:
                self.on_commit(committed_clause)
            return {
                "type": "commit",
                "clause": committed_clause,
                "partial": partial_text,
                "engine": self.active_engine,
                "is_pause": force_commit
            }

        return {
            "type": "partial",
            "partial": partial_text,
            "engine": self.active_engine
        }

    def _transcribe_audio(self, audio_data: np.ndarray) -> str:
        """Batch audio array transcription."""
        if self.whisper_model:
            try:
                segments, info = self.whisper_model.transcribe(
                    audio_data,
                    beam_size=1,
                    language="en",
                    vad_filter=True,
                    condition_on_previous_text=False
                )
                text = " ".join([seg.text.strip() for seg in segments]).strip()
                return text
            except Exception as e:
                print(f"ASRProcessor: Whisper error: {e}")
                return ""
        elif self.vosk_recognizer is not None:
            try:
                pcm_bytes = (audio_data * 32767).clip(-32768, 32767).astype(np.int16).tobytes()
                temp_rec = vosk.KaldiRecognizer(self.vosk_model, SAMPLE_RATE)
                temp_rec.AcceptWaveform(pcm_bytes)
                res = json.loads(temp_rec.FinalResult())
                return res.get("text", "").strip()
            except Exception as e:
                return ""
        else:
            sentence = self.synthetic_corpus[self._corpus_idx % len(self.synthetic_corpus)]
            words = sentence.split()
            self._token_step += 1
            visible_count = min(self._token_step, len(words))
            emitted = " ".join(words[:visible_count])

            if visible_count >= len(words):
                self._token_step = 0
                self._corpus_idx += 1

            return emitted

    def reset_state(self) -> None:
        """Clears buffers and resets recognizer state."""
        self.audio_buffer.clear()
        self.previous_hypothesis_words.clear()
        self.committed_words.clear()
        self.consecutive_silence_chunks = 0
        self.last_partial_text = ""
        if self.vosk_recognizer is not None:
            try:
                self.vosk_recognizer.Reset()
            except Exception:
                pass
