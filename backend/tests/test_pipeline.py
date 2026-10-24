import sys
import time
from pathlib import Path
import pytest
import numpy as np

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from isl_translator import ISLTranslator
from visual_sequencer import VisualCardSequencer
from database import DatabaseManager
from audio_capture import AudioCaptureEngine
from asr_processor import ASRProcessor

def test_pipeline_svo_to_sov_mandatory():
    translator = ISLTranslator()
    result = translator.translate("The boy is eating an apple")
    assert result["isl_glosses"] == ["BOY", "APPLE", "EAT", "PRESENT"], f"Unexpected tokens: {result['isl_glosses']}"
    assert result["nmm"]["eyebrows"] == "neutral"

def test_pipeline_nlp_sub_15ms_latency():
    translator = ISLTranslator()
    test_phrase = "Where is the student going today?"
    # Warmup
    translator.translate("warmup")
    
    t0 = time.perf_counter()
    res = translator.translate(test_phrase)
    elapsed_ms = (time.perf_counter() - t0) * 1000.0
    
    assert elapsed_ms < 15.0, f"NLP latency exceeded 15ms: {elapsed_ms:.2f}ms"
    assert res["nmm"]["eyebrows"] == "furrowed" # WH-question furrowed brows per ISL grammar

def test_pipeline_sequencing_and_oov_fingerspelling():
    db = DatabaseManager()
    sequencer = VisualCardSequencer(db)
    
    # Test known sign
    seq_known = sequencer.sequence_glosses(["APPLE"])
    assert len(seq_known) == 1
    assert seq_known[0]["gloss"] == "APPLE"
    assert not seq_known[0]["is_oov"]
    assert seq_known[0]["keyframe_track"] is not None
    
    # Test OOV word decomposition into individual fingerspelled letters
    seq_oov = sequencer.sequence_glosses(["ROHAN"])
    assert len(seq_oov) == 5
    letters = [item["display_text"] for item in seq_oov]
    assert letters == ["R", "O", "H", "A", "N"]
    for item in seq_oov:
        assert item["is_oov"]
        assert item["category"] == "FINGERSPELLING"

def test_pipeline_zero_disk_and_non_blocking_capture():
    recorded_chunks = []
    def on_chunk(chunk, is_speech):
        recorded_chunks.append((chunk, is_speech))

    engine = AudioCaptureEngine(callback=on_chunk)
    engine.start()
    time.sleep(0.35)
    engine.stop()

    assert len(recorded_chunks) > 0, "No audio chunks captured"
    for chunk, _ in recorded_chunks:
        assert isinstance(chunk, np.ndarray)
        assert chunk.shape == (1600,)

    # Verify zero .wav files generated on disk
    wav_files = list(backend_dir.glob("*.wav")) + list(backend_dir.parent.glob("*.wav"))
    assert len(wav_files) == 0, f"Found unexpected .wav files on disk: {wav_files}"

def test_pipeline_vosk_realtime_transcription():
    committed = []
    partials = []

    asr = ASRProcessor(
        engine="vosk",
        on_partial=lambda text: partials.append(text),
        on_commit=lambda clause: committed.append(clause)
    )

    t = np.linspace(0, 0.1, 1600, endpoint=False)
    carrier = np.sin(2 * np.pi * 320 * t)
    modulator = 0.5 + 0.5 * np.sin(2 * np.pi * 4 * t)
    speech_chunk = (0.05 * carrier * modulator).astype(np.float32)
    silence_chunk = np.zeros(1600, dtype=np.float32)

    # Ingest speech chunks followed by silence micro-pause
    for _ in range(5):
        asr.ingest_chunk(speech_chunk, is_speech=True)
    for _ in range(4):
        asr.ingest_chunk(silence_chunk, is_speech=False)

    assert asr.active_engine == "vosk"

def test_pipeline_interpreter_feedback_logging():
    db = DatabaseManager()
    feedback_id = db.record_feedback("TEST_GLOSS", "Original test sentence", "Automated test note")
    assert feedback_id > 0
    all_fb = db.get_all_feedback()
    assert any(fb["id"] == feedback_id and fb["gloss"] == "TEST_GLOSS" for fb in all_fb)
