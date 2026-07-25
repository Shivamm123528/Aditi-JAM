import json
import os
from datetime import date, datetime
import streamlit as st

# ---------- CONFIG ----------
DATA_FILE = "users_data.json"

st.set_page_config(
    page_title="Aditi's IIT JAM Streak Tracker",
    page_icon="🎯",
    layout="centered",
)

# ---------- LEVEL TITLES & BADGES ----------
TITLES = [
    (1, "🌱 Beginner", "🥉"),
    (2, "🔥 Spark Starter", "🥉"),
    (3, "⚡ Consistent Learner", "🥉"),
    (5, "📚 Study Warrior", "🥈"),
    (7, "🛡️ Week Crusher", "🥈"),
    (10, "💎 Focus Master", "🥈"),
    (12, "🎯 Matrix Specialist", "🥈"),
    (15, "🚀 Unstoppable Force", "🥇"),
    (18, "🧠 Vector Visionary", "🥇"),
    (20, "👑 Math Champion", "🥇"),
    (25, "🔱 Real Analysis Titan", "🏆"),
    (30, "🌌 Streak Legend", "🏆"),
    (40, "🏛️ JAM Maestro", "👑"),
    (50, "💫 IITian Bound", "👑"),
    (60, "🪐 Supreme Scholar", "👑"),
]


def get_user_title(streak):
    current_title = ("🌱 Beginner", "🥉")
    for min_days, title_name, badge in TITLES:
        if streak >= min_days:
            current_title = (title_name, badge)
        else:
            break
    return current_title


# ---------- STYLING (High-Contrast White Theme) ----------
st.markdown(
    """
    <style>
    /* Main Background & Text Color Defaults */
    .stApp {
        background-color: #FFFFFF !important;
        color: #000000 !important;
    }
    
    /* Input Labels and Inputs Visibility */
    label, p, span, div {
        color: #000000 !important;
    }
    
    .stTextInput input {
        color: #000000 !important;
        background-color: #F8F9FA !important;
        border: 2px solid #333333 !important;
        border-radius: 8px !important;
    }
    
    .big-title {
        font-size: 2.3rem;
        font-weight: 900;
        text-align: center;
        margin-bottom: 0.1rem;
        color: #111111 !important;
    }
    
    .live-time-bar {
        text-align: center;
        font-size: 1.05rem;
        font-weight: 700;
        background: #F0F2F6;
        padding: 0.6rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        border: 1px solid #CCCCCC;
    }
    
    .streak-box {
        display: flex;
        justify-content: space-between;
        gap: 1rem;
        margin-bottom: 1rem;
    }
    
    .streak-card {
        flex: 1;
        background: #F8F9FA;
        border-radius: 16px;
        padding: 1.2rem 0.5rem;
        text-align: center;
        border: 2px solid #222222;
        box-shadow: 3px 3px 0px #000000;
    }
    
    .streak-number {
        font-size: 2.6rem;
        font-weight: 900;
        color: #000000 !important;
    }
    
    .streak-label {
        font-size: 0.85rem;
        color: #333333 !important;
        font-weight: 700;
        text-transform: uppercase;
        margin-top: 0.2rem;
    }
    
    .baby-card {
        text-align: center;
        background: #FFF5F5;
        border: 2px solid #FF8080;
        padding: 1.2rem;
        border-radius: 15px;
        margin-bottom: 1rem;
    }
    
    .baby-card-happy {
        text-align: center;
        background: #F0FFF4;
        border: 2px solid #68D391;
        padding: 1.2rem;
        border-radius: 15px;
        margin-bottom: 1rem;
    }
    
    .title-badge-card {
        text-align: center;
        background: #EDF2F7;
        border: 2px solid #4A5568;
        padding: 0.8rem;
        border-radius: 12px;
        font-weight: 800;
        font-size: 1.2rem;
        margin-bottom: 1rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------- DATA PERSISTENCE ----------
def load_users():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}


def save_users(users):
    with open(DATA_FILE, "w") as f:
        json.dump(users, f, indent=4)


def new_user_record(password):
    return {
        "password": password,
        "current_streak": 0,
        "highest_streak": 0,
        "last_upload_date": None,
        "history": [],  # List of records: {"date": "YYYY-MM-DD", "uploaded": True/False, "questions_done": 50}
    }


def check_for_broken_streak(users, username):
    record = users[username]
    if record["last_upload_date"] is None:
        return users

    last_date = datetime.strptime(
        record["last_upload_date"], "%Y-%m-%d"
    ).date()
    today = date.today()
    gap_days = (today - last_date).days

    if gap_days > 1 and record["current_streak"] != 0:
        record["current_streak"] = 0
        save_users(users)

    return users


# ---------- SESSION STATE ----------
if "user" not in st.session_state:
    st.session_state.user = None

users = load_users()

# ---------- HEADER ----------
st.markdown(
    '<div class="big-title">🎯 Aditi\'s IIT JAM Streak Tracker</div>',
    unsafe_allow_html=True,
)

# Online Real-time Display
now = datetime.now()
current_time_str = now.strftime("%A, %d %B %Y | %I:%M %p")
st.markdown(
    f'<div class="live-time-bar">🕒 <b>Current Date & Time:</b> {current_time_str}</div>',
    unsafe_allow_html=True,
)

# ---------- LOGIN / SIGNUP ----------
if st.session_state.user is None:
    st.subheader("🔑 Account Access")
    username = st.text_input("Username").strip()
    password = st.text_input("Password", type="password")

    if st.button("Login / Register Account", use_container_width=True):
        if not username or not password:
            st.error("Please fill in both fields.")
        elif username in users:
            if users[username]["password"] == password:
                st.session_state.user = username
                st.rerun()
            else:
                st.error("Incorrect password.")
        else:
            users[username] = new_user_record(password)
            save_users(users)
            st.session_state.user = username
            st.success(f"Account created successfully for {username}!")
            st.rerun()

# ---------- LOGGED-IN DASHBOARD ----------
else:
    username = st.session_state.user
    users = check_for_broken_streak(users, username)
    record = users[username]

    col1, col2 = st.columns([3, 1])
    with col1:
        st.write(f"### 👋 Welcome back, **{username}**!")
    with col2:
        if st.button("Logout", use_container_width=True):
            st.session_state.user = None
            st.rerun()

    # Title & Level Badge
    title_name, badge = get_user_title(record["current_streak"])
    st.markdown(
        f'<div class="title-badge-card">{badge} Rank Title: {title_name}</div>',
        unsafe_allow_html=True,
    )

    # Streak Cards
    st.markdown(
        f"""
        <div class="streak-box">
            <div class="streak-card">
                <div class="streak-number">🔥 {record['current_streak']}</div>
                <div class="streak-label">Current Streak</div>
            </div>
            <div class="streak-card">
                <div class="streak-number">🏆 {record['highest_streak']}</div>
                <div class="streak-label">Highest Streak</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    today_str = date.today().isoformat()
    already_uploaded_today = record["last_upload_date"] == today_str

    # Cute Reaction Baby Display
    if not already_uploaded_today:
        st.markdown(
            """
            <div class="baby-card">
                <h1 style="margin:0; font-size: 3.5rem;">🥺👶</h1>
                <h3 style="margin:0.5rem 0 0 0; color: #C53030 !important;">"Please study and complete 50 questions today... don't break our streak!"</h3>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            """
            <div class="baby-card-happy">
                <h1 style="margin:0; font-size: 3.5rem;">🥳👶</h1>
                <h3 style="margin:0.5rem 0 0 0; color: #276749 !important;">"Yay! You uploaded proof and saved the streak today! Super proud of you!"</h3>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.divider()

    # ---------- DAILY CHECK-IN SECTION ----------
    st.subheader("📝 Daily Progress Check-in")

    uploaded_file = st.file_uploader(
        "Upload proof photo (Last Solved Question):",
        type=["png", "jpg", "jpeg", "webp"],
    )

    q_completed = st.radio(
        "Did you complete all 50 questions today?",
        ["Yes", "No"],
        horizontal=True,
    )

    questions_done_count = 50
    if q_completed == "No":
        questions_done_count = st.number_input(
            "How many questions did you complete today?",
            min_value=0,
            max_value=50,
            value=0,
        )

    if uploaded_file is not None:
        st.image(
            uploaded_file,
            caption="Uploaded Proof Preview",
            use_container_width=True,
        )

        col_save, col_del = st.columns(2)

        with col_save:
            if st.button("Confirm Check-in", use_container_width=True):
                if not already_uploaded_today:
                    record["current_streak"] += 1
                    if record["current_streak"] > record["highest_streak"]:
                        record["highest_streak"] = record["current_streak"]

                record["last_upload_date"] = today_str

                # Update History Log
                history = record.get("history", [])
                history = [h for h in history if h["date"] != today_str]
                history.append(
                    {
                        "date": today_str,
                        "uploaded": True,
                        "questions_done": questions_done_count,
                    }
                )
                record["history"] = history

                save_users(users)
                st.balloons()
                st.success("Check-in recorded successfully! 🎉")
                st.rerun()

        with col_del:
            if st.button(
                "❌ Remove / Delete File",
                type="primary",
                use_container_width=True,
            ):
                st.warning("File preview cleared. You can now select a new file.")
                st.rerun()

    st.divider()

    # ---------- HISTORY BOX ----------
    st.subheader("📜 Activity History Log")
    history_logs = record.get("history", [])

    if not history_logs:
        st.info("No records in history yet. Complete a check-in above!")
    else:
        for entry in reversed(history_logs):
            status = "✅ Uploaded Proof" if entry["uploaded"] else "❌ Missed"
            st.write(
                f"• **Date:** `{entry['date']}` | **Status:** {status} | **Questions Solved:** `{entry['questions_done']}/50`"
            )
