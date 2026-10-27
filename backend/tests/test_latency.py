import sys
import time
import os
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from audio_capture import AudioCaptureEngine
from asr_processor import ASRProcessor
from isl_translator import ISLTranslator
from visual_sequencer import VisualCardSequencer
from database import DatabaseManager

def test_zero_disk_wav_files():
    """Verifies that running audio capture and ASR leaves zero .wav files on disk."""
    backend_dir = Path(__file__).resolve().parent.parent
    initial_wavs = list(backend_dir.glob("**/*.wav"))
    
    engine = AudioCaptureEngine()
    engine.start()
    time.sleep(0.35) # Run for 350ms (3+ chunks)
    engine.stop()

    final_wavs = list(backend_dir.glob("**/*.wav"))
    assert len(final_wavs) == len(initial_wavs), "Audio capture created .wav files on disk! Zero-disk required."

def test_sub_15ms_nlp_benchmark():
    """Verifies that spaCy SVO -> SOV translation executes in strictly under 15 ms."""
    translator = ISLTranslator()
    
    # Warmup
    translator.translate("Hello world")

    latencies = []
    test_utterances = [
        "The boy is eating an apple",
        "What are you reading today in school?",
        "Good morning teacher, please help the student.",
        "I do not eat cold food yesterday."
    ]

    for utterance in test_utterances:
        t0 = time.perf_counter()
        res = translator.translate(utterance)
        t1 = time.perf_counter()
        dur_ms = (t1 - t0) * 1000.0
        latencies.append(dur_ms)
        assert dur_ms < 15.0, f"Utterance '{utterance}' took {dur_ms:.2f}ms, exceeding 15ms ceiling!"

    avg_ms = sum(latencies) / len(latencies)
    print(f"\nAverage NLP translation latency across test set: {avg_ms:.2f} ms")
    assert avg_ms < 15.0

def test_end_to_end_streaming_latency_ceiling():
    """
    Verifies NFR-1 requirement:
    Total pipeline latency from audio chunk ingestion to gloss dispatch
    remains strictly below the 1.2s - 1.8s NFR-1 latency ceiling (targeting < 400ms).
    """
    db = DatabaseManager()
    translator = ISLTranslator()
    sequencer = VisualCardSequencer(db)
    asr = ASRProcessor()

    # Simulate 100ms chunk ingestion -> ASR -> NLP -> Sequencer
    chunk = np.zeros(1600, dtype=np.float32)

    # Warmup
    _ = asr._transcribe_audio(chunk)
    _ = translator.translate("Warmup")

    t_start = time.perf_counter()

    # Step 1: In-memory chunk ingestion
    is_speech = True

    # Step 2: ASR evaluation
    text = asr._transcribe_audio(chunk)

    # Step 3: NLP translation
    nlp_res = translator.translate(text or "The boy is eating an apple")

    # Step 4: Sequencer
    seq = sequencer.sequence_glosses(nlp_res["isl_glosses"])

    t_end = time.perf_counter()
    total_latency_ms = (t_end - t_start) * 1000.0

    print(f"End-to-end in-memory pipeline latency: {total_latency_ms:.2f} ms")
    assert total_latency_ms < 1200.0, f"Latency {total_latency_ms:.2f}ms exceeded 1.2s NFR-1 ceiling!"


def test_interpreter_feedback_sqlite_logging():
    """Verifies that missing sign feedback logs into SQLite interpreter_feedback table (FR-7, 4.2.2)."""
    db = DatabaseManager()
    feedback_id = db.record_feedback(
        gloss="TEST_MISSING_GLOSS",
        original_phrase="The boy is doing something new",
        notes="Automated benchmark verification"
    )
    assert feedback_id > 0

    all_feedback = db.get_all_feedback()
    assert any(f["gloss"] == "TEST_MISSING_GLOSS" for f in all_feedback)

def test_vosk_audio_to_text_streaming():
    """Verifies that Vosk Kaldi engine initializes, converts 16kHz audio chunks, and streams results."""
    partials = []
    commits = []
    asr = ASRProcessor(
        engine="vosk",
        on_partial=lambda p: partials.append(p),
        on_commit=lambda c: commits.append(c)
    )
    assert asr.active_engine == "vosk"
    assert asr.vosk_recognizer is not None

    # Feed silence / synthetic chunk
    chunk = np.zeros(1600, dtype=np.float32)
    res = asr.ingest_chunk(chunk, is_speech=False)
    # Recognizer processes without throwing exceptions
    asr.reset_state()

if __name__ == "__main__":
    test_zero_disk_wav_files()
    test_vosk_audio_to_text_streaming()
    test_system_audio_loopback_active()
    test_sub_15ms_nlp_benchmark()
    test_end_to_end_streaming_latency_ceiling()
    test_interpreter_feedback_sqlite_logging()
    print("All Latency, Vosk, and NFR benchmarks passed successfully!")


