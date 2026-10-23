import re
from typing import List, Dict, Any, Tuple

# Stopwords and functional words stripped in Indian Sign Language
ISL_STOPWORDS = {
    "a", "an", "the", "is", "am", "are", "was", "were", "be", "been", "being",
    "do", "does", "did", "to", "of", "for", "with", "at", "by", "from", "in", "on"
}

# Question words that in ISL are placed at the end of the sentence (Topic-Comment order)
QUESTION_WORDS = {"what", "where", "who", "why", "when", "how", "which"}

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
    Translates English sentences into syntactically valid Indian Sign Language (ISL)
    gloss representations following Subject-Object-Verb (SOV) and Topic-Comment order,
    extracting Non-Manual Markers (NMMs) such as interrogatives and negations.
    """

    def __init__(self):
        self.nlp = None
        try:
            import spacy
            # Attempt to load small English model if installed
            if spacy.util.is_package("en_core_web_sm"):
                self.nlp = spacy.load("en_core_web_sm")
        except Exception:
            self.nlp = None

    def lemmatize_token(self, token: str) -> str:
        """Strips inflections, plural endings, and verb tenses to root gloss."""
        t_lower = token.lower()
        if t_lower in IRREGULAR_LEMMAS:
            return IRREGULAR_LEMMAS[t_lower].upper()
        
        # Simple rule-based stemming for regular verbs
        if t_lower.endswith("ing") and len(t_lower) > 5:
            return t_lower[:-3].upper()
        if t_lower.endswith("ed") and len(t_lower) > 4:
            return t_lower[:-2].upper()
        if t_lower.endswith("s") and not t_lower.endswith("ss") and len(t_lower) > 3:
            return t_lower[:-1].upper()
            
        return token.upper()

    def translate(self, text: str) -> Dict[str, Any]:
        """
        Translates an English sentence string to an ISL gloss stream and NMM tags.
        Returns a dict:
        {
            "original_text": str,
            "isl_glosses": List[str],
            "nmm": str, # "neutral", "question", "negation", "smile"
            "is_question": bool
        }
        """
        clean_text = text.strip()
        if not clean_text:
            return {
                "original_text": "",
                "isl_glosses": [],
                "nmm": "neutral",
                "is_question": False
            }

        is_question = clean_text.endswith("?") or any(w in clean_text.lower().split() for w in QUESTION_WORDS)
        has_negation = bool(re.search(r"\b(not|no|never|don't|didn't|cannot|won't)\b", clean_text, re.IGNORECASE))

        nmm = "neutral"
        if is_question:
            nmm = "question"
        elif has_negation:
            nmm = "negation"

        if self.nlp:
            glosses = self._translate_spacy(clean_text)
        else:
            glosses = self._translate_rule_based(clean_text)

        return {
            "original_text": clean_text,
            "isl_glosses": glosses,
            "nmm": nmm,
            "is_question": is_question
        }

    def _translate_spacy(self, text: str) -> List[str]:
        """Uses spaCy dependency parsing to isolate Subject, Object, Verb, and reorder to SOV."""
        doc = self.nlp(text)
        subjects = []
        objects = []
        verbs = []
        others = []
        question_tokens = []

        for token in doc:
            t_lower = token.text.lower()
            if t_lower in ISL_STOPWORDS or token.is_punct:
                continue

            lemma = token.lemma_.upper() if token.lemma_ else self.lemmatize_token(token.text)

            if t_lower in QUESTION_WORDS:
                question_tokens.append(lemma)
            elif "subj" in token.dep_:
                subjects.append(lemma)
            elif "obj" in token.dep_ or token.dep_ in ("attr", "dative"):
                objects.append(lemma)
            elif token.pos_ == "VERB" or "ROOT" in token.dep_:
                verbs.append(lemma)
            else:
                others.append(lemma)

        # Reconstruct in ISL Order: Others (Time/Location) -> Subject -> Object -> Verb -> Question/NMM
        result = others + subjects + objects + verbs + question_tokens
        return result or [self.lemmatize_token(t.text) for t in doc if not t.is_punct and t.text.lower() not in ISL_STOPWORDS]

    def _translate_rule_based(self, text: str) -> List[str]:
        """
        Fast deterministic fallback parser:
        Extracts Subject, Verb, Object, and moves question markers to the end.
        Handles SVO -> SOV reordering.
        """
        # Remove punctuation except question mark
        normalized = re.sub(r"[^\w\s\?]", "", text)
        words = normalized.split()
        if not words:
            return []

        subjects = []
        verbs = []
        objects = []
        question_tokens = []
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

        # Step 1: Filter out stopwords
        filtered = []
        for w in words:
            w_clean = w.replace("?", "").lower()
            if not w_clean:
                continue
            if w_clean in QUESTION_WORDS:
                question_tokens.append(w_clean.upper())
            elif w_clean not in ISL_STOPWORDS:
                filtered.append(w_clean)

        # Step 2: Separate Subject, Object, Verb
        for w in filtered:
            lemma = self.lemmatize_token(w)
            if w in known_verbs:
                verbs.append(lemma)
            elif len(subjects) == 0 and w in pronouns_and_nouns:
                subjects.append(lemma)
            elif w in pronouns_and_nouns:
                objects.append(lemma)
            else:
                other_tokens.append(lemma)

        # Step 3: Compose SOV sequence: [Time/Others] -> [Subject] -> [Object] -> [Verb] -> [Question]
        # In ISL: "Boy eat apple" -> "BOY APPLE EAT"
        reordered = []
        if subjects:
            reordered.extend(subjects)
        if objects:
            reordered.extend(objects)
        if other_tokens:
            reordered.extend(other_tokens)
        if verbs:
            reordered.extend(verbs)
        if question_tokens:
            reordered.extend(question_tokens)

        # Fallback if categories were not identified: return filtered words in order
        if not reordered:
            reordered = [self.lemmatize_token(w) for w in filtered]

        return reordered
