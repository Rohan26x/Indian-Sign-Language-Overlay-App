import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from isl_translator import ISLTranslator

def test_mandatory_boy_eating_apple():
    """Verifies mandatory Page 14 test case: 'The boy is eating an apple' -> ['BOY', 'APPLE', 'EAT', 'PRESENT'] in <15 ms."""
    translator = ISLTranslator()
    res = translator.translate("The boy is eating an apple")
    
    assert res["isl_glosses"] == ["BOY", "APPLE", "EAT", "PRESENT"], f"Expected ['BOY', 'APPLE', 'EAT', 'PRESENT'], got {res['isl_glosses']}"
    assert res["nmm"]["eyebrows"] == "neutral"
    assert res["nmm"]["headTilt"] == 0.0
    assert res["nmm"]["headShake"] is False
    assert res["parse_latency_ms"] < 15.0, f"Parse latency {res['parse_latency_ms']}ms exceeded 15ms ceiling"

def test_wh_question_nmm():
    """Verifies WH-question syntax and furrowed eyebrows NMM dictionary."""
    translator = ISLTranslator()
    res = translator.translate("What are you reading?")
    
    assert res["is_question"] is True
    assert res["is_wh_question"] is True
    assert res["nmm"]["eyebrows"] == "furrowed"
    assert res["nmm"]["headTilt"] == 0.25
    assert res["nmm"]["headShake"] is False
    assert res["nmm"]["mouth"] == "open_small"
    assert "WHAT" in res["isl_glosses"]
    assert res["parse_latency_ms"] < 15.0

def test_yes_no_question_nmm():
    """Verifies Yes/No question syntax and raised eyebrows NMM dictionary."""
    translator = ISLTranslator()
    res = translator.translate("Are you happy?")
    
    assert res["is_question"] is True
    assert res["nmm"]["eyebrows"] == "raised"
    assert res["nmm"]["headTilt"] == 0.18
    assert res["nmm"]["mouth"] == "neutral"
    assert res["parse_latency_ms"] < 15.0

def test_negation_nmm():
    """Verifies negation syntax, head shake, and frown mouth NMM dictionary."""
    translator = ISLTranslator()
    res = translator.translate("I do not eat apple")
    
    assert res["has_negation"] is True
    assert res["nmm"]["headShake"] is True
    assert res["nmm"]["eyebrows"] == "furrowed"
    assert res["nmm"]["mouth"] == "frown"
    assert "NOT" in res["isl_glosses"]
    assert res["parse_latency_ms"] < 15.0

def test_lemmatization():
    translator = ISLTranslator()
    assert translator.lemmatize_token("eating") == "EAT"
    assert translator.lemmatize_token("drank") == "DRINK"
    assert translator.lemmatize_token("books") == "BOOK"
    assert translator.lemmatize_token("studied") == "STUDY"

if __name__ == "__main__":
    test_mandatory_boy_eating_apple()
    test_wh_question_nmm()
    test_yes_no_question_nmm()
    test_negation_nmm()
    test_lemmatization()
    print("All ISLTranslator tests passed successfully!")
