import streamlit as st
import os
import random
import requests
import pandas as pd
import streamlit.components.v1 as components
from datetime import date, datetime, timedelta
from supabase import create_client, Client

# ---------- CONFIG ----------
DAILY_TARGET = 40
PENDING_LIMIT = 35  # if backlog exceeds this, streak resets
STORAGE_BUCKET = "checkin-photos"  # Supabase Storage bucket for uploaded photos


# ---------- SUPABASE CLIENT ----------
@st.cache_resource
def get_supabase_client() -> Client:
    url = st.secrets["supabase"]["url"]
    key = st.secrets["supabase"]["key"]
    return create_client(url, key)


supabase = get_supabase_client()

st.set_page_config(
    page_title="Aditi's IIT JAM Mission",
    page_icon="🪄",
    layout="centered",
)

# ---------- ONLINE DATE/TIME SYNC ----------
@st.cache_data(ttl=1800)
def fetch_online_datetime():
    try:
        resp = requests.get(
            "https://worldtimeapi.org/api/timezone/Asia/Kolkata", timeout=5
        )
        resp.raise_for_status()
        data = resp.json()
        dt = datetime.fromisoformat(data["datetime"])
        return dt.replace(tzinfo=None), True
    except Exception:
        return datetime.now(), False


# ---------- ROTATING HEADINGS ----------
HEADINGS = [
    "🎯 Aditi's IIT JAM Mission",
    "🚀 Operation JAM 2027: Daily Tracker",
    "⚡ Aditi vs. The Syllabus",
    "🪄 The 40-Question Daily Spell",
    "🧠 Aditi's Math Mastery Streak",
]


def get_daily_heading(today):
    return HEADINGS[today.toordinal() % len(HEADINGS)]


# ---------- DAILY MOTIVATIONAL QUOTES ----------
QUOTES = [
    "Small steps every day add up to something huge.",
    "Discipline is choosing what you want most over what you want now.",
    "You don't have to be perfect, you just have to show up.",
    "Every question you solve today is a rep for your brain.",
    "Consistency beats intensity. Keep stacking days.",
    "Future you is already proud of today's effort.",
    "One more day. That's all you need to focus on.",
    "Progress hides inside boring, repeated effort.",
    "The streak isn't the goal. The habit is.",
    "You're not behind. You're building.",
    "Hard days make the streak mean something.",
    "Nobody sees the 40 questions. Everybody sees the result.",
    "Momentum is built one upload at a time.",
    "Study now, thank yourself later.",
    "Slow progress is still progress.",
    "Your only competition is yesterday's version of you.",
    "Great things are built quietly, day after day.",
    "The streak is proof you kept a promise to yourself.",
    "Don't break the chain.",
    "A little bit today keeps the panic away tomorrow.",
    "Focus on the next question, not the whole mountain.",
    "You show up even when it's boring. That's the whole game.",
    "Confidence is built in the reps nobody applauds.",
    "Today's 40 questions are tomorrow's easy answers.",
    "Keep going. It compounds.",
    "You are one upload away from a new personal best.",
    "Effort compounds quietly until it doesn't.",
    "Every streak starts with a single day one.",
    "Show up for yourself today, like you did yesterday.",
    "The work you do today is a gift to future you.",
]


def get_daily_quote(today):
    return QUOTES[today.toordinal() % len(QUOTES)]


# ---------- SHIVAM'S NOTE ----------
SHIVAMS_NOTE = (
    "Hey Aditi, I built this app specifically for you. I know how much you value your "
    "snap streaks, so I wanted to channel that exact same energy into your JAM maths prep. "
    "I\u2019ve put a lot of hope into this project because I know how hard you're working. "
    "Keep the streak active, don't break the chain, and crack this exam. Make me proud! "
    "Let's get that streak to 100.\n\n\u2014 Shivam"
)

# ---------- STREAK TITLES (day, title-with-emoji) ----------
TITLE_MILESTONES = [
    (1, "🌱 The First Step"),
    (2, "🔥 Spark Ignited"),
    (3, "⚙️ Building Momentum"),
    (5, "🏃‍♀️ Pace Setter"),
    (8, "🧠 Focus Trainee"),
    (10, "🛡️ Double Digits Defender"),
    (12, "📐 Matrix Master in Training"),
    (15, "⚔️ Half-Month Hero"),
    (18, "🧩 Problem-Solving Prodigy"),
    (20, "💎 Consistency Champion"),
    (25, "🚀 Quarter-Century Crusher"),
    (27, "📈 The Unstoppable Curve"),
    (30, "🌙 Full Month Legend"),
    (40, "🌌 Calculus Conqueror"),
    (50, "🔱 Half-Century Scholar"),
    (60, "🪐 Real Analysis Titan"),
    (70, "🛡️ Vector Virtuoso"),
    (80, "⚔️ Abstract Algebra Ace"),
    (90, "👑 Three-Month Monarch"),
    (105, "🌠 The 100+ Phenomenon"),
    (120, "🧠 Four-Month Mastermind"),
    (135, "📐 Geometry General"),
    (150, "☄️ Unbreakable Will"),
    (165, "🦅 High-Flying Focus"),
    (180, "🌍 Half-Year Hero (180 Days)"),
    (195, "🧩 Topology Tactician"),
    (210, "🚀 Seven-Month Sprinter"),
    (225, "💎 Diamond Discipline"),
    (240, "🌌 Eight-Month Elite"),
    (255, "🧬 Group Theory Guru"),
    (270, "🏆 Nine-Month Ninja"),
    (285, "🔱 Equation Emperor"),
    (300, "⚔️ Spartan Scholar (300 Days!)"),
    (315, "🛡️ Differential Duke"),
    (330, "🪐 Sequence & Series Sovereign"),
    (345, "📈 Unstoppable Momentum"),
    (360, "👑 The Final Countdown"),
    (365, "🎇 One Year Legend (JAM Ready)"),
    (380, "🚀 Boundless Scholar"),
    (395, "🧠 Iron Mindset"),
    (410, "📐 Limitless Logic"),
    (425, "☄️ Meteoric Rise"),
    (440, "🦅 Soaring Intellect"),
    (455, "🌍 Gravity Defier"),
    (470, "🧩 The Integration Illusionist"),
    (485, "💎 Flawless Execution"),
    (500, "🌌 Half-Thousand Hero (500 Days!)"),
    (515, "🧬 Unrivaled Genius"),
    (530, "🏆 Elite Equationist"),
    (545, "🔱 Theorem Tamer"),
    (560, "⚔️ Math Warrior"),
    (575, "🛡️ Fortified Focus"),
    (590, "🪐 Conceptual Conqueror"),
    (605, "📈 Infinite Upward Trend"),
    (620, "👑 Syllabus Sovereign"),
    (635, "🎇 Relentless Force"),
    (650, "🚀 The Mathematical Myth"),
    (665, "🧠 Supreme Strategist"),
    (680, "📐 Geometric God/Goddess"),
    (695, "☄️ The Cosmic Calculator"),
    (710, "🦅 Zenith Achiever"),
    (725, "🌍 Universal Understanding"),
    (740, "🧩 Master of Matrices"),
    (755, "💎 Crystal Clear Concepts"),
    (770, "🌌 The 770 Singularity"),
    (785, "🧬 Brilliant Brainwave"),
    (800, "🏆 The 800-Day Dynasty"),
    (815, "🔱 Number Ninja Elite"),
    (830, "⚔️ Unbeatable Intellect"),
    (845, "🛡️ Master of Proofs"),
    (860, "🪐 Orbiting Greatness"),
    (875, "📈 Exponential Excellence"),
    (890, "👑 Crowned Mathematician"),
    (905, "🎇 The 900+ Juggernaut"),
    (920, "🚀 Mind over Matter"),
    (935, "🧠 Ultimate Scholar"),
    (950, "📐 The Penultimate Peak"),
    (965, "☄️ Force of Nature"),
    (980, "🦅 Legacy Builder"),
    (995, "🌍 The Edge of Infinity"),
    (1000, "♾️ The Infinity Streak (1000 Days)"),
]


def current_title(streak):
    achieved = [t for t in TITLE_MILESTONES if t[0] <= streak]
    return achieved[-1] if achieved else None


def next_title(streak):
    upcoming = [t for t in TITLE_MILESTONES if t[0] > streak]
    return upcoming[0] if upcoming else None


def milestone_message(streak):
    title = current_title(streak)
    if title and title[0] == streak:
        day, name = title
        return f"🏆 Day {day} unlocked: {name}!"
    return None


# ---------- HARRY POTTER CHARACTER DECK ----------
# NOTE ON IMAGES: I can't source or embed actual Harry Potter film stills or
# official artwork here since that's Warner Bros. / J.K. Rowling copyrighted
# material. Every "waiting_image" / "completed_image" below is a clearly
# labeled placeholder URL — replace each with an image you have the rights
# to use before sharing this app publicly. The dialogue lines are original
# text you provided, not quotes from the books or films.
IMG_BASE = "PASTE_YOUR_IMAGE_HOST_URL_HERE"  # e.g. "https://your-cdn.com/hp"

PLACEHOLDER_MARKER_TO_DELETE_wizard_svg_START = True
def wizard_svg(mood="sad"):
    if mood == "happy":
        eyebrow_l = "M45,66 Q60,56 75,66"
        eyebrow_r = "M85,66 Q100,56 115,66"
        mouth = "M58,104 Q80,124 102,104"
        wand_glow = '<circle cx="132" cy="60" r="7" fill="#ffe066" opacity="0.9"/><circle cx="132" cy="60" r="13" fill="#ffe066" opacity="0.35"/>'
        sparkles = (
            '<circle cx="30" cy="40" r="2.5" fill="#ffe066"/>'
            '<circle cx="20" cy="70" r="2" fill="#ffe066"/>'
            '<circle cx="140" cy="100" r="2" fill="#ffe066"/>'
        )
        owl_eye = '<circle cx="24" cy="128" r="4" fill="#2b1a12"/><circle cx="36" cy="128" r="4" fill="#2b1a12"/>'
    else:
        eyebrow_l = "M45,70 Q60,62 75,70"
        eyebrow_r = "M85,70 Q100,62 115,70"
        mouth = "M58,118 Q80,104 102,118"
        wand_glow = ""
        sparkles = ""
        owl_eye = '<path d="M20,128 q4,4 8,0" stroke="#2b1a12" stroke-width="2" fill="none"/><path d="M32,128 q4,4 8,0" stroke="#2b1a12" stroke-width="2" fill="none"/>'

    return f'''
    <svg width="160" height="150" viewBox="0 0 160 150" xmlns="http://www.w3.org/2000/svg">
      <!-- little owl companion -->
      <ellipse cx="28" cy="120" rx="18" ry="16" fill="#8a7460"/>
      <path d="M14,110 L22,98 L26,112 Z" fill="#8a7460"/>
      <path d="M42,110 L34,98 L30,112 Z" fill="#8a7460"/>
      {owl_eye}
      <path d="M28,132 L24,138 L32,138 Z" fill="#e0a030"/>

      <!-- wizard hat -->
      <path d="M80,6 L108,64 L52,64 Z" fill="#3a1c71"/>
      <ellipse cx="80" cy="64" rx="30" ry="7" fill="#2a1050"/>
      <rect x="60" y="52" width="40" height="7" fill="#d4af37"/>
      <circle cx="80" cy="20" r="4" fill="#d4af37"/>

      <!-- face -->
      <circle cx="80" cy="86" r="30" fill="#f2c9a0" stroke="#caa06a" stroke-width="2"/>
      <circle cx="70" cy="86" r="3.5" fill="#2b1a12"/>
      <circle cx="90" cy="86" r="3.5" fill="#2b1a12"/>
      <path d="{eyebrow_l}" stroke="#2b1a12" stroke-width="3" fill="none" stroke-linecap="round"/>
      <path d="{eyebrow_r}" stroke="#2b1a12" stroke-width="3" fill="none" stroke-linecap="round"/>
      <path d="{mouth}" stroke="#7a3e2e" stroke-width="3" fill="none" stroke-linecap="round"/>

      <!-- robe -->
      <path d="M50,112 L110,112 L124,148 L36,148 Z" fill="#5c1e8a"/>
      <path d="M50,112 L110,112 L118,128 L42,128 Z" fill="#7a2eb0"/>
      <circle cx="80" cy="122" r="3" fill="#d4af37"/>

      <!-- wand -->
      <line x1="108" y1="96" x2="132" y2="60" stroke="#4a2e1a" stroke-width="4" stroke-linecap="round"/>
      {wand_glow}
      {sparkles}
    </svg>
    '''


def mood_card(uploaded_today):
    if uploaded_today:
        svg = wizard_svg("happy")
        text = "Brilliant spellwork today! Your magical streak grows stronger! 🪄✨"
    else:
        svg = wizard_svg("sad")
        text = "My wand's gone dim... please cast today's questions to light it back up! 📖✨"
    return f"""
    <div style="display:flex;align-items:center;gap:1rem;background:rgba(20,10,45,0.45);
                border:1px solid rgba(212,175,55,0.4);
                border-radius:18px;padding:0.9rem 1.1rem;margin-bottom:0.6rem;
                box-shadow:0 4px 14px rgba(0,0,0,0.35);">
        <div>{svg}</div>
        <div style="font-weight:700;color:#f5e6c8;font-size:1.02rem;">{text}</div>
    </div>
    """


def flame_display(streak):
    if streak == 0:
        return "🌑"
    return "✨" * min(streak, 10)


# ---------- STYLING: ORIGINAL MAGIC / WIZARD-SCHOOL THEME ----------
st.markdown(
    """
    <style>
    .stApp {
        background:
            radial-gradient(circle at 15% 15%, rgba(255,255,255,0.10) 1.5px, transparent 1.5px),
            radial-gradient(circle at 70% 30%, rgba(255,255,255,0.08) 1.5px, transparent 1.5px),
            radial-gradient(circle at 40% 80%, rgba(255,255,255,0.08) 1.5px, transparent 1.5px),
            radial-gradient(circle at 85% 75%, rgba(255,255,255,0.07) 1.5px, transparent 1.5px),
            radial-gradient(ellipse at top, #3a1c71 0%, #241049 45%, #120a26 100%);
        background-size: 180px 180px, 220px 220px, 200px 200px, 240px 240px, cover;
        background-attachment: fixed;
    }
    .main .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
        max-width: 540px;
    }
    .stApp, .stApp p, .stApp span, .stApp li,
    .stMarkdown, .stMarkdown p, .stCaption, [data-testid="stCaptionContainer"],
    label, .stTextInput label p, .stNumberInput label p, .stRadio label p,
    h1, h2, h3, h4, h5, h6, .stSubheader {
        color: #f5e6c8 !important;
    }
    input[type="text"], input[type="password"], input[type="number"], textarea {
        background-color: #ffffff !important;
        color: #000000 !important;
        caret-color: #000000 !important;
        border: 1px solid #d4af37 !important;
    }
    .stButton > button, .stDownloadButton > button {
        background: linear-gradient(135deg, #3a1c71, #6a3de8) !important;
        color: #f5e6c8 !important;
        border: 1.5px solid #d4af37 !important;
        font-weight: 700 !important;
        box-shadow: 0 3px 10px rgba(0,0,0,0.35);
    }
    .stButton > button:hover, .stDownloadButton > button:hover {
        background: linear-gradient(135deg, #4c2a8e, #8353ff) !important;
        color: #fff3d0 !important;
        border: 1.5px solid #ffe066 !important;
    }
    .stButton > button p, .stButton > button span, .stButton > button div {
        color: #f5e6c8 !important;
    }
    [data-testid="stExpander"] summary {
        background: linear-gradient(135deg, #3a1c71, #6a3de8) !important;
        border-radius: 10px !important;
        border: 1.5px solid #d4af37 !important;
    }
    [data-testid="stExpander"] summary span,
    [data-testid="stExpander"] summary p {
        color: #f5e6c8 !important;
        font-weight: 700 !important;
    }
    .big-title {
        font-size: 2.0rem;
        font-weight: 900;
        text-align: center;
        margin-bottom: 0.1rem;
        background: linear-gradient(90deg, #d4af37, #fff3d0, #d4af37);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .subtitle { text-align: center; color: #d8c9a3 !important; margin-bottom: 0.3rem; font-size: 0.95rem; }
    .synced-date { text-align: center; color: #b8a888 !important; font-size: 0.85rem; margin-bottom: 1rem; }
    .quote-card {
        background: rgba(255,255,255,0.06);
        border-left: 5px solid #d4af37;
        border-radius: 12px;
        padding: 0.9rem 1.1rem;
        font-style: italic;
        color: #f5e6c8 !important;
        margin-bottom: 1.2rem;
        box-shadow: 0 4px 14px rgba(0,0,0,0.3);
    }
    .streak-box, .progress-box { display: flex; justify-content: space-between; gap: 1rem; margin-bottom: 1rem; }
    .streak-card {
        flex: 1;
        background: linear-gradient(160deg, rgba(255,255,255,0.10), rgba(90,30,140,0.25));
        border-radius: 18px;
        padding: 1.3rem 0.5rem;
        text-align: center;
        box-shadow: 0 6px 16px rgba(0,0,0,0.35);
        border: 1px solid rgba(212,175,55,0.4);
    }
    .streak-card.high { background: linear-gradient(160deg, rgba(255,255,255,0.10), rgba(30,110,70,0.3)); box-shadow: 0 6px 16px rgba(30,150,80,0.2); }
    .streak-card.pending { background: linear-gradient(160deg, rgba(255,255,255,0.10), rgba(140,30,30,0.3)); box-shadow: 0 6px 16px rgba(200,40,40,0.2); }
    .streak-number { font-size: 2.4rem; font-weight: 900; color: #f5e6c8 !important; }
    .streak-card.high .streak-number { color: #8fe3b0 !important; }
    .streak-card.pending .streak-number { color: #ff9a9a !important; }
    .streak-label { font-size: 0.78rem; color: #cbb98f !important; text-transform: uppercase; letter-spacing: 0.07em; margin-top: 0.2rem; }
    .login-card { background: rgba(20,10,45,0.55); border-radius: 20px; padding: 1.6rem 1.4rem; box-shadow: 0 8px 24px rgba(0,0,0,0.4); margin-top: 0.6rem; border: 1px solid rgba(212,175,55,0.35); }
    .flame-row { text-align: center; font-size: 1.5rem; letter-spacing: 0.15em; margin-bottom: 0.4rem; }
    .stApp .milestone-banner { text-align: center; background: linear-gradient(90deg, #d4af37, #f09819); color:#2b1a12 !important; border-radius: 12px; padding: 0.6rem; font-weight: 700; margin-bottom: 1rem; }
    .stApp .milestone-banner * { color: #2b1a12 !important; }
    .stApp .title-unlocked { text-align: center; background: linear-gradient(90deg, #6a3de8, #a06bff); color:#fff !important; border-radius: 14px; padding: 0.9rem; font-weight: 700; font-size: 1.1rem; margin-bottom: 0.4rem; border: 1px solid rgba(212,175,55,0.5); }
    .stApp .title-unlocked * { color: #fff !important; }
    .stApp .title-locked { text-align: center; background: rgba(255,255,255,0.06); color:#cbb98f !important; border-radius: 14px; padding: 0.9rem; font-weight: 600; margin-bottom: 0.4rem; border: 1px dashed rgba(212,175,55,0.3); }
    .note-card { background: linear-gradient(135deg, #3a1030, #5c1e3a); border: 1px solid #d4af37; border-radius: 16px; padding: 1.1rem 1.3rem; margin-bottom: 1rem; box-shadow: 0 6px 16px rgba(0,0,0,0.35); font-size: 0.98rem; line-height: 1.5; color:#f5e6c8 !important; white-space: pre-line; }
    .tutorial-glow { border-radius: 18px; box-shadow: 0 0 0 4px #ffe066, 0 0 24px 8px rgba(255,224,102,0.6); padding: 0.5rem; margin-bottom: 0.4rem; transition: box-shadow 0.3s; }
    .tutorial-callout { background: rgba(10,5,20,0.85); color: #ffe066 !important; border: 1px solid #ffe066; border-radius: 10px; padding: 0.7rem 1rem; margin-bottom: 0.6rem; font-weight: 600; }
    .tutorial-callout * { color: #ffe066 !important; }
    .pending-warning { background: rgba(224,123,0,0.18); border-left: 5px solid #e07b00; border-radius: 10px; padding: 0.7rem 1rem; margin: 0.6rem 0; color:#ffcf94 !important; font-weight:600; }
    .pending-ok { background: rgba(46,158,80,0.18); border-left: 5px solid #2e9e50; border-radius: 10px; padding: 0.7rem 1rem; margin: 0.6rem 0; color:#8fe3b0 !important; font-weight:600; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------- DATA PERSISTENCE (multi-user, Supabase-backed) ----------
def load_users():
    response = supabase.table("users").select("*").execute()
    users = {}
    for row in response.data:
        users[row["username"]] = {
            "password": row["password"],
            "current_streak": row["current_streak"],
            "highest_streak": row["highest_streak"],
            "last_upload_date": row["last_upload_date"],
            "created_date": row["created_date"],
            "history": row["history"] or {},
            "pending_reset_date": row.get("pending_reset_date"),
        }
    return users


def save_user(username, record):
    """Upsert a single user's record into the Supabase 'users' table."""
    supabase.table("users").upsert({
        "username": username,
        "password": record["password"],
        "current_streak": record["current_streak"],
        "highest_streak": record["highest_streak"],
        "last_upload_date": record["last_upload_date"],
        "created_date": record["created_date"],
        "history": record["history"],
        "pending_reset_date": record.get("pending_reset_date"),
    }).execute()


def save_users(users):
    for username, record in users.items():
        save_user(username, record)


def new_user_record(password, today_str):
    return {
        "password": password,
        "current_streak": 0,
        "highest_streak": 0,
        "last_upload_date": None,
        "created_date": today_str,
        "history": {},
        "pending_reset_date": None,
    }


def backfill_missing_days(record, today):
    if record["last_upload_date"] is None:
        return
    last_date = datetime.strptime(record["last_upload_date"], "%Y-%m-%d").date()
    d = last_date + timedelta(days=1)
    while d < today:
        ds = d.isoformat()
        record.setdefault("history", {})
        if ds not in record["history"]:
            record["history"][ds] = {"uploaded": False, "questions": 0}
        d += timedelta(days=1)


def check_for_broken_streak(users, username, today):
    record = users[username]
    if record["last_upload_date"] is None:
        return users
    last_date = datetime.strptime(record["last_upload_date"], "%Y-%m-%d").date()
    gap_days = (today - last_date).days
    changed = False
    if gap_days > 1:
        backfill_missing_days(record, today)
        if record["current_streak"] != 0:
            record["current_streak"] = 0
        # Streak broke -> pending backlog also resets to zero going forward
        record["pending_reset_date"] = (today - timedelta(days=1)).isoformat()
        changed = True
    if changed:
        save_user(username, record)
    return users


def compute_progress(history, reset_date=None):
    """Replays history to get lifetime total questions solved (never reset)
    and the current pending backlog. If reset_date is set, only days AFTER
    that date count toward backlog (used to zero out backlog when a streak
    breaks, without touching the historical log)."""
    total_solved = 0
    pending = 0
    for d in sorted(history.keys()):
        entry = history[d]
        q = entry.get("questions", 0) if entry.get("uploaded") else 0
        total_solved += q
        if reset_date is None or d > reset_date:
            shortfall = max(0, DAILY_TARGET - q)
            surplus = max(0, q - DAILY_TARGET)
            pending = max(0, pending + shortfall - surplus)
    return total_solved, pending


def register_upload(users, username, questions_completed, file_bytes, file_ext, today):
    record = users[username]
    today_str = today.isoformat()

    if record["last_upload_date"] is None:
        record["current_streak"] = 1
    else:
        last_date = datetime.strptime(record["last_upload_date"], "%Y-%m-%d").date()
        gap_days = (today - last_date).days
        if gap_days == 0:
            pass
        elif gap_days == 1:
            record["current_streak"] += 1
        else:
            record["current_streak"] = 1

    record["last_upload_date"] = today_str
    record.setdefault("history", {})[today_str] = {
        "uploaded": True,
        "questions": questions_completed,
    }

    # Recompute backlog since the last reset point
    _, pending = compute_progress(record["history"], record.get("pending_reset_date"))
    if pending > PENDING_LIMIT:
        record["current_streak"] = 0
        # Backlog also resets to zero the moment the streak breaks
        record["pending_reset_date"] = today_str

    record["highest_streak"] = max(record["highest_streak"], record["current_streak"])
    save_user(username, record)

    ext_clean = file_ext.lstrip(".").lower()
    content_type = "image/jpeg" if ext_clean in ("jpg", "jpeg") else f"image/{ext_clean}"
    storage_path = f"{username}/{today_str}{file_ext}"
    supabase.storage.from_(STORAGE_BUCKET).upload(
        storage_path,
        file_bytes,
        {"content-type": content_type, "upsert": "true"},
    )

    return users


def find_saved_image(username, date_str):
    try:
        files = supabase.storage.from_(STORAGE_BUCKET).list(username)
    except Exception:
        return None
    for f in files:
        if f["name"].startswith(date_str):
            storage_path = f"{username}/{f['name']}"
            return supabase.storage.from_(STORAGE_BUCKET).get_public_url(storage_path)
    return None


# ---------- TUTORIAL / GUIDED TOUR ----------
TUTORIAL_STEPS = [
    {"target": "title", "text": "👉 Tap this box to reveal your current title! Titles stay locked until your streak reaches that many days."},
    {"target": "mood", "text": "👉 This little wizard shows how today is going — dim and sad if you haven't checked in yet, glowing and happy once you have!"},
    {"target": "streak", "text": "👉 These are your Current Streak and your all-time Highest Streak. Don't let the first one hit zero!"},
    {"target": "progress", "text": f"👉 Here's your total questions solved and any pending backlog. Keep backlog under {PENDING_LIMIT} or the streak resets!"},
    {"target": "checkin", "text": "👉 Upload today's photo here, tell the app how many questions you solved, then hit Submit."},
    {"target": "history", "text": "👉 Every single day gets logged here so you can look back on your whole journey."},
]


def section(name, render_fn):
    active = (
        st.session_state.get("tutorial_active", False)
        and TUTORIAL_STEPS[st.session_state.get("tutorial_step", 0)]["target"] == name
    )
    if active:
        st.markdown('<div class="tutorial-glow">', unsafe_allow_html=True)
    render_fn()
    if active:
        st.markdown("</div>", unsafe_allow_html=True)
        step = TUTORIAL_STEPS[st.session_state.tutorial_step]
        st.markdown(f'<div class="tutorial-callout">{step["text"]}</div>', unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        with c1:
            if st.session_state.tutorial_step > 0:
                if st.button("⬅ Back", key=f"tut_back_{name}", use_container_width=True):
                    st.session_state.tutorial_step -= 1
                    st.rerun()
        with c2:
            if st.button("Skip Tour", key=f"tut_skip_{name}", use_container_width=True):
                st.session_state.tutorial_active = False
                st.rerun()
        with c3:
            is_last = st.session_state.tutorial_step == len(TUTORIAL_STEPS) - 1
            if st.button("Finish ✅" if is_last else "Next ➡", key=f"tut_next_{name}", use_container_width=True):
                if is_last:
                    st.session_state.tutorial_active = False
                else:
                    st.session_state.tutorial_step += 1
                st.rerun()


# ---------- SESSION STATE ----------
if "user" not in st.session_state:
    st.session_state.user = None
if "uploader_counter" not in st.session_state:
    st.session_state.uploader_counter = 0
if "tutorial_active" not in st.session_state:
    st.session_state.tutorial_active = False
if "tutorial_step" not in st.session_state:
    st.session_state.tutorial_step = 0
if "note_opened" not in st.session_state:
    st.session_state.note_opened = False

users = load_users()
current_dt, is_online = fetch_online_datetime()
today = current_dt.date()

# ---------- HEADER (always visible) ----------
st.markdown(f'<div class="big-title">{get_daily_heading(today)}</div>', unsafe_allow_html=True)
st.markdown(
    f'<div class="subtitle">Solve {DAILY_TARGET} questions a day. Upload proof. Keep the streak alive.</div>',
    unsafe_allow_html=True,
)
sync_note = "synced online" if is_online else "device time — offline"
st.markdown(
    f'<div class="synced-date">📅 Today: {current_dt.strftime("%A, %d %B %Y")} ({sync_note})</div>',
    unsafe_allow_html=True,
)
st.markdown(f'<div class="quote-card">💬 {get_daily_quote(today)}</div>', unsafe_allow_html=True)

# ---------- SHIVAM'S NOTE (interactive reveal) ----------
if st.button("💌 A note for you, Aditi", use_container_width=True):
    st.session_state.note_opened = not st.session_state.note_opened
    if st.session_state.note_opened:
        st.balloons()

if st.session_state.note_opened:
    st.markdown(f'<div class="note-card">{SHIVAMS_NOTE}</div>', unsafe_allow_html=True)

# ---------- LOGIN / SIGNUP ----------
if st.session_state.user is None:
    st.markdown('<div class="login-card">', unsafe_allow_html=True)
    st.subheader("👋 Welcome — log in or create your account")
    st.caption("New here? Just enter a username and password and hit the button — your account will be created automatically.")

    username = st.text_input("Username").strip()
    password = st.text_input("Password", type="password")

    if st.button("Login / Create Account", use_container_width=True):
        if not username or not password:
            st.error("Please enter both a username and a password.")
        elif username in users:
            if users[username]["password"] == password:
                st.session_state.user = username
                st.rerun()
            else:
                st.error("Incorrect password for that username.")
        else:
            users[username] = new_user_record(password, today.isoformat())
            save_user(username, users[username])
            st.session_state.user = username
            st.success(f"Account created! Welcome, {username} 🎉")
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)
    st.caption("Note: this is a lightweight app for friends/family use — passwords are stored in plain text, so don't reuse a sensitive password here.")

# ---------- LOGGED-IN DASHBOARD ----------
else:
    username = st.session_state.user
    users = check_for_broken_streak(users, username, today)
    record = users[username]
    today_str = today.isoformat()
    todays_entry = record.get("history", {}).get(today_str)
    uploaded_today = bool(todays_entry and todays_entry["uploaded"])
    total_solved, pending = compute_progress(record.get("history", {}), record.get("pending_reset_date"))

    top_col1, top_col2, top_col3 = st.columns([2.2, 1.3, 1])
    with top_col1:
        st.write(f"**Logged in as:** {username}")
    with top_col2:
        if not st.session_state.tutorial_active:
            if st.button("❓ Take the tour", use_container_width=True):
                st.session_state.tutorial_active = True
                st.session_state.tutorial_step = 0
                st.rerun()
    with top_col3:
        if st.button("Logout", use_container_width=True):
            st.session_state.user = None
            st.rerun()

    # ---- Title (locked/unlocked, click to reveal) ----
    def render_title():
        with st.expander("🏆 Tap to reveal your title", expanded=False):
            title = current_title(record["current_streak"])
            st.write(f"**Current Streak:** {record['current_streak']} day(s)")
            if title:
                day, name = title
                st.markdown(f'<div class="title-unlocked">{name}<br><span style="font-size:0.8rem;">(unlocked at Day {day})</span></div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="title-locked">🔒 Keep your streak going to unlock your first title!</div>', unsafe_allow_html=True)

            nxt = next_title(record["current_streak"])
            if nxt:
                nday, _ = nxt
                days_left = nday - record["current_streak"]
                st.caption(f"🔒 Next title unlocks in {days_left} day(s) — keep the streak alive to find out what it is!")

            st.write("—" * 3)
            st.caption("Full title roadmap:")
            rows = []
            for day, name in TITLE_MILESTONES:
                unlocked = record["current_streak"] >= day
                rows.append({
                    "Day": day,
                    "Title": name if unlocked else "🔒 Locked",
                    "Status": "✅ Unlocked" if unlocked else "🔒 Locked",
                })
            df_titles = pd.DataFrame(rows)
            st.dataframe(df_titles, use_container_width=True, hide_index=True, height=250)

    section("title", render_title)

    # ---- Mood card ----
    def render_mood():
        st.markdown(mood_card(uploaded_today), unsafe_allow_html=True)
    section("mood", render_mood)

    # ---- Streak numbers ----
    def render_streak():
        st.markdown(f'<div class="flame-row">{flame_display(record["current_streak"])}</div>', unsafe_allow_html=True)
        st.markdown(
            f"""
            <div class="streak-box">
                <div class="streak-card">
                    <div class="streak-number">{record['current_streak']}</div>
                    <div class="streak-label">Current Streak</div>
                </div>
                <div class="streak-card high">
                    <div class="streak-number">{record['highest_streak']}</div>
                    <div class="streak-label">Highest Streak</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if record["last_upload_date"]:
            st.caption(f"Last check-in: {record['last_upload_date']}")
        else:
            st.caption("No check-ins yet. Upload your first photo to start your streak!")
    section("streak", render_streak)

    # ---- Progress: total solved + pending backlog ----
    def render_progress():
        st.markdown(
            f"""
            <div class="progress-box">
                <div class="streak-card high">
                    <div class="streak-number">{total_solved}</div>
                    <div class="streak-label">Total Questions Solved</div>
                </div>
                <div class="streak-card pending">
                    <div class="streak-number">{pending}</div>
                    <div class="streak-label">Pending Backlog</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if pending > 0:
            st.markdown(
                f'<div class="pending-warning">⚠️ You have <b>{pending}</b> pending question(s) built up. '
                f'Try to clear this by solving extra another day — if backlog goes over {PENDING_LIMIT}, the streak resets!</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown('<div class="pending-ok">✅ No backlog — you\'re fully caught up!</div>', unsafe_allow_html=True)
    section("progress", render_progress)

    st.divider()

    # ---- Check-in flow ----
    def render_checkin_widgets(key_suffix=""):
        uploader_key = f"uploader_{st.session_state.uploader_counter}{key_suffix}"
        uploaded_file = st.file_uploader(
            "Upload today's photo",
            type=["png", "jpg", "jpeg", "webp", "heic"],
            key=uploader_key,
            label_visibility="collapsed",
        )

        if uploaded_file is not None:
            col_prev, col_remove = st.columns([3, 1])
            with col_prev:
                st.image(uploaded_file, caption="Preview", use_container_width=True)
            with col_remove:
                if st.button("❌ Remove", key=f"remove_{key_suffix}"):
                    st.session_state.uploader_counter += 1
                    st.rerun()

            st.write("**How many questions did you complete today?**")
            questions_completed = st.number_input(
                "Questions completed",
                min_value=0,
                max_value=500,
                value=DAILY_TARGET,
                step=1,
                key=f"num_{key_suffix}",
                label_visibility="collapsed",
            )

            if questions_completed < DAILY_TARGET:
                shortfall = DAILY_TARGET - questions_completed
                st.markdown(
                    f'<div class="pending-warning">You\'re {shortfall} question(s) short of today\'s target of {DAILY_TARGET}. '
                    f'This will still count toward your streak, but try to clear the extra {shortfall} soon — '
                    f'total backlog can\'t go over {PENDING_LIMIT} or the streak resets!</div>',
                    unsafe_allow_html=True,
                )
            elif questions_completed > DAILY_TARGET:
                st.markdown(
                    f'<div class="pending-ok">Nice, {questions_completed - DAILY_TARGET} extra question(s) today — that will pay down your backlog!</div>',
                    unsafe_allow_html=True,
                )

            if st.button("✅ Submit Check-in", use_container_width=True, key=f"submit_{key_suffix}"):
                ext = os.path.splitext(uploaded_file.name)[1] or ".jpg"
                already_checked_in = uploaded_today
                new_users = register_upload(
                    users, username, int(questions_completed),
                    uploaded_file.getvalue(), ext, today,
                )
                new_record = new_users[username]

                if already_checked_in:
                    st.info("Today's submission has been updated.")
                else:
                    st.success(f"🎉 Nice work! Streak updated to {new_record['current_streak']} day(s)!")
                    msg = milestone_message(new_record["current_streak"])
                    if msg:
                        st.markdown(f'<div class="milestone-banner">{msg}</div>', unsafe_allow_html=True)
                    st.balloons()

                st.session_state.uploader_counter += 1
                st.rerun()

    def render_checkin():
        if uploaded_today:
            st.success(f"✅ Already checked in today — {todays_entry['questions']} question(s) logged.")
            saved_img = find_saved_image(username, today_str)
            if saved_img:
                st.image(saved_img, caption="Today's submission", use_container_width=True)
            with st.expander("Made a mistake? Update today's submission"):
                render_checkin_widgets(key_suffix="update")
        else:
            st.subheader("📸 Check in for today")
            st.write("Upload a photo of your solved questions to register today's streak.")
            render_checkin_widgets(key_suffix="fresh")

    section("checkin", render_checkin)

    # ---- History log ----
    def render_history():
        st.divider()
        st.subheader("📖 History")
        history = record.get("history", {})
        if history:
            rows = []
            for d in sorted(history.keys(), reverse=True):
                entry = history[d]
                rows.append({
                    "Date": d,
                    "Uploaded": "✅" if entry["uploaded"] else "❌",
                    "Questions Completed": entry.get("questions", 0),
                })
            df = pd.DataFrame(rows)
            with st.expander(f"View full history ({len(rows)} day(s) logged)", expanded=False):
                st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.caption("No history yet — your daily log will build up here.")
    section("history", render_history)

    st.divider()
    st.caption("Missing a full calendar day resets your current streak (and pending backlog) to 0. Your highest streak is always saved.")
