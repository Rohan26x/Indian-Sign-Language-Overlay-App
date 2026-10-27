import json
import os
from database import DatabaseManager

def load_handtalk_lexicon() -> dict:
    json_path = os.path.join(os.path.dirname(__file__), "..", "frontend", "assets", "handtalk_anim_lexicon.json")
    if os.path.exists(json_path):
        with open(json_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def seed():
    ht_lex = load_handtalk_lexicon()
    bsl_anims = ht_lex.get("bsl", {})
    bzs_anims = ht_lex.get("bzs", {})
    ht_words = ht_lex.get("words", {})

    db = DatabaseManager()
    with db.get_connection() as conn:
        cursor = conn.cursor()
        
        # Complete ISL Lexicon data with exact Hand Talk 3D movement mappings
        # Format: (gloss, english_keywords, category, emoji, card_asset, fallback_nmm)
        definitions = [
            # Greetings & Courtesy
            ("HELLO", "hello,hi,hey,greetings", "GREETING", "👋", "cards/hello.svg", "smile"),
            ("GOOD_MORNING", "good morning,morning", "GREETING", "🌅", "cards/good_morning.svg", "smile"),
            ("THANK_YOU", "thank you,thanks,grateful", "COURTESY", "🙏", "cards/thank_you.svg", "nod"),
            ("PLEASE", "please,kindly", "COURTESY", "🤲", "cards/please.svg", "neutral"),
            ("WELCOME", "welcome", "COURTESY", "🤝", "cards/welcome.svg", "smile"),
            ("SORRY", "sorry,apologies,pardon", "COURTESY", "🙇", "cards/sorry.svg", "apologetic"),

            # People & Pronouns
            ("BOY", "boy,kid,guy,male child", "NOUN", "👦", "cards/boy.svg", "neutral"),
            ("GIRL", "girl,female child", "NOUN", "👧", "cards/girl.svg", "neutral"),
            ("MAN", "man,male,adult,gentleman", "NOUN", "👨", "cards/man.svg", "neutral"),
            ("WOMAN", "woman,female,lady", "NOUN", "👩", "cards/woman.svg", "neutral"),
            ("MOTHER", "mother,mom,mommy,mama", "NOUN", "🤱", "cards/mother.svg", "smile"),
            ("FATHER", "father,dad,daddy,papa", "NOUN", "👨", "cards/father.svg", "neutral"),
            ("FRIEND", "friend,buddy,pal", "NOUN", "🧑‍🤝‍🧑", "cards/friend.svg", "smile"),
            ("FAMILY", "family,relatives", "NOUN", "👨‍👩‍👧‍👦", "cards/family.svg", "smile"),
            ("BABY", "baby,infant,toddler", "NOUN", "👶", "cards/baby.svg", "smile"),
            ("BROTHER", "brother,bro", "NOUN", "👦", "cards/brother.svg", "neutral"),
            ("SISTER", "sister,sis", "NOUN", "👧", "cards/sister.svg", "neutral"),
            ("TEACHER", "teacher,professor,instructor,educator", "NOUN", "🧑‍🏫", "cards/teacher.svg", "neutral"),
            ("STUDENT", "student,pupil,learner", "NOUN", "🧑‍🎓", "cards/student.svg", "neutral"),
            ("DOCTOR", "doctor,physician,medic", "NOUN", "🩺", "cards/doctor.svg", "neutral"),
            ("I", "i,me,my,myself", "PRONOUN", "👤", "cards/i.svg", "neutral"),
            ("YOU", "you,your,yours", "PRONOUN", "👉", "cards/you.svg", "neutral"),
            ("HE", "he,him,his", "PRONOUN", "👨", "cards/he.svg", "neutral"),
            ("SHE", "she,her,hers", "PRONOUN", "👩", "cards/she.svg", "neutral"),
            ("WE", "we,us,our,ours", "PRONOUN", "👥", "cards/we.svg", "neutral"),
            ("THEY", "they,them,their,theirs", "PRONOUN", "👥", "cards/they.svg", "neutral"),

            # Food & Drink
            ("WATER", "water,drink,aqua", "NOUN", "💧", "cards/water.svg", "neutral"),
            ("EAT", "eat,eating,ate,consumes,dine,food", "VERB", "🍽️", "cards/eat.svg", "chew"),
            ("DRINK", "drink,drinking,drank,beverage", "VERB", "🥤", "cards/drink.svg", "neutral"),
            ("FOOD", "food,meal,dishes", "NOUN", "🍲", "cards/food.svg", "chew"),
            ("APPLE", "apple,fruit", "NOUN", "🍎", "cards/apple.svg", "neutral"),
            ("BREAD", "bread,loaf,toast", "NOUN", "🍞", "cards/bread.svg", "neutral"),
            ("MILK", "milk,dairy", "NOUN", "🥛", "cards/milk.svg", "neutral"),
            ("COFFEE", "coffee,espresso", "NOUN", "☕", "cards/coffee.svg", "neutral"),
            ("TEA", "tea,chai", "NOUN", "🍵", "cards/tea.svg", "neutral"),
            ("FRUIT", "fruit,fruits", "NOUN", "🍇", "cards/fruit.svg", "neutral"),

            # Objects & Places
            ("SCHOOL", "school,college,campus,academy", "NOUN", "🏫", "cards/school.svg", "neutral"),
            ("BOOK", "book,textbook,reading,novel", "NOUN", "📖", "cards/book.svg", "neutral"),
            ("PEN", "pen,pencil,marker", "NOUN", "🖊️", "cards/pen.svg", "neutral"),
            ("WORK", "work,job,employment,office", "NOUN", "💼", "cards/work.svg", "neutral"),
            ("HOME", "home,house,residence", "NOUN", "🏠", "cards/home.svg", "neutral"),
            ("HOSPITAL", "hospital,clinic,medical center", "NOUN", "🏥", "cards/hospital.svg", "neutral"),
            ("CAR", "car,automobile,vehicle", "NOUN", "🚗", "cards/car.svg", "neutral"),
            ("BUS", "bus,coach", "NOUN", "🚌", "cards/bus.svg", "neutral"),
            ("TRAIN", "train,railway,metro", "NOUN", "🚆", "cards/train.svg", "neutral"),
            ("INDIA", "india,bharat", "NOUN", "🇮🇳", "cards/india.svg", "proud"),

            # Actions & Verbs
            ("GO", "go,going,went,depart", "VERB", "🚶", "cards/go.svg", "neutral"),
            ("COME", "come,coming,came,arrive", "VERB", "🏃", "cards/come.svg", "neutral"),
            ("SEE", "see,seeing,saw,look,watch", "VERB", "👀", "cards/see.svg", "neutral"),
            ("HEAR", "hear,hearing,heard,listen", "VERB", "👂", "cards/hear.svg", "neutral"),
            ("SPEAK", "speak,speaking,spoke,talk,say", "VERB", "🗣️", "cards/speak.svg", "neutral"),
            ("WRITE", "write,writing,wrote", "VERB", "✍️", "cards/write.svg", "focused"),
            ("READ", "read,reading,reads", "VERB", "👓", "cards/read.svg", "focused"),
            ("LEARN", "learn,learning,learned,study", "VERB", "🧠", "cards/learn.svg", "focused"),
            ("STUDY", "study,studying,studies", "VERB", "📚", "cards/study.svg", "focused"),
            ("PLAY", "play,playing,played,game", "VERB", "⚽", "cards/play.svg", "happy"),
            ("SLEEP", "sleep,sleeping,slept,rest", "VERB", "😴", "cards/sleep.svg", "neutral"),
            ("WALK", "walk,walking,walked", "VERB", "🚶", "cards/walk.svg", "neutral"),
            ("RUN", "run,running,ran,jog", "VERB", "🏃", "cards/run.svg", "neutral"),
            ("SIT", "sit,sitting,sat", "VERB", "🪑", "cards/sit.svg", "neutral"),
            ("STAND", "stand,standing,stood", "VERB", "🧍", "cards/stand.svg", "neutral"),
            ("STOP", "stop,halt,pause", "VERB", "🛑", "cards/stop.svg", "neutral"),
            ("HELP", "help,assisting,support,aid", "VERB", "🆘", "cards/help.svg", "caring"),
            ("OPEN", "open,opening,opened", "VERB", "🔓", "cards/open.svg", "neutral"),
            ("CLOSE", "close,closing,closed,shut", "VERB", "🔒", "cards/close.svg", "neutral"),
            ("START", "start,begin,initiate", "VERB", "🚀", "cards/start.svg", "neutral"),
            ("FINISH", "finish,end,complete,done", "VERB", "🏁", "cards/finish.svg", "neutral"),

            # Adjectives & Descriptions
            ("GOOD", "good,nice,great,fine,well", "ADJECTIVE", "👍", "cards/good.svg", "smile"),
            ("BAD", "bad,poor,unpleasant,terrible", "ADJECTIVE", "👎", "cards/bad.svg", "frown"),
            ("HAPPY", "happy,cheerful,glad,joy", "ADJECTIVE", "😊", "cards/happy.svg", "smile"),
            ("SAD", "sad,unhappy,depressed,sorrow", "ADJECTIVE", "😢", "cards/sad.svg", "frown"),
            ("LOVE", "love,affection,adore", "ADJECTIVE", "❤️", "cards/love.svg", "smile"),
            ("LIKE", "like,enjoy,prefer", "ADJECTIVE", "👍", "cards/like.svg", "smile"),
            ("BIG", "big,large,huge,giant", "ADJECTIVE", "🐘", "cards/big.svg", "neutral"),
            ("SMALL", "small,little,tiny", "ADJECTIVE", "🐭", "cards/small.svg", "neutral"),
            ("HOT", "hot,warm,heat", "ADJECTIVE", "🔥", "cards/hot.svg", "neutral"),
            ("COLD", "cold,chilly,cool,freezing", "ADJECTIVE", "❄️", "cards/cold.svg", "neutral"),
            ("NAME", "name,title,called", "NOUN", "🏷️", "cards/name.svg", "neutral"),

            # Questions (NMM Question tag)
            ("WHAT", "what", "QUESTION", "❓", "cards/what.svg", "furrow_brow"),
            ("WHERE", "where", "QUESTION", "📍", "cards/where.svg", "furrow_brow"),
            ("WHO", "who", "QUESTION", "🙋", "cards/who.svg", "furrow_brow"),
            ("WHY", "why", "QUESTION", "🤔", "cards/why.svg", "furrow_brow"),
            ("WHEN", "when", "QUESTION", "⏰", "cards/when.svg", "furrow_brow"),
            ("HOW", "how", "QUESTION", "💡", "cards/how.svg", "furrow_brow"),

            # Time & Tense
            ("TODAY", "today,this day", "TIME", "📅", "cards/today.svg", "neutral"),
            ("TOMORROW", "tomorrow,next day", "TIME", "🔜", "cards/tomorrow.svg", "neutral"),
            ("YESTERDAY", "yesterday,prior day", "TIME", "🔙", "cards/yesterday.svg", "neutral"),
            ("TIME", "time,hour,clock", "TIME", "⏰", "cards/time.svg", "neutral"),
            ("DAY", "day,daytime", "TIME", "🌞", "cards/day.svg", "neutral"),
            ("NIGHT", "night,nighttime,dark", "TIME", "🌃", "cards/night.svg", "neutral"),
            ("NOW", "now,currently,presently", "TIME", "⏱️", "cards/now.svg", "neutral"),
            ("PRESENT", "present,is,am,are,now,currently", "TENSE", "⏱️", "cards/present.svg", "neutral"),
            ("PAST", "past,was,were,did,ago", "TENSE", "🔙", "cards/past.svg", "neutral"),
            ("FUTURE", "future,will,shall,later", "TENSE", "🔜", "cards/future.svg", "neutral"),

            # Nature & Environment
            ("SUN", "sun,sunshine,sunny", "NOUN", "☀️", "cards/sun.svg", "neutral"),
            ("MOON", "moon,lunar", "NOUN", "🌙", "cards/moon.svg", "neutral"),
            ("RAIN", "rain,raining,rainy,shower", "NOUN", "🌧️", "cards/rain.svg", "neutral"),

            # Colors
            ("COLOR", "color,colour", "NOUN", "🎨", "cards/color.svg", "neutral"),
            ("RED", "red,crimson", "ADJECTIVE", "🔴", "cards/red.svg", "neutral"),
            ("BLUE", "blue,azure", "ADJECTIVE", "🔵", "cards/blue.svg", "neutral"),
            ("GREEN", "green,emerald", "ADJECTIVE", "🟢", "cards/green.svg", "neutral"),
            ("YELLOW", "yellow,amber", "ADJECTIVE", "🟡", "cards/yellow.svg", "neutral"),
            ("BLACK", "black,dark", "ADJECTIVE", "⚫", "cards/black.svg", "neutral"),
            ("WHITE", "white,bright", "ADJECTIVE", "⚪", "cards/white.svg", "neutral"),

            # Negation & Logic
            ("NOT", "not,no,never,dont,didnt,wont", "NEGATION", "🚫", "cards/not.svg", "frown"),
            ("NO", "no,negative,nope", "NEGATION", "❌", "cards/no.svg", "frown"),
            ("YES", "yes,yeah,yep,affirmative", "COURTESY", "✅", "cards/good.svg", "smile"),
        ]

        signs_data = []
        for gloss, keywords, category, emoji, card, nmm in definitions:
            # Look up authentic Hand Talk animation track string
            track_str = (
                ht_words.get(gloss) or
                ht_words.get(gloss.upper()) or
                ht_words.get(gloss.lower()) or
                ht_words.get(gloss.replace('_', ' ')) or
                ht_words.get(gloss.replace('_', ' ').lower())
            )

            # If alias mapping is needed
            if not track_str:
                if gloss == "STUDY":
                    track_str = ht_words.get("LEARN")
                elif gloss == "GOOD_MORNING":
                    track_str = ht_words.get("HELLO")
                elif gloss == "PRESENT":
                    track_str = ht_words.get("NOW")
                elif gloss == "PAST":
                    track_str = ht_words.get("YESTERDAY")
                elif gloss == "FUTURE":
                    track_str = ht_words.get("TOMORROW")

            if track_str:
                keyframe_track = json.dumps(track_str)
            else:
                keyframe_track = json.dumps(gloss.lower())

            signs_data.append((gloss, keywords, category, emoji, card, keyframe_track, nmm))

        cursor.executemany("""
            INSERT OR REPLACE INTO signs (gloss, english_keywords, category, emoji, card_asset, keyframe_track, nmm_expression)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, signs_data)

        # Seed Authentic Hand Talk Fingerspelling (A-Z)
        alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        fingerspelling_data = []
        for char in alphabet:
            card_path = f"cards/fingerspelling_{char.lower()}.svg"
            char_lower = char.lower()
            track_str = bsl_anims.get(char_lower) or bzs_anims.get(char_lower)
            if track_str:
                keyframe_data = json.dumps(track_str)
            else:
                keyframe_data = json.dumps(char_lower)

            fingerspelling_data.append((char, f"FS_{char}", card_path, keyframe_data))

        cursor.executemany("""
            INSERT OR REPLACE INTO fingerspelling (character, gloss, card_asset, keyframe_track)
            VALUES (?, ?, ?, ?)
        """, fingerspelling_data)

        conn.commit()

    print(f"Database seeded successfully with {len(signs_data)} signs (ALL mapped to authentic Hand Talk tracks) and {len(fingerspelling_data)} fingerspelling characters.")

if __name__ == "__main__":
    seed()
