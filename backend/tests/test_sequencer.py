import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from database import DatabaseManager
from visual_sequencer import VisualCardSequencer

def test_lexicon_lookup():
    db = DatabaseManager()
    sequencer = VisualCardSequencer(db)

    # Known vocabulary words
    seq = sequencer.sequence_glosses(["HELLO", "APPLE", "EAT"])
    assert len(seq) == 3
    assert seq[0]["gloss"] == "HELLO"
    assert seq[0]["is_oov"] is False
    assert seq[0]["emoji"] == "👋"
    assert seq[1]["gloss"] == "APPLE"
    assert seq[2]["gloss"] == "EAT"

def test_oov_fingerspelling_decomposition():
    db = DatabaseManager()
    sequencer = VisualCardSequencer(db)

    # Out-Of-Vocabulary proper noun (e.g., "ROHAN")
    seq = sequencer.sequence_glosses(["ROHAN"])
    assert len(seq) == 5  # R - O - H - A - N
    for item in seq:
        assert item["is_oov"] is True
        assert item["fingerspelling"] is True
        assert item["category"] == "FINGERSPELLING"

    assert seq[0]["display_text"] == "R"
    assert seq[1]["display_text"] == "O"
    assert seq[2]["display_text"] == "H"
    assert seq[3]["display_text"] == "A"
    assert seq[4]["display_text"] == "N"

if __name__ == "__main__":
    test_lexicon_lookup()
    test_oov_fingerspelling_decomposition()
    print("All VisualCardSequencer tests passed successfully!")
