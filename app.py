import streamlit as st
import json
import os
import requests
import pandas as pd
from datetime import date, datetime, timedelta

# ---------- CONFIG ----------
DATA_FILE = "users_data.json"
UPLOADS_DIR = "uploads"

st.set_page_config(
    page_title="Study Streak Tracker",
    page_icon="🔥",
    layout="centered",
)

# ---------- ONLINE DATE/TIME SYNC ----------
@st.cache_data(ttl=1800)
def fetch_online_datetime():
    """Try to fetch the real current date/time from the internet so the
    streak can't be fooled by a wrong device clock. Falls back to the
    server's local date if the request fails."""
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


def get_today():
    dt, _ = fetch_online_datetime()
    return dt.date()


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
    idx = today.toordinal() % len(QUOTES)
    return QUOTES[idx]


# ---------- STREAK TITLES ----------
TITLE_MILESTONES = [
    (1, "First Spark", "✨"),
    (2, "Warming Up", "🌤️"),
    (3, "Building Momentum", "💪"),
    (5, "High Five", "🖐️"),
    (7, "One Week Wonder", "🌟"),
    (10, "Double Digits", "🔟"),
    (12, "Dozen Strong", "📚"),
    (15, "Halfway Hero", "⏳"),
    (18, "Eighteen & Grinding", "⚙️"),
    (20, "Twenty Titan", "💥"),
    (25, "Quarter Century", "🎯"),
    (30, "Monthly Master", "📆"),
    (40, "Fantastic Forty", "🚀"),
    (50, "Half-Century Hero", "🏅"),
    (60, "Unstoppable", "🔥"),
    (75, "Diamond Focus", "💎"),
    (100, "Century Club", "🏆"),
    (150, "Iron Will", "🛡️"),
    (200, "Marathoner", "🏃"),
    (365, "Full Year Legend", "👑"),
]


def current_title(streak):
    achieved = [t for t in TITLE_MILESTONES if t[0] <= streak]
    return achieved[-1] if achieved else None


def next_title(streak):
    upcoming = [t for t in TITLE_MILESTONES if t[0] > streak]
    return upcoming[0] if upcoming else None


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
    <svg width="120" height="120" viewBox="0 0 160 160" xmlns="http://www.w3.org/2000/svg">
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
                border-radius:18px;padding:0.9rem 1.1rem;margin-bottom:1rem;
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

    /* Force readable dark text everywhere on our light background,
       regardless of the user's light/dark system theme. */
    .stApp, .stApp p, .stApp span, .stApp li,
    .stMarkdown, .stMarkdown p, .stCaption, [data-testid="stCaptionContainer"],
    label, .stTextInput label p, .stNumberInput label p, .stRadio label p,
    h1, h2, h3, h4, h5, h6, .stSubheader {
        color: #3a2a20 !important;
    }

    /* Make native text/number inputs clearly visible: white bg, black text */
    input[type="text"], input[type="password"], input[type="number"], textarea {
        background-color: #ffffff !important;
        color: #000000 !important;
        caret-color: #000000 !important;
        border: 1px solid #e0c4a8 !important;
    }

    .big-title {
        font-size: 2.2rem;
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
    .streak-box {
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
    .streak-card.high {
        background: linear-gradient(160deg, #ffffff, #d9f7e3);
        box-shadow: 0 6px 16px rgba(30,150,80,0.15);
    }
    .streak-number {
        font-size: 2.6rem;
        font-weight: 900;
        color: #3a2a20 !important;
    }
    .streak-card.high .streak-number {
        color: #1f6d3f !important;
    }
    .streak-label {
        font-size: 0.8rem;
        color: #77675e !important;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-top: 0.2rem;
    }
    .login-card {
        background: rgba(255,255,255,0.75);
        border-radius: 20px;
        padding: 1.6rem 1.4rem;
        box-shadow: 0 8px 24px rgba(0,0,0,0.08);
        margin-top: 0.6rem;
    }
    .flame-row {
        text-align: center;
        font-size: 1.6rem;
        letter-spacing: 0.15em;
        margin-bottom: 0.6rem;
    }
    .stApp .milestone-banner {
        text-align: center;
        background: linear-gradient(90deg, #f09819, #ff512f);
        color: #ffffff !important;
        border-radius: 12px;
        padding: 0.6rem;
        font-weight: 700;
        margin-bottom: 1rem;
    }
    .stApp .title-banner {
        text-align: center;
        background: linear-gradient(90deg, #6a3de8, #a06bff);
        color: #ffffff !important;
        border-radius: 14px;
        padding: 0.8rem;
        font-weight: 700;
        font-size: 1.05rem;
        margin-bottom: 0.5rem;
        box-shadow: 0 6px 16px rgba(106,61,232,0.25);
    }
    .stApp .title-banner * {
        color: #ffffff !important;
    }
    .next-title-caption {
        text-align: center;
        color: #8a6a52 !important;
        font-size: 0.85rem;
        margin-bottom: 1rem;
    }
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
    """Fill in any calendar days between the last upload and today (exclusive)
    as 'not uploaded', so the history log has no gaps."""
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


def register_upload(users, username, questions_completed, file_bytes, file_ext, today):
    record = users[username]
    today_str = today.isoformat()

    if record["last_upload_date"] is None:
        record["current_streak"] = 1
    else:
        last_date = datetime.strptime(record["last_upload_date"], "%Y-%m-%d").date()
        gap_days = (today - last_date).days

        if gap_days == 0:
            pass  # already checked in today, streak unaffected
        elif gap_days == 1:
            record["current_streak"] += 1
        else:
            record["current_streak"] = 1

    record["last_upload_date"] = today_str
    record["highest_streak"] = max(record["highest_streak"], record["current_streak"])
    record.setdefault("history", {})[today_str] = {
        "uploaded": True,
        "questions": questions_completed,
    }
    save_users(users)

    # Persist the image so it can be shown again later
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


def milestone_message(streak):
    title = current_title(streak)
    if title and title[0] == streak:
        day, name, emoji = title
        return f"🏆 Day {day} unlocked: {emoji} {name}!"
    return None


# ---------- SESSION STATE ----------
if "user" not in st.session_state:
    st.session_state.user = None
if "uploader_counter" not in st.session_state:
    st.session_state.uploader_counter = 0

users = load_users()
current_dt, is_online = fetch_online_datetime()
today = current_dt.date()

# ---------- HEADER (always visible) ----------
st.markdown('<div class="big-title">🔥 Study Streak Tracker</div>', unsafe_allow_html=True)
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

    top_col1, top_col2 = st.columns([3, 1])
    with top_col1:
        st.write(f"**Logged in as:** {username}")
    with top_col2:
        if st.button("Logout"):
            st.session_state.user = None
            st.rerun()

    # Title banner
    title = current_title(record["current_streak"])
    if title:
        day, name, emoji = title
        st.markdown(f'<div class="title-banner">{emoji} Current Title: {name} (Day {day}+)</div>', unsafe_allow_html=True)
    nxt = next_title(record["current_streak"])
    if nxt:
        day, name, emoji = nxt
        days_left = day - record["current_streak"]
        st.markdown(
            f'<div class="next-title-caption">Next title in {days_left} day(s): {emoji} {name} (Day {day})</div>',
            unsafe_allow_html=True,
        )

    st.markdown(mood_card(uploaded_today), unsafe_allow_html=True)
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

    st.divider()

    # ---------- CHECK-IN FLOW ----------
    def render_checkin_widgets(key_suffix=""):
        """Renders the uploader + Yes/No + submit flow. Shared for a fresh
        check-in and for updating an already-submitted day."""
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

            completed_all = st.radio(
                "Did you complete all 50 questions today?",
                ["Yes", "No"],
                horizontal=True,
                key=f"radio_{key_suffix}",
            )
            if completed_all == "Yes":
                questions_completed = 50
            else:
                questions_completed = st.number_input(
                    "How many questions have you completed?",
                    min_value=0,
                    max_value=49,
                    value=25,
                    step=1,
                    key=f"num_{key_suffix}",
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

    # ---------- HISTORY LOG ----------
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

    st.divider()
    st.caption("Missing a full calendar day resets your current streak to 0. Your highest streak is always saved.")
