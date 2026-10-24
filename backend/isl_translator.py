import re
import time
from typing import List, Dict, Any, Tuple, Optional

# Non-Manual Markers (NMM) Presets (Section 2.2 Gap 3 & Section 4.1 Stage 5)
NMM_WH_QUESTION = {
    "eyebrows": "furrowed",
    "headTilt": 0.25,
    "headShake": False,
    "mouth": "open_small"
}

NMM_YES_NO_QUESTION = {
    "eyebrows": "raised",
    "headTilt": 0.18,
    "headShake": False,
    "mouth": "neutral"
}

NMM_NEGATION = {
    "eyebrows": "furrowed",
    "headTilt": 0.0,
    "headShake": True,
    "mouth": "frown"
}

NMM_DECLARATIVE = {
    "eyebrows": "neutral",
    "headTilt": 0.0,
    "headShake": False,
    "mouth": "neutral"
}

# Stopwords and functional words stripped in Indian Sign Language (FR-3)
ISL_STOPWORDS = {
    "a", "an", "the", "is", "am", "are", "was", "were", "be", "been", "being",
    "do", "does", "did", "to", "of", "for", "with", "at", "by", "from", "in", "on", "into", "onto"
}

# Interrogative words placed in final topic-comment position in ISL
WH_WORDS = {"what", "where", "who", "why", "how", "when", "which"}

# Time / Topic indicator lemmas
TIME_WORDS = {
    "today", "tomorrow", "yesterday", "now", "currently", "morning", "afternoon",
    "evening", "night", "daily", "daily", "soon", "later", "before", "after"
}

# Common irregular verb lemmatizations
IRREGULAR_LEMMAS = {
    "ate": "eat", "eating": "eat", "eats": "eat",
    "drank": "drink", "drinking": "drink", "drinks": "drink",
    "went": "go", "going": "go", "goes": "go", "gone": "go",
    "came": "come", "coming": "come", "comes": "come",
    "saw": "see", "seeing": "see", "sees": "see", "seen": "see",
    "read": "read", "reading": "read", "reads": "read",
    "wrote": "write", "writing": "write", "writes": "write", "written": "write",
    "playing": "play", "plays": "play", "played": "play",
    "studying": "study", "studies": "study", "studied": "study",
    "helping": "help", "helps": "help", "helped": "help"
}

class ISLTranslator:
    """
    Translates English utterances into syntactically valid Indian Sign Language (ISL)
    gloss representations following Subject-Object-Verb (SOV) and Topic-Comment order,
    extracting Non-Manual Markers (NMMs) based on dependency grammar analysis (FR-3, Objective 3).
    """

    def __init__(self):
        self.nlp = None
        try:
            import spacy
            if spacy.util.is_package("en_core_web_sm"):
                self.nlp = spacy.load("en_core_web_sm")
            else:
                self.nlp = None
        except Exception as e:
            print(f"ISLTranslator: spaCy model load warning ({e}). Using deterministic fallback.")
            self.nlp = None

    def lemmatize_token(self, token: str) -> str:
        """Strips inflections and plural suffixes to root gloss."""
        t_lower = token.lower()
        if t_lower in IRREGULAR_LEMMAS:
            return IRREGULAR_LEMMAS[t_lower].upper()
        
        if t_lower.endswith("ing") and len(t_lower) > 5:
            return t_lower[:-3].upper()
        if t_lower.endswith("ed") and len(t_lower) > 4:
            return t_lower[:-2].upper()
        if t_lower.endswith("s") and not t_lower.endswith("ss") and len(t_lower) > 3:
            return t_lower[:-1].upper()
            
        return token.upper()

    def detect_nmm(self, text: str) -> Tuple[Dict[str, Any], bool, bool, bool]:
        """
        Determines the grammatical Non-Manual Marker (NMM) dictionary based on sentence syntax.
        Returns: (nmm_dict, is_question, is_wh_question, has_negation)
        """
        lower = text.lower().strip()
        words = re.findall(r"\b\w+\b", lower)

        is_wh = any(w in WH_WORDS for w in words)
        is_question = lower.endswith("?") or is_wh or any(lower.startswith(q) for q in ["is ", "are ", "do ", "does ", "can ", "will ", "did ", "should "])
        has_neg = bool(re.search(r"\b(not|no|never|don't|didn't|cannot|can't|won't|isn't|aren't|wasn't|weren't)\b", lower))

        if is_wh:
            return dict(NMM_WH_QUESTION), True, True, has_neg
        elif is_question:
            return dict(NMM_YES_NO_QUESTION), True, False, has_neg
        elif has_neg:
            return dict(NMM_NEGATION), False, False, True
        else:
            return dict(NMM_DECLARATIVE), False, False, False

    def translate(self, text: str) -> Dict[str, Any]:
        """
        Translates an English sentence string into an ISL gloss stream with SOV reordering
        and Non-Manual Markers (NMMs) in <15 ms.
        """
        clean_text = text.strip()
        if not clean_text:
            return {
                "original_text": "",
                "isl_glosses": [],
                "nmm": dict(NMM_DECLARATIVE),
                "token_nmms": [],
                "is_question": False,
                "is_wh_question": False,
                "has_negation": False,
                "parse_latency_ms": 0.0
            }

        start_time = time.perf_counter()
        nmm_dict, is_question, is_wh, has_neg = self.detect_nmm(clean_text)

        if self.nlp:
            glosses = self._translate_spacy(clean_text)
        else:
            glosses = self._translate_rule_based(clean_text)

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        # Create token-level NMM markers
        token_nmms = [dict(nmm_dict) for _ in glosses]

        return {
            "original_text": clean_text,
            "isl_glosses": glosses,
            "nmm": nmm_dict,
            "token_nmms": token_nmms,
            "is_question": is_question,
            "is_wh_question": is_wh,
            "has_negation": has_neg,
            "parse_latency_ms": round(latency_ms, 2)
        }

    def _translate_spacy(self, text: str) -> List[str]:
        """
        Uses spaCy dependency parsing for incremental clause segmentation and constituent
        reordering into ISL SOV syntax:
        [TIME / TOPIC] + [SUBJECT] + [OBJECT] + [VERB] + [TENSE MARKER] + [NEGATION / WH-QUESTION]
        """
        doc = self.nlp(text)
        
        # Check for multi-clause segmentation on coordinating conjunctions (cc) or markers
        clauses = []
        current_clause_tokens = []
        for token in doc:
            if token.dep_ in ("cc", "mark") and current_clause_tokens:
                clauses.append(current_clause_tokens)
                current_clause_tokens = []
            current_clause_tokens.append(token)
        if current_clause_tokens:
            clauses.append(current_clause_tokens)

        all_glosses = []
        for clause_tokens in clauses:
            clause_glosses = self._parse_single_clause(clause_tokens)
            all_glosses.extend(clause_glosses)

        # Fallback if empty
        if not all_glosses:
            all_glosses = [
                t.lemma_.upper() for t in doc 
                if not t.is_punct and t.text.lower() not in ISL_STOPWORDS
            ]

        return all_glosses

    def _parse_single_clause(self, tokens: list) -> List[str]:
        """Parses a single syntactic clause into ISL SOV constituents."""
        time_tokens = []
        subject_tokens = []
        object_tokens = []
        verb_tokens = []
        tense_tokens = []
        question_tokens = []
        negation_tokens = []
        other_tokens = []

        has_progressive = False
        has_past = False
        has_future = False

        for token in tokens:
            t_lower = token.text.lower()
            lemma = token.lemma_.upper() if token.lemma_ else self.lemmatize_token(token.text)

            # Skip punctuation
            if token.is_punct:
                continue

            # Detect tense from auxiliaries and verb forms
            if token.tag_ == "VBG" or (token.tag_ == "VBZ" and t_lower in ("is", "'s")):
                has_progressive = True
            if token.tag_ == "VBD" or t_lower in ("was", "were", "did", "ate", "went", "saw"):
                has_past = True
            if t_lower in ("will", "shall", "going"):
                has_future = True

            # Interrogatives
            if t_lower in WH_WORDS:
                question_tokens.append(t_lower.upper())
                continue

            # Negation
            if t_lower in ("not", "no", "never", "n't"):
                negation_tokens.append("NOT")
                continue

            # Skip auxiliary copulas & stopwords
            if t_lower in ISL_STOPWORDS:
                continue

            # Time / Topic Modifiers
            if t_lower in TIME_WORDS or token.ent_type_ in ("DATE", "TIME"):
                time_tokens.append(lemma)
            # Subjects
            elif "subj" in token.dep_:
                subject_tokens.append(lemma)
            # Objects
            elif "obj" in token.dep_ or token.dep_ in ("attr", "dative", "oprd"):
                object_tokens.append(lemma)
            # Verbs (Action verbs)
            elif token.pos_ == "VERB" or ("ROOT" in token.dep_ and token.pos_ != "PUNCT"):
                # Normalize copulas if accidentally tagged as main verb
                if lemma not in ("BE", "IS", "ARE", "WAS", "WERE"):
                    verb_tokens.append(lemma)
            else:
                other_tokens.append(lemma)

        # Determine ISL Tense Marker (Page 14 Specification: "The boy is eating an apple" -> BOY APPLE EAT PRESENT)
        if has_progressive or any(t.text.lower() in ("is", "am", "are") for t in tokens):
            tense_tokens.append("PRESENT")
        elif has_past:
            tense_tokens.append("PAST")
        elif has_future:
            tense_tokens.append("FUTURE")

        # Synthesize ISL Order: [TIME/TOPIC] + [SUBJECT] + [OBJECT] + [VERB] + [TENSE] + [NEG/Q]
        result = []
        result.extend(time_tokens)
        result.extend(subject_tokens)
        result.extend(object_tokens)
        result.extend(other_tokens)
        result.extend(verb_tokens)
        result.extend(tense_tokens)
        result.extend(negation_tokens)
        result.extend(question_tokens)

        return result

    def _translate_rule_based(self, text: str) -> List[str]:
        """
        Fast deterministic fallback parser:
        Extracts Subject, Object, Verb, and Tense markers into SOV sequence.
        """
        normalized = re.sub(r"[^\w\s\?]", "", text)
        words = normalized.split()
        if not words:
            return []

        subjects = []
        verbs = []
        objects = []
        tense_tokens = []
        question_tokens = []
        negation_tokens = []
        other_tokens = []

        pronouns_and_nouns = {
            "i", "you", "he", "she", "it", "we", "they", "boy", "girl", "man", "woman",
            "teacher", "student", "apple", "book", "water", "school", "home", "india"
        }
        known_verbs = {
            "eat", "ate", "eating", "eats", "drink", "drank", "drinking", "drinks",
            "read", "reading", "reads", "write", "writing", "wrote", "go", "going", "went",
            "come", "coming", "came", "see", "seeing", "saw", "look", "watch",
            "help", "study", "play"
        }

        has_is = any(w.lower() in ("is", "am", "are") for w in words)
        has_was = any(w.lower() in ("was", "were", "did") for w in words)

        for w in words:
            w_lower = w.lower()
            if w_lower in WH_WORDS:
                question_tokens.append(w_lower.upper())
            elif w_lower in ("not", "no", "never"):
                negation_tokens.append("NOT")
            elif w_lower in ISL_STOPWORDS:
                continue
            else:
                lemma = self.lemmatize_token(w)
                if w_lower in known_verbs:
                    verbs.append(lemma)
                    if has_is or w_lower.endswith("ing"):
                        tense_tokens.append("PRESENT")
                    elif has_was:
                        tense_tokens.append("PAST")
                elif len(subjects) == 0 and w_lower in pronouns_and_nouns:
                    subjects.append(lemma)
                elif w_lower in pronouns_and_nouns:
                    objects.append(lemma)
                else:
                    other_tokens.append(lemma)

        reordered = subjects + objects + other_tokens + verbs + tense_tokens + negation_tokens + question_tokens
        return reordered or [self.lemmatize_token(w) for w in words if w.lower() not in ISL_STOPWORDS]
