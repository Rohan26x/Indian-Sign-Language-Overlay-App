import os

cards_dir = r"e:\Project\AUDIO-SIGN\isl-overlay-app\frontend\assets\cards"
os.makedirs(cards_dir, exist_ok=True)

signs = [
    ("hello", "👋", "HELLO", "GREETING", "#06b6d4"),
    ("good_morning", "🌅", "GOOD MORNING", "GREETING", "#38bdf8"),
    ("thank_you", "🙏", "THANK YOU", "COURTESY", "#10b981"),
    ("please", "🤲", "PLEASE", "COURTESY", "#8b5cf6"),
    ("welcome", "🤝", "WELCOME", "COURTESY", "#6366f1"),
    ("sorry", "🙇", "SORRY", "COURTESY", "#ec4899"),
    ("boy", "👦", "BOY", "NOUN", "#0284c7"),
    ("girl", "👧", "GIRL", "NOUN", "#f43f5e"),
    ("man", "👨", "MAN", "NOUN", "#2563eb"),
    ("woman", "👩", "WOMAN", "NOUN", "#db2777"),
    ("mother", "🤱", "MOTHER", "NOUN", "#ec4899"),
    ("father", "👨", "FATHER", "NOUN", "#3b82f6"),
    ("friend", "🧑‍🤝‍🧑", "FRIEND", "NOUN", "#10b981"),
    ("family", "👨‍👩‍👧‍👦", "FAMILY", "NOUN", "#8b5cf6"),
    ("baby", "👶", "BABY", "NOUN", "#f43f5e"),
    ("brother", "👦", "BROTHER", "NOUN", "#0284c7"),
    ("sister", "👧", "SISTER", "NOUN", "#db2777"),
    ("apple", "🍎", "APPLE", "NOUN", "#ef4444"),
    ("bread", "🍞", "BREAD", "NOUN", "#d97706"),
    ("milk", "🥛", "MILK", "NOUN", "#0284c7"),
    ("coffee", "☕", "COFFEE", "NOUN", "#78350f"),
    ("tea", "🍵", "TEA", "NOUN", "#15803d"),
    ("fruit", "🍇", "FRUIT", "NOUN", "#9333ea"),
    ("food", "🍲", "FOOD", "NOUN", "#d97706"),
    ("book", "📖", "BOOK", "NOUN", "#d97706"),
    ("pen", "🖊️", "PEN", "NOUN", "#475569"),
    ("water", "💧", "WATER", "NOUN", "#06b6d4"),
    ("school", "🏫", "SCHOOL", "NOUN", "#4f46e5"),
    ("work", "💼", "WORK", "NOUN", "#334155"),
    ("home", "🏠", "HOME", "NOUN", "#059669"),
    ("hospital", "🏥", "HOSPITAL", "NOUN", "#dc2626"),
    ("doctor", "🩺", "DOCTOR", "NOUN", "#0284c7"),
    ("teacher", "🧑‍🏫", "TEACHER", "NOUN", "#7c3aed"),
    ("student", "🧑‍🎓", "STUDENT", "NOUN", "#0891b2"),
    ("car", "🚗", "CAR", "NOUN", "#ef4444"),
    ("bus", "🚌", "BUS", "NOUN", "#f59e0b"),
    ("train", "🚆", "TRAIN", "NOUN", "#0ea5e9"),
    ("india", "🇮🇳", "INDIA", "NOUN", "#ea580c"),
    ("eat", "🍽️", "EAT", "VERB", "#f59e0b"),
    ("drink", "🥤", "DRINK", "VERB", "#06b6d4"),
    ("read", "👓", "READ", "VERB", "#8b5cf6"),
    ("write", "✍️", "WRITE", "VERB", "#3b82f6"),
    ("go", "🚶", "GO", "VERB", "#10b981"),
    ("come", "🏃", "COME", "VERB", "#14b8a6"),
    ("see", "👀", "SEE", "VERB", "#6366f1"),
    ("hear", "👂", "HEAR", "VERB", "#38bdf8"),
    ("speak", "🗣️", "SPEAK", "VERB", "#8b5cf6"),
    ("learn", "🧠", "LEARN", "VERB", "#6366f1"),
    ("play", "⚽", "PLAY", "VERB", "#22c55e"),
    ("sleep", "😴", "SLEEP", "VERB", "#64748b"),
    ("walk", "🚶", "WALK", "VERB", "#10b981"),
    ("run", "🏃", "RUN", "VERB", "#f97316"),
    ("sit", "🪑", "SIT", "VERB", "#0284c7"),
    ("stand", "🧍", "STAND", "VERB", "#059669"),
    ("stop", "🛑", "STOP", "VERB", "#dc2626"),
    ("help", "🆘", "HELP", "VERB", "#ef4444"),
    ("study", "📚", "STUDY", "VERB", "#8b5cf6"),
    ("open", "🔓", "OPEN", "VERB", "#10b981"),
    ("close", "🔒", "CLOSE", "VERB", "#64748b"),
    ("start", "🚀", "START", "VERB", "#0ea5e9"),
    ("finish", "🏁", "FINISH", "VERB", "#10b981"),
    ("i", "👤", "I", "PRONOUN", "#0ea5e9"),
    ("you", "👉", "YOU", "PRONOUN", "#06b6d4"),
    ("he", "👨", "HE", "PRONOUN", "#3b82f6"),
    ("she", "👩", "SHE", "PRONOUN", "#ec4899"),
    ("we", "👥", "WE", "PRONOUN", "#0284c7"),
    ("they", "👥", "THEY", "PRONOUN", "#64748b"),
    ("good", "👍", "GOOD", "ADJECTIVE", "#10b981"),
    ("bad", "👎", "BAD", "ADJECTIVE", "#ef4444"),
    ("happy", "😊", "HAPPY", "ADJECTIVE", "#f59e0b"),
    ("sad", "😢", "SAD", "ADJECTIVE", "#64748b"),
    ("love", "❤️", "LOVE", "ADJECTIVE", "#ef4444"),
    ("like", "👍", "LIKE", "ADJECTIVE", "#06b6d4"),
    ("big", "🐘", "BIG", "ADJECTIVE", "#2563eb"),
    ("small", "🐭", "SMALL", "ADJECTIVE", "#10b981"),
    ("hot", "🔥", "HOT", "ADJECTIVE", "#ea580c"),
    ("cold", "❄️", "COLD", "ADJECTIVE", "#06b6d4"),
    ("name", "🏷️", "NAME", "NOUN", "#8b5cf6"),
    ("sun", "☀️", "SUN", "NOUN", "#f59e0b"),
    ("moon", "🌙", "MOON", "NOUN", "#6366f1"),
    ("rain", "🌧️", "RAIN", "NOUN", "#0284c7"),
    ("time", "⏰", "TIME", "TIME", "#3b82f6"),
    ("day", "🌞", "DAY", "TIME", "#f59e0b"),
    ("night", "🌃", "NIGHT", "TIME", "#1e1b4b"),
    ("color", "🎨", "COLOR", "NOUN", "#ec4899"),
    ("red", "🔴", "RED", "ADJECTIVE", "#ef4444"),
    ("blue", "🔵", "BLUE", "ADJECTIVE", "#3b82f6"),
    ("green", "🟢", "GREEN", "ADJECTIVE", "#10b981"),
    ("yellow", "🟡", "YELLOW", "ADJECTIVE", "#eab308"),
    ("black", "⚫", "BLACK", "ADJECTIVE", "#18181b"),
    ("white", "⚪", "WHITE", "ADJECTIVE", "#f1f5f9"),
    ("what", "❓", "WHAT", "QUESTION", "#a855f7"),
    ("where", "📍", "WHERE", "QUESTION", "#a855f7"),
    ("who", "🙋", "WHO", "QUESTION", "#a855f7"),
    ("why", "🤔", "WHY", "QUESTION", "#a855f7"),
    ("when", "⏰", "WHEN", "QUESTION", "#a855f7"),
    ("how", "💡", "HOW", "QUESTION", "#a855f7"),
    ("today", "📅", "TODAY", "TIME", "#3b82f6"),
    ("tomorrow", "🔜", "TOMORROW", "TIME", "#2563eb"),
    ("yesterday", "🔙", "YESTERDAY", "TIME", "#1d4ed8"),
    ("now", "⏱️", "NOW", "TIME", "#0284c7"),
    ("present", "⏱️", "PRESENT", "TENSE", "#0ea5e9"),
    ("past", "🔙", "PAST", "TENSE", "#64748b"),
    ("future", "🔜", "FUTURE", "TENSE", "#3b82f6"),
    ("not", "🚫", "NOT", "NEGATION", "#ef4444"),
    ("no", "❌", "NO", "NEGATION", "#dc2626")
]

for name, emoji, gloss, category, color in signs:
    svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 280" width="100%" height="100%">
  <defs>
    <linearGradient id="grad_{name}" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="{color}" stop-opacity="0.25" />
      <stop offset="100%" stop-color="{color}" stop-opacity="0.05" />
    </linearGradient>
    <filter id="glow_{name}" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="6" result="blur" />
      <feComposite in="SourceGraphic" in2="blur" operator="over" />
    </filter>
  </defs>

  <rect width="196" height="276" x="2" y="2" rx="16" fill="#13141f" stroke="{color}" stroke-width="2" stroke-opacity="0.4"/>
  <rect width="188" height="268" x="6" y="6" rx="12" fill="url(#grad_{name})"/>

  <rect x="16" y="16" width="60" height="20" rx="6" fill="{color}" fill-opacity="0.2"/>
  <text x="46" y="30" font-family="-apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif" font-size="9" font-weight="700" fill="{color}" text-anchor="middle" letter-spacing="1">{category}</text>

  <circle cx="100" cy="115" r="46" fill="{color}" fill-opacity="0.12" filter="url(#glow_{name})"/>
  <circle cx="100" cy="115" r="42" fill="#1e2030" stroke="{color}" stroke-width="1.5" stroke-opacity="0.5"/>
  <text x="100" y="132" font-size="44" text-anchor="middle">{emoji}</text>

  <text x="100" y="200" font-family="-apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif" font-size="17" font-weight="800" fill="#ffffff" text-anchor="middle" letter-spacing="0.5">{gloss}</text>
  <text x="100" y="222" font-family="-apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif" font-size="11" font-weight="500" fill="#94a3b8" text-anchor="middle">ISL SIGN</text>

  <line x1="24" y1="244" x2="176" y2="244" stroke="{color}" stroke-width="1" stroke-opacity="0.25" stroke-dasharray="3 3"/>
  <circle cx="100" cy="256" r="3" fill="{color}" fill-opacity="0.7"/>
</svg>'''
    
    file_path = os.path.join(cards_dir, f"{name}.svg")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(svg_content)

print(f"Generated {len(signs)} sign cards in {cards_dir}")
