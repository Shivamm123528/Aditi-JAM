import streamlit as st
import json
import os
from datetime import date, datetime, timedelta

# ---------- CONFIG ----------
DATA_FILE = "streak_data.json"

st.set_page_config(
    page_title="Study Streak Tracker",
    page_icon="🔥",
    layout="centered",
)

# ---------- MOBILE-FRIENDLY STYLING ----------
st.markdown(
    """
    <style>
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 500px;
    }
    .big-title {
        font-size: 2.2rem;
        font-weight: 800;
        text-align: center;
        margin-bottom: 0.2rem;
    }
    .subtitle {
        text-align: center;
        color: #888;
        margin-bottom: 1.5rem;
    }
    .streak-box {
        display: flex;
        justify-content: space-between;
        gap: 1rem;
        margin-bottom: 1.5rem;
    }
    .streak-card {
        flex: 1;
        background: #fff4e6;
        border-radius: 16px;
        padding: 1.2rem 0.5rem;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }
    .streak-card.high {
        background: #eaf7ea;
    }
    .streak-number {
        font-size: 2.5rem;
        font-weight: 800;
    }
    .streak-label {
        font-size: 0.9rem;
        color: #666;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------- DATA PERSISTENCE ----------
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
    else:
        data = {
            "current_streak": 0,
            "highest_streak": 0,
            "last_upload_date": None,  # ISO format string, e.g. "2026-07-25"
        }
        save_data(data)
    return data


def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)


def check_for_broken_streak(data):
    """If more than 1 full calendar day has passed since the last upload,
    the streak is broken and resets to 0. This runs every time the app loads,
    not just on upload, so the display is always accurate."""
    if data["last_upload_date"] is None:
        return data

    last_date = datetime.strptime(data["last_upload_date"], "%Y-%m-%d").date()
    today = date.today()
    gap_days = (today - last_date).days

    if gap_days > 1 and data["current_streak"] != 0:
        data["current_streak"] = 0
        save_data(data)

    return data


def register_upload(data):
    """Apply streak logic when a photo is uploaded."""
    today = date.today()
    today_str = today.isoformat()

    if data["last_upload_date"] is None:
        # first ever upload
        data["current_streak"] = 1
    else:
        last_date = datetime.strptime(data["last_upload_date"], "%Y-%m-%d").date()
        gap_days = (today - last_date).days

        if gap_days == 0:
            # already uploaded today, no double counting
            pass
        elif gap_days == 1:
            # consecutive day
            data["current_streak"] += 1
        else:
            # missed one or more days, streak restarts
            data["current_streak"] = 1

    data["last_upload_date"] = today_str
    data["highest_streak"] = max(data["highest_streak"], data["current_streak"])
    save_data(data)
    return data


# ---------- LOAD + CHECK DATA ----------
data = load_data()
data = check_for_broken_streak(data)

# ---------- HEADER ----------
st.markdown('<div class="big-title">🔥 Study Streak Tracker</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">Solve 50 questions a day. Upload proof. Keep the streak alive.</div>',
    unsafe_allow_html=True,
)

# ---------- STREAK DISPLAY ----------
st.markdown(
    f"""
    <div class="streak-box">
        <div class="streak-card">
            <div class="streak-number">{data['current_streak']}</div>
            <div class="streak-label">Current Streak</div>
        </div>
        <div class="streak-card high">
            <div class="streak-number">{data['highest_streak']}</div>
            <div class="streak-label">Highest Streak</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

if data["last_upload_date"]:
    st.caption(f"Last check-in: {data['last_upload_date']}")
else:
    st.caption("No check-ins yet. Upload your first photo to start your streak!")

st.divider()

# ---------- UPLOAD SECTION ----------
st.subheader("📸 Check in for today")
st.write("Upload a photo of your 50th solved question to register today's streak.")

uploaded_file = st.file_uploader(
    "Upload today's photo",
    type=["png", "jpg", "jpeg", "webp", "heic"],
    label_visibility="collapsed",
)

if uploaded_file is not None:
    # Register the upload using the streak logic
    already_checked_in_today = (
        data["last_upload_date"] == date.today().isoformat()
    )

    data = register_upload(data)

    if already_checked_in_today:
        st.info("✅ You've already checked in today — streak stays the same, but great job studying more!")
    else:
        st.success(f"🎉 Nice work! Streak updated to {data['current_streak']} day(s)!")
        st.balloons()

    st.image(uploaded_file, caption="Today's proof ✅", use_container_width=True)

    # Refresh the numbers shown after upload
    st.markdown(
        f"""
        <div class="streak-box">
            <div class="streak-card">
                <div class="streak-number">{data['current_streak']}</div>
                <div class="streak-label">Current Streak</div>
            </div>
            <div class="streak-card high">
                <div class="streak-number">{data['highest_streak']}</div>
                <div class="streak-label">Highest Streak</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.divider()
st.caption("Built with ❤️ to keep the streak alive. Missing a full calendar day resets your current streak to 0.")
