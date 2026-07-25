import streamlit as st
import json
import os
import requests
import pandas as pd
from datetime import date, datetime, timedelta

# ---------- CONFIG ----------
DATA_FILE = "users_data.json"
UPLOADS_DIR = "uploads"
DAILY_TARGET = 50
PENDING_LIMIT = 40  # if backlog exceeds this, streak resets

st.set_page_config(
    page_title="Aditi's IIT JAM Mission",
    page_icon="🔥",
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
    "🔥 The 50-Question Daily Grind",
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
    "Nobody sees the 50 questions. Everybody sees the result.",
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
    "Today's 50 questions are tomorrow's easy answers.",
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


# ---------- CUTE BABY MOOD ILLUSTRATION (original simple artwork) ----------
def baby_face_svg(mood="sad"):
    if mood == "happy":
        eyebrow_l = "M45,68 Q60,58 75,68"
        eyebrow_r = "M85,68 Q100,58 115,68"
        mouth = "M60,108 Q80,128 100,108"
        tear = ""
    else:
        eyebrow_l = "M45,72 Q60,62 75,72"
        eyebrow_r = "M85,72 Q100,62 115,72"
        mouth = "M60,122 Q80,105 100,122"
        tear = '<path d="M52,92 q-5,10 0,17 q5,-7 0,-17" fill="#7ec8f2"/>'

    return f'''
    <svg width="110" height="110" viewBox="0 0 160 160" xmlns="http://www.w3.org/2000/svg">
      <path d="M50,32 Q80,8 110,32 Q95,20 80,26 Q65,20 50,32 Z" fill="#7a4a2a"/>
      <circle cx="80" cy="88" r="62" fill="#ffe0c2" stroke="#f2b880" stroke-width="3"/>
      <circle cx="52" cy="102" r="9" fill="#ffb0a0" opacity="0.7"/>
      <circle cx="108" cy="102" r="9" fill="#ffb0a0" opacity="0.7"/>
      <circle cx="60" cy="86" r="6" fill="#3a2a20"/>
      <circle cx="100" cy="86" r="6" fill="#3a2a20"/>
      <path d="{eyebrow_l}" stroke="#3a2a20" stroke-width="4" fill="none" stroke-linecap="round"/>
      <path d="{eyebrow_r}" stroke="#3a2a20" stroke-width="4" fill="none" stroke-linecap="round"/>
      <path d="{mouth}" stroke="#a15c3e" stroke-width="4" fill="none" stroke-linecap="round"/>
      {tear}
    </svg>
    '''


def mood_card(uploaded_today):
    if uploaded_today:
        svg = baby_face_svg("happy")
        text = "Yay! You showed up today! Keep the streak alive! 🎉"
    else:
        svg = baby_face_svg("sad")
        text = "I haven't seen today's upload yet... please study! 📚"
    return f"""
    <div style="display:flex;align-items:center;gap:1rem;background:rgba(255,255,255,0.65);
                border-radius:18px;padding:0.9rem 1.1rem;margin-bottom:0.6rem;
                box-shadow:0 4px 14px rgba(0,0,0,0.06);">
        <div>{svg}</div>
        <div style="font-weight:700;color:#4a3626;font-size:1.05rem;">{text}</div>
    </div>
    """


def flame_display(streak):
    if streak == 0:
        return "💤"
    return "🔥" * min(streak, 10)


# ---------- STYLING ----------
st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(160deg, #fff7ed 0%, #ffe8d6 40%, #ffd9c2 100%);
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
        color: #3a2a20 !important;
    }
    input[type="text"], input[type="password"], input[type="number"], textarea {
        background-color: #ffffff !important;
        color: #000000 !important;
        caret-color: #000000 !important;
        border: 1px solid #e0c4a8 !important;
    }
    /* Buttons: always visible, never dark-on-dark */
    .stButton > button, .stDownloadButton > button {
        background: linear-gradient(135deg, #ffffff, #ffe3c2) !important;
        color: #3a2a20 !important;
        border: 1.5px solid #f0a848 !important;
        font-weight: 700 !important;
        box-shadow: 0 3px 10px rgba(240,120,20,0.15);
    }
    .stButton > button:hover, .stDownloadButton > button:hover {
        background: linear-gradient(135deg, #fff3e0, #ffcf94) !important;
        color: #3a2a20 !important;
        border: 1.5px solid #f09819 !important;
    }
    .stButton > button p, .stButton > button span, .stButton > button div {
        color: #3a2a20 !important;
    }
    /* Expander headers: same treatment */
    [data-testid="stExpander"] summary {
        background: linear-gradient(135deg, #ffffff, #ffe3c2) !important;
        border-radius: 10px !important;
        border: 1.5px solid #f0a848 !important;
    }
    [data-testid="stExpander"] summary span,
    [data-testid="stExpander"] summary p {
        color: #3a2a20 !important;
        font-weight: 700 !important;
    }
    .big-title {
        font-size: 2.0rem;
        font-weight: 900;
        text-align: center;
        margin-bottom: 0.1rem;
        background: linear-gradient(90deg, #ff512f, #f09819);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .subtitle {
        text-align: center;
        color: #6b4a38 !important;
        margin-bottom: 0.3rem;
        font-size: 0.95rem;
    }
    .synced-date {
        text-align: center;
        color: #8a6a52 !important;
        font-size: 0.85rem;
        margin-bottom: 1rem;
    }
    .quote-card {
        background: rgba(255,255,255,0.6);
        border-left: 5px solid #f09819;
        border-radius: 12px;
        padding: 0.9rem 1.1rem;
        font-style: italic;
        color: #4a3626 !important;
        margin-bottom: 1.2rem;
        box-shadow: 0 4px 14px rgba(0,0,0,0.06);
    }
    .streak-box, .progress-box {
        display: flex;
        justify-content: space-between;
        gap: 1rem;
        margin-bottom: 1rem;
    }
    .streak-card {
        flex: 1;
        background: linear-gradient(160deg, #ffffff, #ffe9d6);
        border-radius: 18px;
        padding: 1.3rem 0.5rem;
        text-align: center;
        box-shadow: 0 6px 16px rgba(240,90,10,0.15);
        border: 1px solid rgba(255,255,255,0.6);
    }
    .streak-card.high { background: linear-gradient(160deg, #ffffff, #d9f7e3); box-shadow: 0 6px 16px rgba(30,150,80,0.15); }
    .streak-card.pending { background: linear-gradient(160deg, #ffffff, #ffe0e0); box-shadow: 0 6px 16px rgba(200,40,40,0.12); }
    .streak-number { font-size: 2.4rem; font-weight: 900; color: #3a2a20 !important; }
    .streak-card.high .streak-number { color: #1f6d3f !important; }
    .streak-card.pending .streak-number { color: #b03030 !important; }
    .streak-label { font-size: 0.78rem; color: #77675e !important; text-transform: uppercase; letter-spacing: 0.07em; margin-top: 0.2rem; }
    .login-card { background: rgba(255,255,255,0.75); border-radius: 20px; padding: 1.6rem 1.4rem; box-shadow: 0 8px 24px rgba(0,0,0,0.08); margin-top: 0.6rem; }
    .flame-row { text-align: center; font-size: 1.5rem; letter-spacing: 0.15em; margin-bottom: 0.4rem; }
    .stApp .milestone-banner { text-align: center; background: linear-gradient(90deg, #f09819, #ff512f); color:#fff !important; border-radius: 12px; padding: 0.6rem; font-weight: 700; margin-bottom: 1rem; }
    .stApp .title-unlocked { text-align: center; background: linear-gradient(90deg, #6a3de8, #a06bff); color:#fff !important; border-radius: 14px; padding: 0.9rem; font-weight: 700; font-size: 1.1rem; margin-bottom: 0.4rem; }
    .stApp .title-unlocked * { color: #fff !important; }
    .stApp .title-locked { text-align: center; background: #eee2d6; color:#7a6a5c !important; border-radius: 14px; padding: 0.9rem; font-weight: 600; margin-bottom: 0.4rem; }
    .note-card { background: linear-gradient(135deg, #ffe8e8, #ffd8ec); border-radius: 16px; padding: 1.1rem 1.3rem; margin-bottom: 1rem; box-shadow: 0 6px 16px rgba(255,80,150,0.15); font-size: 0.98rem; line-height: 1.5; color:#5a2b3a !important; white-space: pre-line; }
    .tutorial-glow { border-radius: 18px; box-shadow: 0 0 0 4px #ffe066, 0 0 24px 8px rgba(255,190,40,0.7); padding: 0.5rem; margin-bottom: 0.4rem; transition: box-shadow 0.3s; }
    .tutorial-callout { background: #2b2b2b; color: #ffe066 !important; border-radius: 10px; padding: 0.7rem 1rem; margin-bottom: 0.6rem; font-weight: 600; }
    .tutorial-callout * { color: #ffe066 !important; }
    .pending-warning { background: #fff0e0; border-left: 5px solid #e07b00; border-radius: 10px; padding: 0.7rem 1rem; margin: 0.6rem 0; color:#7a3e00 !important; font-weight:600; }
    .pending-ok { background: #e6f8ea; border-left: 5px solid #2e9e50; border-radius: 10px; padding: 0.7rem 1rem; margin: 0.6rem 0; color:#1f6d3f !important; font-weight:600; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------- DATA PERSISTENCE (multi-user) ----------
def load_users():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}


def save_users(users):
    with open(DATA_FILE, "w") as f:
        json.dump(users, f)


def new_user_record(password, today_str):
    return {
        "password": password,
        "current_streak": 0,
        "highest_streak": 0,
        "last_upload_date": None,
        "created_date": today_str,
        "history": {},
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
        changed = True
    if changed:
        save_users(users)
    return users


def compute_progress(history):
    """Replays the whole history to get a running total of questions solved
    and the current pending backlog (days where fewer than 50 were logged
    build up backlog; extra questions on a good day pay it down)."""
    total_solved = 0
    pending = 0
    for d in sorted(history.keys()):
        entry = history[d]
        q = entry.get("questions", 0) if entry.get("uploaded") else 0
        total_solved += q
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

    # Recompute backlog; if it's grown past the limit, the streak breaks
    _, pending = compute_progress(record["history"])
    if pending > PENDING_LIMIT:
        record["current_streak"] = 0

    record["highest_streak"] = max(record["highest_streak"], record["current_streak"])
    save_users(users)

    folder = os.path.join(UPLOADS_DIR, username)
    os.makedirs(folder, exist_ok=True)
    filepath = os.path.join(folder, f"{today_str}{file_ext}")
    with open(filepath, "wb") as f:
        f.write(file_bytes)

    return users


def find_saved_image(username, date_str):
    folder = os.path.join(UPLOADS_DIR, username)
    if not os.path.isdir(folder):
        return None
    for fname in os.listdir(folder):
        if fname.startswith(date_str):
            return os.path.join(folder, fname)
    return None


# ---------- TUTORIAL / GUIDED TOUR ----------
TUTORIAL_STEPS = [
    {"target": "title", "text": "👉 Tap this box to reveal your current title! Titles stay locked until your streak reaches that many days."},
    {"target": "mood", "text": "👉 This little character shows how today is going — sad if you haven't checked in yet, happy once you have!"},
    {"target": "streak", "text": "👉 These are your Current Streak and your all-time Highest Streak. Don't let the first one hit zero!"},
    {"target": "progress", "text": "👉 Here's your total questions solved and any pending backlog. Keep backlog under 40 or the streak resets!"},
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
    '<div class="subtitle">Solve 50 questions a day. Upload proof. Keep the streak alive.</div>',
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
            save_users(users)
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
    total_solved, pending = compute_progress(record.get("history", {}))

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
                value=50,
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
    st.caption("Missing a full calendar day resets your current streak to 0. Your highest streak is always saved.")
