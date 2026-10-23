import json
from database import DatabaseManager

def generate_sample_keyframes(gesture_type: str = "wave") -> list:
    """
    Generates procedural bone transform keyframes for Three.js skeletal playback.
    Bones: RightArm, LeftArm, RightForeArm, LeftForeArm, RightHand, LeftHand, Head.
    """
    if gesture_type == "greeting":
        # Right hand raises and waves
        return [
            {"time": 0.0, "RightArm": [0.0, 0.0, 0.3, 0.95], "RightForeArm": [-0.5, 0.0, 0.0, 0.86], "morphs": {"smile": 0.5}},
            {"time": 0.4, "RightArm": [0.2, 0.0, 0.5, 0.84], "RightForeArm": [-0.8, 0.2, 0.0, 0.55], "morphs": {"smile": 0.8}},
            {"time": 0.8, "RightArm": [0.2, 0.0, 0.3, 0.93], "RightForeArm": [-0.6, -0.2, 0.0, 0.77], "morphs": {"smile": 0.8}},
            {"time": 1.2, "RightArm": [0.0, 0.0, 0.0, 1.0], "RightForeArm": [0.0, 0.0, 0.0, 1.0], "morphs": {"smile": 0.0}}
        ]
    elif gesture_type == "eating":
        # Right hand brings food to mouth
        return [
            {"time": 0.0, "RightArm": [0.0, 0.0, 0.2, 0.97], "RightForeArm": [-0.3, 0.0, 0.0, 0.95], "morphs": {"mouthOpen": 0.0}},
            {"time": 0.5, "RightArm": [0.3, 0.0, 0.4, 0.86], "RightForeArm": [-1.1, 0.3, 0.0, 0.2], "morphs": {"mouthOpen": 0.4}},
            {"time": 1.0, "RightArm": [0.2, 0.0, 0.3, 0.92], "RightForeArm": [-0.5, 0.1, 0.0, 0.86], "morphs": {"mouthOpen": 0.1}},
            {"time": 1.4, "RightArm": [0.0, 0.0, 0.0, 1.0], "RightForeArm": [0.0, 0.0, 0.0, 1.0], "morphs": {"mouthOpen": 0.0}}
        ]
    elif gesture_type == "question":
        # Both hands open outward, eyebrows raise
        return [
            {"time": 0.0, "RightArm": [0.0, 0.0, 0.2, 0.97], "LeftArm": [0.0, 0.0, -0.2, 0.97], "morphs": {"browInnerUp": 0.2}},
            {"time": 0.6, "RightArm": [0.2, 0.2, 0.6, 0.75], "LeftArm": [0.2, -0.2, -0.6, 0.75], "morphs": {"browInnerUp": 0.9, "eyeWide": 0.5}},
            {"time": 1.2, "RightArm": [0.0, 0.0, 0.0, 1.0], "LeftArm": [0.0, 0.0, 0.0, 1.0], "morphs": {"browInnerUp": 0.0, "eyeWide": 0.0}}
        ]
    else: # Default neutral sign
        return [
            {"time": 0.0, "RightArm": [0.1, 0.0, 0.3, 0.95], "LeftArm": [0.1, 0.0, -0.3, 0.95]},
            {"time": 0.5, "RightArm": [0.3, 0.1, 0.4, 0.86], "LeftArm": [0.3, -0.1, -0.4, 0.86]},
            {"time": 1.0, "RightArm": [0.0, 0.0, 0.0, 1.0], "LeftArm": [0.0, 0.0, 0.0, 1.0]}
        ]

def seed():
    db = DatabaseManager()
    with db.get_connection() as conn:
        cursor = conn.cursor()
        
        # Core ISL Lexicon data
        signs_data = [
            # Greetings
            ("HELLO", "hello,hi,hey", "GREETING", "👋", "cards/hello.svg", json.dumps(generate_sample_keyframes("greeting")), "smile"),
            ("GOOD_MORNING", "good morning,morning", "GREETING", "🌅", "cards/good_morning.svg", json.dumps(generate_sample_keyframes("greeting")), "smile"),
            ("THANK_YOU", "thank you,thanks", "COURTESY", "🙏", "cards/thank_you.svg", json.dumps(generate_sample_keyframes("greeting")), "nod"),
            ("PLEASE", "please,kindly", "COURTESY", "🤲", "cards/please.svg", json.dumps(generate_sample_keyframes("neutral")), "neutral"),
            ("WELCOME", "welcome", "COURTESY", "🤝", "cards/welcome.svg", json.dumps(generate_sample_keyframes("greeting")), "smile"),
            ("SORRY", "sorry,apologies", "COURTESY", "🙇", "cards/sorry.svg", json.dumps(generate_sample_keyframes("neutral")), "apologetic"),

            # Nouns
            ("BOY", "boy,kid,guy", "NOUN", "👦", "cards/boy.svg", json.dumps(generate_sample_keyframes("neutral")), "neutral"),
            ("GIRL", "girl,female child", "NOUN", "👧", "cards/girl.svg", json.dumps(generate_sample_keyframes("neutral")), "neutral"),
            ("MAN", "man,male,adult", "NOUN", "👨", "cards/man.svg", json.dumps(generate_sample_keyframes("neutral")), "neutral"),
            ("WOMAN", "woman,female,lady", "NOUN", "👩", "cards/woman.svg", json.dumps(generate_sample_keyframes("neutral")), "neutral"),
            ("APPLE", "apple,fruit", "NOUN", "🍎", "cards/apple.svg", json.dumps(generate_sample_keyframes("eating")), "neutral"),
            ("BOOK", "book,textbook,reading", "NOUN", "📖", "cards/book.svg", json.dumps(generate_sample_keyframes("neutral")), "neutral"),
            ("WATER", "water,drink,aqua", "NOUN", "💧", "cards/water.svg", json.dumps(generate_sample_keyframes("eating")), "neutral"),
            ("SCHOOL", "school,college,campus", "NOUN", "🏫", "cards/school.svg", json.dumps(generate_sample_keyframes("neutral")), "neutral"),
            ("HOME", "home,house", "NOUN", "🏠", "cards/home.svg", json.dumps(generate_sample_keyframes("neutral")), "neutral"),
            ("TEACHER", "teacher,professor,instructor", "NOUN", "🧑‍🏫", "cards/teacher.svg", json.dumps(generate_sample_keyframes("neutral")), "neutral"),
            ("STUDENT", "student,pupil,learner", "NOUN", "🧑‍🎓", "cards/student.svg", json.dumps(generate_sample_keyframes("neutral")), "neutral"),
            ("INDIA", "india,bharat", "NOUN", "🇮🇳", "cards/india.svg", json.dumps(generate_sample_keyframes("greeting")), "proud"),

            # Verbs
            ("EAT", "eat,eating,ate,consumes", "VERB", "🍽️", "cards/eat.svg", json.dumps(generate_sample_keyframes("eating")), "chew"),
            ("DRINK", "drink,drinking,drank", "VERB", "🥤", "cards/drink.svg", json.dumps(generate_sample_keyframes("eating")), "neutral"),
            ("READ", "read,reading,reads", "VERB", "👓", "cards/read.svg", json.dumps(generate_sample_keyframes("neutral")), "focused"),
            ("WRITE", "write,writing,wrote", "VERB", "✍️", "cards/write.svg", json.dumps(generate_sample_keyframes("neutral")), "focused"),
            ("GO", "go,going,went", "VERB", "🚶", "cards/go.svg", json.dumps(generate_sample_keyframes("neutral")), "neutral"),
            ("COME", "come,coming,came", "VERB", "🏃", "cards/come.svg", json.dumps(generate_sample_keyframes("neutral")), "neutral"),
            ("SEE", "see,seeing,saw,look,watch", "VERB", "👀", "cards/see.svg", json.dumps(generate_sample_keyframes("neutral")), "neutral"),
            ("HELP", "help,assisting,support", "VERB", "🆘", "cards/help.svg", json.dumps(generate_sample_keyframes("greeting")), "caring"),
            ("STUDY", "study,studying,studies", "VERB", "📚", "cards/study.svg", json.dumps(generate_sample_keyframes("neutral")), "focused"),
            ("PLAY", "play,playing,played", "VERB", "⚽", "cards/play.svg", json.dumps(generate_sample_keyframes("neutral")), "happy"),

            # Pronouns & Adjectives
            ("I", "i,me,my,myself", "PRONOUN", "👤", "cards/i.svg", json.dumps(generate_sample_keyframes("neutral")), "neutral"),
            ("YOU", "you,your,yours", "PRONOUN", "👉", "cards/you.svg", json.dumps(generate_sample_keyframes("neutral")), "neutral"),
            ("HE", "he,him,his", "PRONOUN", "👨", "cards/he.svg", json.dumps(generate_sample_keyframes("neutral")), "neutral"),
            ("SHE", "she,her,hers", "PRONOUN", "👩", "cards/she.svg", json.dumps(generate_sample_keyframes("neutral")), "neutral"),
            ("GOOD", "good,nice,great,fine", "ADJECTIVE", "👍", "cards/good.svg", json.dumps(generate_sample_keyframes("greeting")), "smile"),
            ("BAD", "bad,poor,unpleasant", "ADJECTIVE", "👎", "cards/bad.svg", json.dumps(generate_sample_keyframes("neutral")), "frown"),
            ("HAPPY", "happy,cheerful,glad", "ADJECTIVE", "😊", "cards/happy.svg", json.dumps(generate_sample_keyframes("greeting")), "smile"),
            ("SAD", "sad,unhappy,depressed", "ADJECTIVE", "😢", "cards/sad.svg", json.dumps(generate_sample_keyframes("neutral")), "frown"),

            # Interrogatives (NMM Question tag)
            ("WHAT", "what", "QUESTION", "❓", "cards/what.svg", json.dumps(generate_sample_keyframes("question")), "furrow_brow"),
            ("WHERE", "where", "QUESTION", "📍", "cards/where.svg", json.dumps(generate_sample_keyframes("question")), "furrow_brow"),
            ("WHO", "who", "QUESTION", "🙋", "cards/who.svg", json.dumps(generate_sample_keyframes("question")), "furrow_brow"),
            ("WHY", "why", "QUESTION", "🤔", "cards/why.svg", json.dumps(generate_sample_keyframes("question")), "furrow_brow"),
            ("WHEN", "when", "QUESTION", "⏰", "cards/when.svg", json.dumps(generate_sample_keyframes("question")), "furrow_brow"),
            ("HOW", "how", "QUESTION", "💡", "cards/how.svg", json.dumps(generate_sample_keyframes("question")), "furrow_brow"),

            # Time markers
            ("TODAY", "today", "TIME", "📅", "cards/today.svg", json.dumps(generate_sample_keyframes("neutral")), "neutral"),
            ("TOMORROW", "tomorrow", "TIME", "🔜", "cards/tomorrow.svg", json.dumps(generate_sample_keyframes("neutral")), "neutral"),
            ("YESTERDAY", "yesterday", "TIME", "🔙", "cards/yesterday.svg", json.dumps(generate_sample_keyframes("neutral")), "neutral"),
            ("NOW", "now,currently", "TIME", "⏱️", "cards/now.svg", json.dumps(generate_sample_keyframes("neutral")), "neutral"),
        ]

        cursor.executemany("""
            INSERT OR REPLACE INTO signs (gloss, english_keywords, category, emoji, card_asset, keyframe_track, nmm_expression)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, signs_data)

        # Seed Two-Handed ISL Fingerspelling (A-Z)
        alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        fingerspelling_data = []
        for char in alphabet:
            card_path = f"cards/fingerspelling_{char.lower()}.svg"
            keyframe_data = json.dumps([
                {"time": 0.0, "RightHand": [0.1, 0.0, 0.2, 0.97], "LeftHand": [0.1, 0.0, -0.2, 0.97]},
                {"time": 0.3, "RightHand": [0.4, 0.2, 0.5, 0.72], "LeftHand": [0.4, -0.2, -0.5, 0.72]},
                {"time": 0.6, "RightHand": [0.0, 0.0, 0.0, 1.0], "LeftHand": [0.0, 0.0, 0.0, 1.0]}
            ])
            fingerspelling_data.append((char, f"FS_{char}", card_path, keyframe_data))

        cursor.executemany("""
            INSERT OR REPLACE INTO fingerspelling (character, gloss, card_asset, keyframe_track)
            VALUES (?, ?, ?, ?)
        """, fingerspelling_data)

        conn.commit()
    print(f"Database seeded successfully with {len(signs_data)} signs and {len(fingerspelling_data)} fingerspelling characters.")

if __name__ == "__main__":
    seed()
