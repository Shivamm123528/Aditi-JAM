import os
import random
import requests
import pandas as pd
import streamlit as st
from datetime import date, datetime, timedelta
from supabase import create_client, Client

# ---------- CONFIG ----------
DAILY_TARGET = 40
PENDING_LIMIT = 35  
STORAGE_BUCKET = "checkin-photos"

# ---------- SUPABASE CLIENT ----------
@st.cache_resource
def get_supabase_client() -> Client:
    url = st.secrets["supabase"]["url"]
    key = st.secrets["supabase"]["key"]
    return create_client(url, key)

supabase = get_supabase_client()

st.set_page_config(
    page_title="Aditi's IIT JAM Mission",
    page_icon="🚀",
    layout="centered",
)

# ---------- ONLINE DATE/TIME SYNC ----------
@st.cache_data(ttl=1800)
def fetch_online_datetime():
    try:
        resp = requests.get("https://worldtimeapi.org/api/timezone/Asia/Kolkata", timeout=5)
        resp.raise_for_status()
        data = resp.json()
        dt = datetime.fromisoformat(data["datetime"])
        return dt.replace(tzinfo=None), True
    except Exception:
        return datetime.now(), False

HEADINGS = [
    "🎯 Aditi's IIT JAM Mission",
    "🚀 Operation JAM 2027: Daily Tracker",
    "⚡ Aditi vs. The Syllabus",
    "📈 Aditi's Math Mastery Streak",
]

def get_daily_heading(today):
    return HEADINGS[today.toordinal() % len(HEADINGS)]

QUOTES = [
    "Small steps every day add up to something huge.",
    "Discipline is choosing what you want most over what you want now.",
    "You don't have to be perfect, you just have to show up.",
    "Every question you solve today is a rep for your brain.",
    "Consistency beats intensity. Keep stacking days.",
    "Future you is already proud of today's effort.",
]

def get_daily_quote(today):
    return QUOTES[today.toordinal() % len(QUOTES)]

SHIVAMS_NOTE = (
    "Hey Aditi, I built this app specifically for you to channel your focus and energy into your "
    "JAM maths prep. Keep the streak active, don't break the chain, and crack this exam. "
    "Let's get that streak scaling up high!\n\n— Shivam"
)

TITLE_MILESTONES = [
    (1, "🌱 The First Step"),
    (2, "🔥 Spark Ignited"),
    (3, "⚙️ Building Momentum"),
    (5, "🏃‍♀️ Pace Setter"),
    (10, "🛡️ Double Digits Defender"),
    (15, "⚔️ Half-Month Hero"),
    (30, "🌙 Full Month Legend"),
    (50, "🔱 Half-Century Scholar"),
    (100, "🌠 The 100+ Phenomenon"),
    (365, "🎇 One Year Legend (JAM Ready)"),
]

def current_title(streak):
    achieved = [t for t in TITLE_MILESTONES if t[0] <= streak]
    return achieved[-1] if achieved else None

def next_title(streak):
    upcoming = [t for t in TITLE_MILESTONES if t[0] > streak]
    return upcoming[0] if upcoming else None

# ---------- STYLING & CINEMATIC MOVIE BANNER ----------
st.markdown("""
    <style>
    .stApp {
        background-color: #0e1117;
        color: #e6edfd;
    }
    .main .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
        max-width: 540px;
    }
    .big-title {
        font-size: 1.9rem;
        font-weight: 800;
        text-align: center;
        margin-bottom: 0.1rem;
        color: #58a6ff;
    }
    .subtitle { text-align: center; color: #8b949e; margin-bottom: 0.8rem; font-size: 0.95rem; }
    .synced-date { text-align: center; color: #8b949e; font-size: 0.85rem; margin-bottom: 1rem; }
    .quote-card {
        background: #161b22;
        border-left: 4px solid #58a6ff;
        border-radius: 8px;
        padding: 0.9rem 1.1rem;
        font-style: italic;
        margin-bottom: 1.2rem;
        border: 1px solid #30363d;
    }
    .streak-box { display: flex; justify-content: space-between; gap: 1rem; margin-bottom: 1rem; }
    .streak-card {
        flex: 1;
        background: #161b22;
        border-radius: 12px;
        padding: 1.2rem 0.5rem;
        text-align: center;
        border: 1px solid #30363d;
    }
    .streak-number { font-size: 2.2rem; font-weight: 900; color: #58a6ff; }
    .streak-label { font-size: 0.75rem; color: #8b949e; text-transform: uppercase; letter-spacing: 0.05em; margin-top: 0.2rem; }
    .login-card { background: #161b22; border-radius: 14px; padding: 1.6rem 1.4rem; border: 1px solid #30363d; margin-top: 0.6rem; }
    .note-card { background: #1f242c; border: 1px solid #58a6ff; border-radius: 12px; padding: 1.1rem 1.3rem; margin-bottom: 1rem; font-size: 0.95rem; line-height: 1.5; white-space: pre-line; }
    </style>
""", unsafe_allow_html=True)

# ---------- DATA PERSISTENCE ----------
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

def compute_progress(history, reset_date=None):
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

# ---------- APP ENTRY ----------
if "user" not in st.session_state:
    st.session_state.user = None
if "uploader_counter" not in st.session_state:
    st.session_state.uploader_counter = 0
if "note_opened" not in st.session_state:
    st.session_state.note_opened = False

users = load_users()
current_dt, is_online = fetch_online_datetime()
today = current_dt.date()

# Cinematic Movie Banner Image Integration
st.image(
    "https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=1000&q=80",
    caption="Operation Focus — Engineering & Mathematics Hub",
    use_container_width=True
)

st.markdown(f'<div class="big-title">{get_daily_heading(today)}</div>', unsafe_allow_html=True)
st.markdown(f'<div class="subtitle">Solve {DAILY_TARGET} questions daily. Upload proof. Maintain momentum.</div>', unsafe_allow_html=True)

sync_note = "synced online" if is_online else "offline mode"
st.markdown(f'<div class="synced-date">📅 Today: {current_dt.strftime("%A, %d %B %Y")} ({sync_note})</div>', unsafe_allow_html=True)
st.markdown(f'<div class="quote-card">💬 {get_daily_quote(today)}</div>', unsafe_allow_html=True)

if st.button("💌 A note for you, Aditi", use_container_width=True):
    st.session_state.note_opened = not st.session_state.note_opened

if st.session_state.note_opened:
    st.markdown(f'<div class="note-card">{SHIVAMS_NOTE}</div>', unsafe_allow_html=True)

# ---------- LOGIN / SIGNUP UI ----------
if st.session_state.user is None:
    st.markdown('<div class="login-card">', unsafe_allow_html=True)
    st.subheader("👋 Account Login")
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
                st.error("Incorrect password.")
        else:
            users[username] = new_user_record(password, today.isoformat())
            save_user(username, users[username])
            st.session_state.user = username
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

# ---------- DASHBOARD ----------
else:
    username = st.session_state.user
    record = users[username]
    today_str = today.isoformat()
    todays_entry = record.get("history", {}).get(today_str)
    uploaded_today = bool(todays_entry and todays_entry["uploaded"])
    total_solved, pending = compute_progress(record.get("history", {}), record.get("pending_reset_date"))

    top_col1, top_col2 = st.columns([3, 1])
    with top_col1:
        st.write(f"**Logged in as:** {username}")
    with top_col2:
        if st.button("Logout", use_container_width=True):
            st.session_state.user = None
            st.rerun()

    # Current Title Display
    title = current_title(record["current_streak"])
    if title:
        _, name = title
        st.info(f"🎖️ **Milestone Status:** {name}")

    # Streaks View
    st.markdown(f"""
        <div class="streak-box">
            <div class="streak-card">
                <div class="streak-number">{record['current_streak']}</div>
                <div class="streak-label">Current Streak</div>
            </div>
            <div class="streak-card">
                <div class="streak-number">{record['highest_streak']}</div>
                <div class="streak-label">Highest Streak</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Progress Stats View
    st.markdown(f"""
        <div class="streak-box">
            <div class="streak-card">
                <div class="streak-number">{total_solved}</div>
                <div class="streak-label">Total Solved</div>
            </div>
            <div class="streak-card">
                <div class="streak-number">{pending}</div>
                <div class="streak-label">Pending Backlog</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Check-in Section
    st.subheader("📝 Daily Check-in")
    if uploaded_today:
        st.success("✅ Checked in for today!")
        public_url = find_saved_image(username, today_str)
        if public_url:
            st.image(public_url, caption=f"Proof submitted for {today_str}", use_container_width=True)
    else:
        questions_input = st.number_input("Questions solved today", min_value=0, max_value=200, value=DAILY_TARGET, step=1)
        uploaded_file = st.file_uploader("Upload proof image", type=["jpg", "jpeg", "png"], key=f"uploader_{st.session_state.uploader_counter}")

        if st.button("Submit Work", use_container_width=True):
            if uploaded_file is None:
                st.error("Please upload a photo before submitting.")
            else:
                file_bytes = uploaded_file.getvalue()
                file_ext = os.path.splitext(uploaded_file.name)[1]
                
                # Register upload logic locally & push to Supabase
                record["current_streak"] = record["current_streak"] + 1 if record["current_streak"] > 0 else 1
                record["last_upload_date"] = today_str
                record.setdefault("history", {})[today_str] = {"uploaded": True, "questions": int(questions_input)}
                record["highest_streak"] = max(record["highest_streak"], record["current_streak"])
                save_user(username, record)
                
                ext_clean = file_ext.lstrip(".").lower()
                content_type = "image/jpeg" if ext_clean in ("jpg", "jpeg") else f"image/{ext_clean}"
                storage_path = f"{username}/{today_str}{file_ext}"
                supabase.storage.from_(STORAGE_BUCKET).upload(
                    storage_path, file_bytes, {"content-type": content_type, "upsert": "true"}
                )
                
                st.session_state.uploader_counter += 1
                st.success("Submitted successfully!")
                st.rerun()

    # History Log Dropdown
    with st.expander("📅 View History Log"):
        history_data = record.get("history", {})
        if not history_data:
            st.info("No logs recorded yet.")
        else:
            hist_rows = [{"Date": d, "Status": "✅ Done" if info.get("uploaded") else "❌ Missed", "Questions": info.get("questions", 0)} for d, info in sorted(history_data.items(), reverse=True)]
            st.dataframe(pd.DataFrame(hist_rows), use_container_width=True, hide_index=True)
