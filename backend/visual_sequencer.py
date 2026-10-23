from typing import List, Dict, Any
from database import DatabaseManager

class VisualCardSequencer:
    """
    Resolves translated ISL gloss tokens against the local lexicon database.
    If a gloss is in the vocabulary, dispatches its 3D animation keyframes and 2D sign card/emoji.
    If a gloss is Out-Of-Vocabulary (OOV) or a proper noun, decomposes the token into
    individual characters and dispatches two-handed ISL fingerspelling fallback frames.
    """

    def __init__(self, db_manager: DatabaseManager = None):
        self.db = db_manager or DatabaseManager()

    def sequence_glosses(self, glosses: List[str]) -> List[Dict[str, Any]]:
        """
        Processes a list of ISL gloss strings and returns an animation & visual card sequence.
        """
        sequence = []

        for gloss in glosses:
            clean_gloss = gloss.strip().upper()
            if not clean_gloss:
                continue

            sign_data = self.db.lookup_sign(clean_gloss)
            if sign_data:
                sequence.append({
                    "gloss": sign_data["gloss"],
                    "display_text": sign_data["gloss"],
                    "category": sign_data["category"],
                    "emoji": sign_data["emoji"],
                    "card_asset": sign_data["card_asset"],
                    "keyframe_track": sign_data.get("keyframe_track"),
                    "nmm_expression": sign_data.get("nmm_expression") or "neutral",
                    "is_oov": False,
                    "fingerspelling": False
                })
            else:
                # Out-Of-Vocabulary (OOV) Fallback: Two-handed fingerspelling decomposition
                letters = [c for c in clean_gloss if c.isalnum()]
                if not letters:
                    continue

                for char in letters:
                    fs_data = self.db.lookup_fingerspelling(char)
                    if fs_data:
                        sequence.append({
                            "gloss": f"{clean_gloss}[{char}]",
                            "display_text": char,
                            "parent_token": clean_gloss,
                            "category": "FINGERSPELLING",
                            "emoji": "🔤",
                            "card_asset": fs_data["card_asset"],
                            "keyframe_track": fs_data.get("keyframe_track"),
                            "nmm_expression": "neutral",
                            "is_oov": True,
                            "fingerspelling": True
                        })
                    else:
                        sequence.append({
                            "gloss": f"{clean_gloss}[{char}]",
                            "display_text": char,
                            "parent_token": clean_gloss,
                            "category": "UNKNOWN",
                            "emoji": "❓",
                            "card_asset": "cards/unknown.svg",
                            "keyframe_track": None,
                            "nmm_expression": "neutral",
                            "is_oov": True,
                            "fingerspelling": True
                        })

        return sequence
