import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from isl_translator import ISLTranslator

def test_svo_to_sov_translation():
    translator = ISLTranslator()
    
    # "The boy is eating an apple" -> [BOY, APPLE, EAT]
    res1 = translator.translate("The boy is eating an apple.")
    assert "BOY" in res1["isl_glosses"]
    assert "APPLE" in res1["isl_glosses"]
    assert "EAT" in res1["isl_glosses"]
    assert res1["nmm"] == "neutral"

def test_question_nmm_extraction():
    translator = ISLTranslator()
    
    # "What are you reading?" -> Question marker placed at end + NMM question
    res = translator.translate("What are you reading?")
    assert res["is_question"] is True
    assert res["nmm"] == "question"
    assert "WHAT" in res["isl_glosses"]

def test_lemmatization():
    translator = ISLTranslator()
    assert translator.lemmatize_token("eating") == "EAT"
    assert translator.lemmatize_token("drank") == "DRINK"
    assert translator.lemmatize_token("books") == "BOOK"
    assert translator.lemmatize_token("studied") == "STUDY"

def test_negation_detection():
    translator = ISLTranslator()
    res = translator.translate("I do not like bad water.")
    assert res["nmm"] == "negation"

if __name__ == "__main__":
    test_svo_to_sov_translation()
    test_question_nmm_extraction()
    test_lemmatization()
    test_negation_detection()
    print("All ISLTranslator tests passed successfully!")
