import streamlit as st
import json
import os
from datetime import date, datetime

# ---------- CONFIG ----------
DATA_FILE = "users_data.json"

st.set_page_config(
    page_title="Study Streak Tracker",
    page_icon="🔥",
    layout="centered",
)

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


def get_daily_quote():
    idx = date.today().toordinal() % len(QUOTES)
    return QUOTES[idx]


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
        max-width: 520px;
    }
    .big-title {
        font-size: 2.3rem;
        font-weight: 900;
        text-align: center;
        margin-bottom: 0.1rem;
        background: linear-gradient(90deg, #ff512f, #f09819);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .subtitle {
        text-align: center;
        color: #7a5c4f;
        margin-bottom: 1rem;
        font-size: 0.95rem;
    }
    .quote-card {
        background: rgba(255,255,255,0.6);
        backdrop-filter: blur(6px);
        border-left: 5px solid #f09819;
        border-radius: 12px;
        padding: 0.9rem 1.1rem;
        font-style: italic;
        color: #5a4433;
        margin-bottom: 1.4rem;
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
    }
    .streak-label {
        font-size: 0.8rem;
        color: #77675e;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-top: 0.2rem;
    }
    .login-card {
        background: rgba(255,255,255,0.7);
        border-radius: 20px;
        padding: 1.8rem 1.5rem;
        box-shadow: 0 8px 24px rgba(0,0,0,0.08);
        margin-top: 1rem;
    }
    .flame-row {
        text-align: center;
        font-size: 1.6rem;
        letter-spacing: 0.15em;
        margin-bottom: 0.6rem;
    }
    .milestone-banner {
        text-align: center;
        background: linear-gradient(90deg, #f09819, #ff512f);
        color: white;
        border-radius: 12px;
        padding: 0.6rem;
        font-weight: 700;
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


def new_user_record(password):
    return {
        "password": password,
        "current_streak": 0,
        "highest_streak": 0,
        "last_upload_date": None,
    }


def check_for_broken_streak(users, username):
    record = users[username]
    if record["last_upload_date"] is None:
        return users

    last_date = datetime.strptime(record["last_upload_date"], "%Y-%m-%d").date()
    today = date.today()
    gap_days = (today - last_date).days

    if gap_days > 1 and record["current_streak"] != 0:
        record["current_streak"] = 0
        save_users(users)

    return users


def register_upload(users, username):
    record = users[username]
    today = date.today()
    today_str = today.isoformat()

    if record["last_upload_date"] is None:
        record["current_streak"] = 1
    else:
        last_date = datetime.strptime(record["last_upload_date"], "%Y-%m-%d").date()
        gap_days = (today - last_date).days

        if gap_days == 0:
            pass  # already checked in today, no double counting
        elif gap_days == 1:
            record["current_streak"] += 1
        else:
            record["current_streak"] = 1

    record["last_upload_date"] = today_str
    record["highest_streak"] = max(record["highest_streak"], record["current_streak"])
    save_users(users)
    return users


MILESTONES = [3, 7, 14, 30, 50, 100, 200, 365]


def milestone_message(streak):
    if streak in MILESTONES:
        return f"🏆 Milestone unlocked: {streak}-day streak! Incredible work."
    return None


def flame_display(streak):
    if streak == 0:
        return "💤"
    count = min(streak, 10)
    return "🔥" * count


# ---------- SESSION STATE ----------
if "user" not in st.session_state:
    st.session_state.user = None

users = load_users()

# ---------- HEADER (always visible) ----------
st.markdown('<div class="big-title">🔥 Study Streak Tracker</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">Solve 50 questions a day. Upload proof. Keep the streak alive.</div>',
    unsafe_allow_html=True,
)
st.markdown(f'<div class="quote-card">💬 {get_daily_quote()}</div>', unsafe_allow_html=True)

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
            users[username] = new_user_record(password)
            save_users(users)
            st.session_state.user = username
            st.success(f"Account created! Welcome, {username} 🎉")
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)
    st.caption("Note: this is a lightweight app for friends/family use — passwords are stored in plain text, so don't reuse a sensitive password here.")

# ---------- LOGGED-IN DASHBOARD ----------
else:
    username = st.session_state.user
    users = check_for_broken_streak(users, username)
    record = users[username]

    top_col1, top_col2 = st.columns([3, 1])
    with top_col1:
        st.write(f"**Logged in as:** {username}")
    with top_col2:
        if st.button("Logout"):
            st.session_state.user = None
            st.rerun()

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

    # progress toward next milestone
    upcoming = next((m for m in MILESTONES if m > record["current_streak"]), None)
    if upcoming:
        progress = record["current_streak"] / upcoming
        st.progress(min(progress, 1.0), text=f"{record['current_streak']}/{upcoming} days to next milestone")

    st.divider()

    st.subheader("📸 Check in for today")
    st.write("Upload a photo of your 50th solved question to register today's streak.")

    uploaded_file = st.file_uploader(
        "Upload today's photo",
        type=["png", "jpg", "jpeg", "webp", "heic"],
        label_visibility="collapsed",
    )

    if uploaded_file is not None:
        already_checked_in_today = record["last_upload_date"] == date.today().isoformat()

        users = register_upload(users, username)
        record = users[username]

        if already_checked_in_today:
            st.info("✅ You've already checked in today — streak stays the same, but great job studying more!")
        else:
            st.success(f"🎉 Nice work! Streak updated to {record['current_streak']} day(s)!")
            msg = milestone_message(record["current_streak"])
            if msg:
                st.markdown(f'<div class="milestone-banner">{msg}</div>', unsafe_allow_html=True)
            st.balloons()

        st.image(uploaded_file, caption="Today's proof ✅", use_container_width=True)

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

    st.divider()
    st.caption("Missing a full calendar day resets your current streak to 0. Your highest streak is always saved.")
