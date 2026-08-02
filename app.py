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


# ---------- HARRY POTTER CHARACTER DECK (40 characters) ----------
# NOTE ON IMAGES: real Harry Potter film stills/artwork are Warner Bros. /
# J.K. Rowling copyrighted material, so this app can't source, download, or
# embed actual movie images. Instead, each character gets a unique
# procedurally-generated illustrated avatar (via the free DiceBear API,
# seeded by the character's name) so every character still has a distinct
# picture. If you own licensed HP artwork, just swap the "image" URL for
# each entry below with your own hosted image link. The before/after
# messages are the exact text you supplied.
CHARACTERS = [
    {"name": "Harry Potter", "slug": "harry-potter", "image": "https://api.dicebear.com/7.x/adventurer/svg?seed=harry-potter&backgroundColor=3a1c71,6a3de8,241049", "before": "Expecto Patronum! Aditi, grab your wand and conquer those 40 questions before the Dementors of backlog catch up!", "after": "Brilliant work, Aditi! You faced the 40 questions head-on like a true Gryffindor!"},
    {"name": "Hermione Granger", "slug": "hermione-granger", "image": "https://api.dicebear.com/7.x/adventurer/svg?seed=hermione-granger&backgroundColor=3a1c71,6a3de8,241049", "before": "It's levi-o-sa, not levio-sa! Focus on your 40 math problems with absolute precision today, Aditi.", "after": "Five points to Gryffindor! Your 40 questions are solved flawlessly. Brilliant logic as always!"},
    {"name": "Ron Weasley", "slug": "ron-weasley", "image": "https://api.dicebear.com/7.x/adventurer/svg?seed=ron-weasley&backgroundColor=3a1c71,6a3de8,241049", "before": "Blimey, Aditi! 40 questions sound rough, but if anyone can beat this, it's definitely you!", "after": "Bloody brilliant, Aditi! You actually crushed all 40! Let's celebrate with some pumpkin juice!"},
    {"name": "Albus Dumbledore", "slug": "albus-dumbledore", "image": "https://api.dicebear.com/7.x/adventurer/svg?seed=albus-dumbledore&backgroundColor=3a1c71,6a3de8,241049", "before": "It is our choices, Aditi, that show what we truly are. It is time to choose to finish your 40 questions.", "after": "Magnificent work on your 40 today. Words are, in my not-so-humble opinion, our most inexhaustible source of magic."},
    {"name": "Severus Snape", "slug": "severus-snape", "image": "https://api.dicebear.com/7.x/adventurer/svg?seed=severus-snape&backgroundColor=3a1c71,6a3de8,241049", "before": "Subtlety of mind, Aditi... Do not slack off. I expect all 40 questions completed and properly analyzed.", "after": "Acceptable... Truly, exceptional discipline shown today. Your 40 questions are accounted for."},
    {"name": "Sirius Black", "slug": "sirius-black", "image": "https://api.dicebear.com/7.x/adventurer/svg?seed=sirius-black&backgroundColor=3a1c71,6a3de8,241049", "before": "The ones that love us never really leave us, Aditi. Push through your 40 questions with courage!", "after": "That’s my girl! You're breaking through barriers just like breaking out of Azkaban. Keep soaring!"},
    {"name": "Rubeus Hagrid", "slug": "rubeus-hagrid", "image": "https://api.dicebear.com/7.x/adventurer/svg?seed=rubeus-hagrid&backgroundColor=3a1c71,6a3de8,241049", "before": "Yer a math wizard, Aditi! Don't let those 40 questions scare yeh, yer stronger than a dragon!", "after": "Cracking good job, Aditi! Yer ready to face any magical beast that comes yer way!"},
    {"name": "Luna Lovegood", "slug": "luna-lovegood", "image": "https://api.dicebear.com/7.x/adventurer/svg?seed=luna-lovegood&backgroundColor=3a1c71,6a3de8,241049", "before": "Being different isn't a bad thing, Aditi. Focus on your 40 unique math questions in your own creative way.", "after": "I think the Nargles left your desk because your 40 questions are magically complete. How wonderful!"},
    {"name": "Draco Malfoy", "slug": "draco-malfoy", "image": "https://api.dicebear.com/7.x/adventurer/svg?seed=draco-malfoy&backgroundColor=3a1c71,6a3de8,241049", "before": "My father hears about everything, Aditi—including whether you finish your 40 questions today or not.", "after": "Hmph... I suppose even you can pull off 40 questions when properly motivated."},
    {"name": "Minerva McGonagall", "slug": "minerva-mcgonagall", "image": "https://api.dicebear.com/7.x/adventurer/svg?seed=minerva-mcgonagall&backgroundColor=3a1c71,6a3de8,241049", "before": "Transfiguration requires intense concentration, Aditi. Focus on your 40 questions without any distractions.", "after": "Impeccable execution! You have transformed raw effort into absolute mastery over your 40 questions."},
    {"name": "Neville Longbottom", "slug": "neville-longbottom", "image": "https://api.dicebear.com/7.x/adventurer/svg?seed=neville-longbottom&backgroundColor=3a1c71,6a3de8,241049", "before": "It takes a great deal of bravery to stand up to 40 hard math questions! You've got this.", "after": "Look what we can achieve when we don't give up! Your 40 questions look incredible, Aditi!"},
    {"name": "Bellatrix Lestrange", "slug": "bellatrix-lestrange", "image": "https://api.dicebear.com/7.x/adventurer/svg?seed=bellatrix-lestrange&backgroundColor=3a1c71,6a3de8,241049", "before": "Let's see how much pain those 40 math equations can give you before you conquer them, Aditi!", "after": "A dark power rises! You tortured those 40 questions until they gave you the right answers!"},
    {"name": "Remus Lupin", "slug": "remus-lupin", "image": "https://api.dicebear.com/7.x/adventurer/svg?seed=remus-lupin&backgroundColor=3a1c71,6a3de8,241049", "before": "Eat a bit of chocolate and tackle your 40 questions, Aditi. You have the strength for this.", "after": "Wonderful control, Aditi. You faced your inner doubts and mastered all 40 questions brilliantly."},
    {"name": "Cedric Diggory", "slug": "cedric-diggory", "image": "https://api.dicebear.com/7.x/adventurer/svg?seed=cedric-diggory&backgroundColor=3a1c71,6a3de8,241049", "before": "Remember, champions stick together. Take it one step at a time through your 40 questions today.", "after": "You touched the cup of productivity today, Aditi! Exceptional work on your 40 questions."},
    {"name": "Ginny Weasley", "slug": "ginny-weasley", "image": "https://api.dicebear.com/7.x/adventurer/svg?seed=ginny-weasley&backgroundColor=3a1c71,6a3de8,241049", "before": "Show them what you're made of, Aditi! Blast through those 40 questions like a Bat-Bogey Hex!", "after": "Absolute winner energy! You cleared all 40 questions without breaking a sweat."},
    {"name": "Fred Weasley", "slug": "fred-weasley", "image": "https://api.dicebear.com/7.x/adventurer/svg?seed=fred-weasley&backgroundColor=3a1c71,6a3de8,241049", "before": "Weasley's Wizard Wheezes recommends knocking out those 40 questions with a bang, Aditi!", "after": "Merlin's pants, you actually did all 40! Time to open a Skiving Snackbox to celebrate!"},
    {"name": "George Weasley", "slug": "george-weasley", "image": "https://api.dicebear.com/7.x/adventurer/svg?seed=george-weasley&backgroundColor=3a1c71,6a3de8,241049", "before": "Don't let the math grind you down! Prank those 40 questions by solving them perfectly!", "after": "Mischief managed! 40 questions down, and you made it look entirely too easy!"},
    {"name": "Cho Chang", "slug": "cho-chang", "image": "https://api.dicebear.com/7.x/adventurer/svg?seed=cho-chang&backgroundColor=3a1c71,6a3de8,241049", "before": "Keep your hand steady on your quill, Aditi. 40 questions require deep focus and calm breathing.", "after": "Your study session was flawless! All 40 questions completed with absolute grace."},
    {"name": "Nymphadora Tonks", "slug": "nymphadora-tonks", "image": "https://api.dicebear.com/7.x/adventurer/svg?seed=nymphadora-tonks&backgroundColor=3a1c71,6a3de8,241049", "before": "Wotcher, Aditi! Don't trip over your robes—just jump straight into your 40 daily questions!", "after": "Brilliant! You shifted shapes and conquered those 40 questions like a true Auror in training!"},
    {"name": "Viktor Krum", "slug": "viktor-krum", "image": "https://api.dicebear.com/7.x/adventurer/svg?seed=viktor-krum&backgroundColor=3a1c71,6a3de8,241049", "before": "I vatch you train, Aditi. Focus your eyes on the math snitch and catch those 40 questions.", "after": "Venn-tastic! You caught the snitch of victory. All 40 questions successfully captured."},
    {"name": "Fleur Delacour", "slug": "fleur-delacour", "image": "https://api.dicebear.com/7.x/adventurer/svg?seed=fleur-delacour&backgroundColor=3a1c71,6a3de8,241049", "before": "Eet is magnifique to see you study hard, Aditi. Now show those 40 questions your true power.", "after": "Ooh, c'est magnifique! Your 40 questions are completed with pure magical perfection."},
    {"name": "Arthur Weasley", "slug": "arthur-weasley", "image": "https://api.dicebear.com/7.x/adventurer/svg?seed=arthur-weasley&backgroundColor=3a1c71,6a3de8,241049", "before": "Fascinating! I wonder how Muggles do math, but your 40 questions are much more urgent!", "after": "Magnificent wizarding engineering, Aditi! You've successfully wired your brain for 40 questions today."},
    {"name": "Molly Weasley", "slug": "molly-weasley", "image": "https://api.dicebear.com/7.x/adventurer/svg?seed=molly-weasley&backgroundColor=3a1c71,6a3de8,241049", "before": "Sit down right away and finish your 40 questions like a good witch!", "after": "Oh, my sweet girl, you finished all 40! I am so incredibly proud of you!"},
    {"name": "Lucius Malfoy", "slug": "lucius-malfoy", "image": "https://api.dicebear.com/7.x/adventurer/svg?seed=lucius-malfoy&backgroundColor=3a1c71,6a3de8,241049", "before": "Quality work is expected from those who possess true ambition, Aditi. Show me your 40 questions.", "after": "Impressive performance. You command your mathematical spells with cold, calculated precision."},
    {"name": "Kingsley Shacklebolt", "slug": "kingsley-shacklebolt", "image": "https://api.dicebear.com/7.x/adventurer/svg?seed=kingsley-shacklebolt&backgroundColor=3a1c71,6a3de8,241049", "before": "Stay vigilant, Aditi. The path to greatness requires unyielding focus on your 40 daily questions.", "after": "Ministry standards have been met and exceeded. Outstanding job completing your 40 questions."},
    {"name": "Professor Flitwick", "slug": "professor-flitwick", "image": "https://api.dicebear.com/7.x/adventurer/svg?seed=professor-flitwick&backgroundColor=3a1c71,6a3de8,241049", "before": "Swish and flick, Aditi! Bring maximum energy and intellect to your 40 Charm-level math problems.", "after": "Wingardium Leviosa! Your knowledge and confidence are soaring high after finishing those 40 questions!"},
    {"name": "Mad-Eye Moody", "slug": "mad-eye-moody", "image": "https://api.dicebear.com/7.x/adventurer/svg?seed=mad-eye-moody&backgroundColor=3a1c71,6a3de8,241049", "before": "CONSTANT VIGILANCE, Aditi! Don't let laziness sneak up on your 40 questions today!", "after": "That's how it's done! Secured the perimeter, locked down the answers, 40 questions defeated!"},
    {"name": "Sybill Trelawney", "slug": "sybill-trelawney", "image": "https://api.dicebear.com/7.x/adventurer/svg?seed=sybill-trelawney&backgroundColor=3a1c71,6a3de8,241049", "before": "My inner eye sees great mathematical triumph in your future, Aditi, provided you solve your 40 questions.", "after": "The tea leaves never lie! Your 40 questions are done, foretelling a glorious future!"},
    {"name": "Professor Sprout", "slug": "professor-sprout", "image": "https://api.dicebear.com/7.x/adventurer/svg?seed=professor-sprout&backgroundColor=3a1c71,6a3de8,241049", "before": "Put on your earmuffs, Aditi, and dig deep into the greenhouse of logic for your 40 questions.", "after": "Look at those brilliant roots and shoots! Your 40 questions have blossomed into success."},
    {"name": "Horace Slughorn", "slug": "horace-slughorn", "image": "https://api.dicebear.com/7.x/adventurer/svg?seed=horace-slughorn&backgroundColor=3a1c71,6a3de8,241049", "before": "Ah, brilliant minds collect top grades! Let's see you tackle those 40 questions.", "after": "A top-tier performance, Aditi! You truly belong in the elite club of problem solvers."},
    {"name": "Dobby", "slug": "dobby", "image": "https://api.dicebear.com/7.x/adventurer/svg?seed=dobby&backgroundColor=3a1c71,6a3de8,241049", "before": "Dobby is happy to serve! Aditi is a great witch who will surely finish her 40 questions today!", "after": "Dobby is a free elf, and Aditi is free from her 40-question backlog! Hip hip hooray!"},
    {"name": "Garrick Ollivander", "slug": "garrick-ollivander", "image": "https://api.dicebear.com/7.x/adventurer/svg?seed=garrick-ollivander&backgroundColor=3a1c71,6a3de8,241049", "before": "The wand chooses the wizard, Aditi, but the wizard must choose to solve her 40 questions.", "after": "I remember every equation you've ever solved... and these 40 were truly exceptional."},
    {"name": "Dean Thomas", "slug": "dean-thomas", "image": "https://api.dicebear.com/7.x/adventurer/svg?seed=dean-thomas&backgroundColor=3a1c71,6a3de8,241049", "before": "Sketch out your equations clearly like a masterpiece canvas, Aditi. 40 questions await!", "after": "Absolute masterpiece! Your 40 questions are fully solved and beautifully presented."},
    {"name": "Seamus Finnigan", "slug": "seamus-finnigan", "image": "https://api.dicebear.com/7.x/adventurer/svg?seed=seamus-finnigan&backgroundColor=3a1c71,6a3de8,241049", "before": "Try not to accidentally blow up your study desk while doing your 40 questions!", "after": "Brilliant! No smoke or explosions, just 40 cleanly solved questions!"},
    {"name": "Parvati Patil", "slug": "parvati-patil", "image": "https://api.dicebear.com/7.x/adventurer/svg?seed=parvati-patil&backgroundColor=3a1c71,6a3de8,241049", "before": "Trust your intuition and your textbooks, Aditi. You can breeze right through those 40 questions.", "after": "You did it! Your study session was magical and your 40 questions are completely finished."},
    {"name": "Padma Patil", "slug": "padma-patil", "image": "https://api.dicebear.com/7.x/adventurer/svg?seed=padma-patil&backgroundColor=3a1c71,6a3de8,241049", "before": "Ravenclaw wisdom dictates methodical, structured progress through your 40 daily questions, Aditi.", "after": "Flawless logic and immaculate calculation! All 40 questions solved to absolute perfection."},
    {"name": "Oliver Wood", "slug": "oliver-wood", "image": "https://api.dicebear.com/7.x/adventurer/svg?seed=oliver-wood&backgroundColor=3a1c71,6a3de8,241049", "before": "Studying is about discipline! Let's win the 40-question match today!", "after": "That's how you catch the winning goal! 40 questions locked in and secured!"},
    {"name": "Lee Jordan", "slug": "lee-jordan", "image": "https://api.dicebear.com/7.x/adventurer/svg?seed=lee-jordan&backgroundColor=3a1c71,6a3de8,241049", "before": "And they're off! Aditi stepping up to the plate to face the almighty 40-question challenge!", "after": "What a stunning victory! Aditi scores all 40 points like an absolute champion!"},
    {"name": "Katie Bell", "slug": "katie-bell", "image": "https://api.dicebear.com/7.x/adventurer/svg?seed=katie-bell&backgroundColor=3a1c71,6a3de8,241049", "before": "Stay strong and keep your momentum going, Aditi. 40 questions are a breeze for you!", "after": "You nailed every single one of them! Fantastic effort on your 40 questions today."},
    {"name": "Angelina Johnson", "slug": "angelina-johnson", "image": "https://api.dicebear.com/7.x/adventurer/svg?seed=angelina-johnson&backgroundColor=3a1c71,6a3de8,241049", "before": "Total concentration, Aditi. No distractions until those 40 questions are completely done.", "after": "Hard work pays off! Your 40 questions are done and your streak keeps burning bright."},
]


def get_daily_character(today):
    """Cycles through one of the 40 characters per calendar day."""
    return CHARACTERS[today.toordinal() % len(CHARACTERS)]


# ---------- OPTIONAL: YOUR OWN RIGHTS-CLEARED CHARACTER PHOTOS ----------
# I can't source or embed real Harry Potter movie stills myself (Warner Bros.
# / J.K. Rowling copyright). But if YOU have photos you're licensed to use,
# upload them to a Supabase Storage bucket named "character-photos", with
# each filename matching a character's slug below (e.g. "harry-potter.jpg",
# "hermione-granger.png"). The app will automatically use your real photo
# instead of the generated placeholder avatar whenever one is found.
STORAGE_BUCKET_CHARACTER_PHOTOS = "character-photos"


@st.cache_data(ttl=300)
def list_character_photo_files():
    try:
        return supabase.storage.from_(STORAGE_BUCKET_CHARACTER_PHOTOS).list()
    except Exception:
        return []


def get_character_image_url(character):
    """Returns your uploaded rights-cleared photo for this character if one
    exists in Supabase Storage, otherwise falls back to the generated
    placeholder avatar."""
    files = list_character_photo_files()
    for f in files:
        base = f["name"].rsplit(".", 1)[0].lower()
        if base == character["slug"]:
            return supabase.storage.from_(STORAGE_BUCKET_CHARACTER_PHOTOS).get_public_url(f["name"])
    return character["image"]


def character_card(character, uploaded_today):
    msg = character["after"] if uploaded_today else character["before"]
    label = "✅ Today's check-in" if uploaded_today else "⏳ Awaiting today's check-in"
    image_url = get_character_image_url(character)
    return f"""
    <div style="background: rgba(20,10,45,0.5); border: 1px solid rgba(212,175,55,0.4);
                border-radius: 18px; padding: 1rem 1.1rem; margin-bottom: 0.6rem;
                box-shadow: 0 4px 14px rgba(0,0,0,0.35); text-align:center;">
        <img class="hp-character-img" src="{image_url}"
             style="width:110px;height:110px;border-radius:50%;border:3px solid #d4af37;
                    background:#241049;box-shadow:0 4px 14px rgba(0,0,0,0.4);object-fit:cover;" />
        <div style="font-weight:800; color:#ffe066 !important; margin-top:0.5rem; font-size:1.05rem;">
            {character['name']}
        </div>
        <div style="font-size:0.75rem; color:#cbb98f !important; margin-bottom:0.4rem;">{label}</div>
        <div style="font-weight:600; color:#f5e6c8 !important; font-size:0.96rem; line-height:1.4;">
            {msg}
        </div>
    </div>
    """


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


# ---------- OPTIONAL: YOUR OWN RIGHTS-CLEARED BACKGROUND IMAGE ----------
# Same deal as the character photos: I can't source a real Harry Potter
# background (Warner Bros. copyright), but if you upload an image you're
# licensed to use to a Supabase Storage bucket named "app-background"
# (any filename starting with "background", e.g. "background.jpg"), the
# app will use it as the page background instead of the default gradient.
STORAGE_BUCKET_BACKGROUND = "app-background"


@st.cache_data(ttl=300)
def get_background_image_url():
    try:
        files = supabase.storage.from_(STORAGE_BUCKET_BACKGROUND).list()
    except Exception:
        return None
    for f in files:
        if f["name"].lower().startswith("background"):
            return supabase.storage.from_(STORAGE_BUCKET_BACKGROUND).get_public_url(f["name"])
    return None


# ---------- OPTIONAL: YOUR OWN RIGHTS-CLEARED BACKGROUND MUSIC ----------
# I also can't provide the actual film score (John Williams / Warner Bros.
# copyright). Upload a track you're licensed to use to a Supabase Storage
# bucket named "app-audio" (any filename starting with "theme", e.g.
# "theme.mp3") and a play/pause control will appear automatically.
STORAGE_BUCKET_AUDIO = "app-audio"


@st.cache_data(ttl=300)
def get_background_audio_url():
    try:
        files = supabase.storage.from_(STORAGE_BUCKET_AUDIO).list()
    except Exception:
        return None
    for f in files:
        if f["name"].lower().startswith("theme"):
            return supabase.storage.from_(STORAGE_BUCKET_AUDIO).get_public_url(f["name"])
    return None


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

# If the user has uploaded their own rights-cleared background image,
# layer it on top of the default gradient theme.
_bg_image_url = get_background_image_url()
if _bg_image_url:
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url('{_bg_image_url}') !important;
            background-size: cover !important;
            background-position: center !important;
            background-attachment: fixed !important;
        }}
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
            "unlocked_spells": row.get("unlocked_spells") or [],
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
        "unlocked_spells": record.get("unlocked_spells", []),
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
        "unlocked_spells": [],
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


# ---------- 50 UNLOCKABLE SPELLS ----------
SPELLS = [
    {"name": "Lumos", "desc": "Changes app background to a bright white \"light mode\" for 10 seconds.", "cost": 2, "effect": {"type": "bg_toggle", "params": {"color": "#f5f0e0", "text": "#20140a", "duration": 10000}}},
    {"name": "Nox", "desc": "Changes app background to an ultra-dark AMOLED black mode.", "cost": 2, "effect": {"type": "bg_toggle", "params": {"color": "#000000", "text": "#00ff88", "duration": 10000}}},
    {"name": "Wingardium Leviosa", "desc": "Makes all text on the screen gently float up and down.", "cost": 4, "effect": {"type": "float_text", "params": {"duration": 6000}}},
    {"name": "Accio", "desc": "Pulls the daily submit button all the way to the top of the screen.", "cost": 4, "effect": {"type": "scroll", "params": {"to": "top", "duration": 1200}}},
    {"name": "Alohomora", "desc": "Unlocks a secret hidden motivational quote from Shivam.", "cost": 5, "effect": {"type": "text_overlay", "params": {"text": "\ud83d\udd13 Hidden Note: \"Believe in the version of you that hasn't given up.\" \u2014 Shivam", "color": "#ffe066", "duration": 5000}}},
    {"name": "Reparo", "desc": "Fixes the UI after another spell breaks it.", "cost": 3, "effect": {"type": "reset", "params": {"toast": "\ud83e\ude84 Reparo! Any lingering visual curses have been repaired.", "duration": 500}}},
    {"name": "Expelliarmus", "desc": "Disarms the submit button (makes it jump away from the mouse) for 5 seconds.", "cost": 6, "effect": {"type": "buttons_fx", "params": {"variant": "shy", "duration": 5000}}},
    {"name": "Stupefy", "desc": "Freezes the screen in place with a red flash for 3 seconds.", "cost": 5, "effect": {"type": "freeze", "params": {"color": "#ff3b3b", "duration": 3000}}},
    {"name": "Protego", "desc": "Wraps the entire app in a glowing blue shield border.", "cost": 8, "effect": {"type": "border", "params": {"color": "#4da6ff", "duration": 8000}}},
    {"name": "Expecto Patronum", "desc": "Triggers an animated silver stag that runs across the screen.", "cost": 15, "effect": {"type": "run", "params": {"emoji": "\ud83e\udd8c", "duration": 4200}}},
    {"name": "Aguamenti", "desc": "Rains blue water drop emojis down the screen.", "cost": 5, "effect": {"type": "rain", "params": {"emoji": "\ud83d\udca7", "count": 28, "duration": 4000}}},
    {"name": "Incendio", "desc": "Triggers a harmless fire animation around the daily streak counter.", "cost": 10, "effect": {"type": "rain", "params": {"emoji": "\ud83d\udd25", "count": 18, "duration": 3200}}},
    {"name": "Obliviate", "desc": "Temporarily blurs all the text on the screen for 5 seconds.", "cost": 8, "effect": {"type": "blur", "params": {"duration": 5000}}},
    {"name": "Riddikulus", "desc": "Turns the streak counter into a clown nose emoji temporarily.", "cost": 5, "effect": {"type": "text_overlay", "params": {"text": "\ud83e\udd21 Streak counter Riddikulus'd into a clown nose!", "color": "#ff8ad1", "duration": 3000}}},
    {"name": "Sectumsempra", "desc": "Slashes the screen with harmless digital scratch marks.", "cost": 12, "effect": {"type": "scratch", "params": {"duration": 2500}}},
    {"name": "Crucio", "desc": "Shakes the entire app violently (screen tremble effect) for 3 seconds.", "cost": 15, "effect": {"type": "shake", "params": {"duration": 3000, "intensity": "high"}}},
    {"name": "Imperio", "desc": "Forces the app to automatically check the \"show history\" box.", "cost": 10, "effect": {"type": "python_flag", "params": {"flag": "force_history_open", "duration": 0}}},
    {"name": "Avada Kedavra", "desc": "Turns the screen completely black with a green flash for 2 seconds.", "cost": 20, "effect": {"type": "avada", "params": {"duration": 2000}}},
    {"name": "Confundo", "desc": "Reverses the text direction (RTL) for 5 seconds.", "cost": 8, "effect": {"type": "rtl", "params": {"duration": 5000}}},
    {"name": "Silencio", "desc": "Mutes the background Harry Potter theme music.", "cost": 5, "effect": {"type": "audio_volume", "params": {"volume": 0, "duration": 5000}}},
    {"name": "Sonorus", "desc": "Increases the volume of the background music to maximum for 5 seconds.", "cost": 6, "effect": {"type": "audio_volume", "params": {"volume": 1, "duration": 5000}}},
    {"name": "Muffliato", "desc": "Adds a buzzing static sound over the music for 5 seconds.", "cost": 5, "effect": {"type": "audio_wobble", "params": {"duration": 5000}}},
    {"name": "Engorgio", "desc": "Enlarges the daily character image to take up the whole screen.", "cost": 8, "effect": {"type": "img_scale", "params": {"selector": ".hp-character-img", "scale": 2.6, "duration": 4000}}},
    {"name": "Reducio", "desc": "Shrinks the entire app UI down to 50% size for 5 seconds.", "cost": 8, "effect": {"type": "scale", "params": {"scale": 0.55, "duration": 5000}}},
    {"name": "Tarantallegra", "desc": "Makes the submit button dance left and right rapidly.", "cost": 6, "effect": {"type": "buttons_fx", "params": {"variant": "dance", "duration": 5000}}},
    {"name": "Petrificus Totalus", "desc": "Disables scrolling completely for 5 seconds.", "cost": 10, "effect": {"type": "no_scroll", "params": {"duration": 5000}}},
    {"name": "Levicorpus", "desc": "Flips the entire app upside down for 5 seconds.", "cost": 15, "effect": {"type": "transform", "params": {"transform": "rotate(180deg)", "duration": 5000}}},
    {"name": "Liberacorpus", "desc": "Flips the app right-side up (counters Levicorpus).", "cost": 2, "effect": {"type": "reset_transform", "params": {"duration": 300}}},
    {"name": "Episkey", "desc": "Heals a broken streak visually (shows a fake +1 streak for a few seconds).", "cost": 12, "effect": {"type": "bump_number", "params": {"selector": ".streak-card .streak-number", "amount": 1, "duration": 3000}}},
    {"name": "Evanesco", "desc": "Makes the daily quote vanish completely.", "cost": 4, "effect": {"type": "hide", "params": {"selector": ".quote-card", "duration": 4000}}},
    {"name": "Incarcerous", "desc": "Wraps the UI in digital ropes that must be clicked to break.", "cost": 10, "effect": {"type": "ropes", "params": {"duration": 4500}}},
    {"name": "Glisseo", "desc": "Turns the scrollbar into a frictionless slide (forces scroll to bottom).", "cost": 6, "effect": {"type": "scroll", "params": {"to": "bottom", "duration": 1200}}},
    {"name": "Descendo", "desc": "Slams all elements on the page to the bottom of the screen.", "cost": 8, "effect": {"type": "transform", "params": {"transform": "translateY(160px)", "duration": 3000}}},
    {"name": "Ascendio", "desc": "Shoots the page view instantly to the top header.", "cost": 4, "effect": {"type": "scroll", "params": {"to": "top", "duration": 1200}}},
    {"name": "Avis", "desc": "Spawns little bird emojis that fly across the screen.", "cost": 6, "effect": {"type": "rain", "params": {"emoji": "\ud83d\udc26", "count": 22, "duration": 4000}}},
    {"name": "Oppugno", "desc": "Makes the bird emojis (from Avis) dive-bomb the mouse cursor.", "cost": 10, "effect": {"type": "rain", "params": {"emoji": "\ud83d\udc26", "count": 45, "duration": 1800}}},
    {"name": "Lumos Maxima", "desc": "Blinds the screen with intense white light for 3 seconds.", "cost": 8, "effect": {"type": "flash", "params": {"color": "#ffffff", "duration": 3000}}},
    {"name": "Aresto Momentum", "desc": "Slows down all CSS animations in the app to 10% speed.", "cost": 5, "effect": {"type": "slowmo", "params": {"duration": 8000}}},
    {"name": "Homenum Revelio", "desc": "Shows a popup saying \"Shivam is watching your progress.\"", "cost": 5, "effect": {"type": "toast", "params": {"text": "\ud83d\udc41\ufe0f Homenum Revelio! Shivam is watching your progress.", "icon": "\ud83d\udc41\ufe0f"}}},
    {"name": "Prior Incantato", "desc": "Replays the visual effect of the last spell cast.", "cost": 4, "effect": {"type": "replay", "params": {}}},
    {"name": "Deletrius", "desc": "Clears all current visual prank effects instantly.", "cost": 2, "effect": {"type": "reset", "params": {"toast": "\ud83e\uddf9 Deletrius! All active visual effects cleared.", "duration": 500}}},
    {"name": "Diffindo", "desc": "Visually \"cuts\" the screen layout in half with a CSS gap.", "cost": 10, "effect": {"type": "cut", "params": {"duration": 2500}}},
    {"name": "Geminio", "desc": "Duplicates the daily character image 10 times across the screen.", "cost": 12, "effect": {"type": "duplicate", "params": {"count": 10, "duration": 4000}}},
    {"name": "Morsmordre", "desc": "Projects a green Dark Mark image faintly in the background.", "cost": 15, "effect": {"type": "dark_mark", "params": {"duration": 4500}}},
    {"name": "Relashio", "desc": "Makes all buttons on the page repel the mouse cursor slightly.", "cost": 8, "effect": {"type": "buttons_fx", "params": {"variant": "shy", "duration": 6000}}},
    {"name": "Scourgify", "desc": "\"Wipes\" the screen clean with a soapy bubble animation.", "cost": 6, "effect": {"type": "scourgify", "params": {"duration": 3500}}},
    {"name": "Specialis Revelio", "desc": "Reveals the exact number of math questions solved since day 1 in a gold font.", "cost": 5, "effect": {"type": "reveal_total", "params": {"duration": 4000}}},
    {"name": "Densaugeo", "desc": "Makes the font size of the streak counter grow massive.", "cost": 6, "effect": {"type": "grow_number", "params": {"selector": ".streak-card .streak-number", "scale": 2.8, "duration": 4000}}},
    {"name": "Colovaria", "desc": "Randomizes the accent colors of the entire Streamlit app.", "cost": 10, "effect": {"type": "hue", "params": {"duration": 4000}}},
    {"name": "Felix Felicis", "desc": "Rains liquid gold/sparkles on the screen, temporarily changing your title to \"The Luckiest Wizard.\"", "cost": 30, "effect": {"type": "felix", "params": {"duration": 5000}}},
]

# ---------- MAGIC POINTS (MP) ECONOMY ----------
MP_PER_QUESTIONS = 20  # 20 solved questions = 1 MP


def compute_mp(total_solved, unlocked_spells):
    """MP is earned permanently at 1 per 20 questions solved (lifetime total).
    Once a spell is unlocked its cost is paid once; unlocked spells are then
    free to cast forever. Returns (earned, spent, balance)."""
    earned = total_solved // MP_PER_QUESTIONS
    spent = sum(s["cost"] for s in SPELLS if s["name"] in unlocked_spells)
    balance = max(0, earned - spent)
    return earned, spent, balance


def unlock_spell(users, username, spell_name):
    record = users[username]
    unlocked = record.setdefault("unlocked_spells", [])
    if spell_name not in unlocked:
        unlocked.append(spell_name)
        save_user(username, record)
    return users


# ---------- SPELL VISUAL EFFECT ENGINE ----------
def cast_effect(effect, dynamic=None):
    """Renders a temporary JS/CSS-driven visual effect into the parent app
    document (Streamlit components run in a sandboxed iframe, so effects
    that need to touch the outer page reach up via window.parent.document).
    Native Streamlit effects (balloons/snow/toast) are called directly."""
    etype = effect.get("type")
    p = dict(effect.get("params", {}))
    if dynamic:
        p.update(dynamic)
    duration = p.get("duration", 3000)
    uid = f"fx_{random.randint(100000, 999999)}"
    js = ""

    if etype == "toast":
        st.toast(p.get("text", "✨"), icon=p.get("icon", "✨"))
        return

    if etype == "python_flag":
        st.session_state[p["flag"]] = True
        st.toast("🪄 Imperio! The history log has been forced open.", icon="🪄")
        return

    if etype == "reveal_total":
        total = p.get("total_solved", 0)
        js = f"""
        var d=document.createElement('div');
        d.id='{uid}';
        d.innerHTML="🔍 <b>Specialis Revelio</b><br><span style='font-size:2rem;color:#ffe066;'>{total}</span><br>questions solved since day 1";
        d.style.cssText='position:fixed;top:50%;left:50%;transform:translate(-50%,-50%);z-index:999999;pointer-events:none;background:rgba(10,5,20,0.9);color:#ffe066;text-align:center;padding:1.2rem 1.6rem;border-radius:16px;border:2px solid #d4af37;font-weight:700;';
        window.parent.document.body.appendChild(d);
        setTimeout(function(){{d.remove();}}, {duration});
        """
        components.html(f"<script>{js}</script>", height=0, width=0)
        return

    if etype == "replay":
        last = st.session_state.get("last_spell_effect")
        if last:
            cast_effect(last)
        else:
            st.toast("✨ Prior Incantato... but no spell has been cast yet!", icon="✨")
        return

    if etype == "reset":
        js = f"""
        var pd = window.parent.document;
        pd.querySelectorAll('[id^="fx_"]').forEach(function(el){{ el.remove(); }});
        var bc = pd.querySelector('.main .block-container');
        if(bc){{ bc.style.transform=''; bc.style.filter=''; bc.style.direction=''; }}
        var app = pd.querySelector('.stApp');
        if(app){{ app.style.boxShadow=''; app.style.filter=''; app.style.background=''; app.style.color=''; }}
        pd.documentElement.style.overflow=''; pd.body.style.overflow='';
        """
        components.html(f"<script>{js}</script>", height=0, width=0)
        if p.get("toast"):
            st.toast(p["toast"], icon="🧹")
        return

    if etype == "reset_transform":
        js = """
        var bc = window.parent.document.querySelector('.main .block-container');
        if(bc){ bc.style.transition='transform 0.4s'; bc.style.transform=''; }
        """
        components.html(f"<script>{js}</script>", height=0, width=0)
        return

    if etype == "audio_volume":
        volume = p.get("volume", 1)
        js = f"""
        var a = window.parent.document.getElementById('hp-bg-audio');
        if(a){{
          var prevVol = a.volume;
          a.volume = {volume};
          setTimeout(function(){{ a.volume = prevVol; }}, {duration});
        }}
        """
        components.html(f"<script>{js}</script>", height=0, width=0)
        st.session_state["last_spell_effect"] = effect
        return

    if etype == "audio_wobble":
        js = f"""
        var a = window.parent.document.getElementById('hp-bg-audio');
        if(a){{
          var prevVol = a.volume;
          var n = 0;
          var iv = setInterval(function(){{
            a.volume = Math.random() * 0.8 + 0.1;
            n++;
            if(n > {max(1, duration // 150)}){{ clearInterval(iv); a.volume = prevVol; }}
          }}, 150);
        }}
        """
        components.html(f"<script>{js}</script>", height=0, width=0)
        st.session_state["last_spell_effect"] = effect
        return

    if etype == "flash":
        color = p.get("color", "#ffffff")
        js = f"""
        var d=document.createElement('div'); d.id='{uid}';
        d.style.cssText='position:fixed;inset:0;background:{color};opacity:0.9;z-index:999999;pointer-events:none;transition:opacity 0.6s;';
        window.parent.document.body.appendChild(d);
        setTimeout(function(){{d.style.opacity='0';}}, {max(0, duration-500)});
        setTimeout(function(){{d.remove();}}, {duration});
        """
    elif etype == "avada":
        js = f"""
        var d=document.createElement('div'); d.id='{uid}';
        d.style.cssText='position:fixed;inset:0;background:#000;opacity:0;z-index:999999;pointer-events:none;transition:opacity 0.3s,background 0.3s;';
        window.parent.document.body.appendChild(d);
        setTimeout(function(){{d.style.opacity='1';}}, 30);
        setTimeout(function(){{d.style.background='#00ff66'; d.style.opacity='0.85';}}, 700);
        setTimeout(function(){{d.style.opacity='0';}}, 1500);
        setTimeout(function(){{d.remove();}}, {duration});
        """
    elif etype == "bg_toggle":
        color = p.get("color", "#ffffff")
        text = p.get("text", "#000000")
        js = f"""
        var app = window.parent.document.querySelector('.stApp');
        if(app){{
          var prevBg = app.style.background; var prevColor = app.style.color;
          app.style.transition='background 0.5s, color 0.5s';
          app.style.background='{color}'; app.style.color='{text}';
          setTimeout(function(){{ app.style.background=prevBg; app.style.color=prevColor; }}, {duration});
        }}
        """
    elif etype == "shake":
        js = f"""
        var el = window.parent.document.querySelector('.main .block-container');
        if(el){{
          var n=0; var iv=setInterval(function(){{
            var x=(Math.random()-0.5)*18;
            el.style.transform='translateX('+x+'px)';
            n++;
            if(n>{max(1, duration // 45)}){{clearInterval(iv); el.style.transform='';}}
          }}, 45);
        }}
        """
    elif etype == "rain":
        emoji = p.get("emoji", "✨")
        count = p.get("count", 25)
        js = f"""
        var container = document.createElement('div'); container.id='{uid}';
        container.style.cssText='position:fixed;inset:0;pointer-events:none;z-index:999999;overflow:hidden;';
        window.parent.document.body.appendChild(container);
        var style = document.createElement('style'); style.id='{uid}_s';
        style.textContent='@keyframes fxfall {{ from {{transform:translateY(-10vh);}} to {{transform:translateY(110vh);}} }}';
        window.parent.document.head.appendChild(style);
        for(var i=0;i<{count};i++){{
          var s = document.createElement('div');
          s.textContent = '{emoji}';
          s.style.cssText='position:absolute;top:0;left:'+(Math.random()*100)+'%;font-size:'+(16+Math.random()*16)+'px;animation:fxfall '+(1.6+Math.random()*1.8)+'s linear forwards;animation-delay:'+(Math.random()*1.2)+'s;';
          container.appendChild(s);
        }}
        setTimeout(function(){{container.remove(); style.remove();}}, {duration});
        """
    elif etype == "run":
        emoji = p.get("emoji", "🦌")
        js = f"""
        var s = document.createElement('div'); s.id='{uid}';
        s.textContent='{emoji}';
        s.style.cssText='position:fixed;top:38%;left:-12%;font-size:64px;z-index:999999;pointer-events:none;filter:drop-shadow(0 0 12px #cfe8ff);';
        window.parent.document.body.appendChild(s);
        var style = document.createElement('style'); style.id='{uid}_s';
        style.textContent='@keyframes fxrun {{ from {{left:-12%;}} to {{left:112%;}} }}';
        window.parent.document.head.appendChild(style);
        s.style.animation='fxrun {duration}ms ease-in-out forwards';
        setTimeout(function(){{s.remove(); style.remove();}}, {duration});
        """
    elif etype == "transform":
        transform = p.get("transform", "none")
        js = f"""
        var el = window.parent.document.querySelector('.main .block-container');
        if(el){{
          el.style.transition='transform 0.6s';
          el.style.transform='{transform}';
          setTimeout(function(){{ el.style.transform=''; }}, {duration});
        }}
        """
    elif etype == "scale":
        scale = p.get("scale", 0.5)
        js = f"""
        var el = window.parent.document.querySelector('.main .block-container');
        if(el){{
          el.style.transition='transform 0.4s'; el.style.transformOrigin='top center';
          el.style.transform='scale({scale})';
          setTimeout(function(){{ el.style.transform=''; }}, {duration});
        }}
        """
    elif etype == "border":
        color = p.get("color", "#4da6ff")
        js = f"""
        var el = window.parent.document.querySelector('.stApp');
        if(el){{
          el.style.transition='box-shadow 0.4s';
          el.style.boxShadow='inset 0 0 0 6px {color}, 0 0 40px 10px {color}';
          setTimeout(function(){{ el.style.boxShadow=''; }}, {duration});
        }}
        """
    elif etype == "text_overlay":
        text = p.get("text", "").replace('"', '\\"')
        color = p.get("color", "#ffe066")
        js = f"""
        var d=document.createElement('div'); d.id='{uid}';
        d.textContent="{text}";
        d.style.cssText='position:fixed;top:50%;left:50%;transform:translate(-50%,-50%);font-size:1.3rem;font-weight:800;color:{color};z-index:999999;pointer-events:none;background:rgba(10,5,20,0.9);padding:1rem 1.4rem;border-radius:16px;border:2px solid {color};text-align:center;max-width:80vw;';
        window.parent.document.body.appendChild(d);
        setTimeout(function(){{d.remove();}}, {duration});
        """
    elif etype == "blur":
        js = f"""
        var el = window.parent.document.querySelector('.main .block-container');
        if(el){{ el.style.filter='blur(6px)'; setTimeout(function(){{el.style.filter='';}}, {duration}); }}
        """
    elif etype == "rtl":
        js = f"""
        var el = window.parent.document.querySelector('.main .block-container');
        if(el){{ el.style.direction='rtl'; setTimeout(function(){{el.style.direction='';}}, {duration}); }}
        """
    elif etype == "hue":
        js = f"""
        var el = window.parent.document.querySelector('.stApp');
        if(el){{ el.style.filter='hue-rotate('+Math.floor(Math.random()*360)+'deg) saturate(1.5)'; setTimeout(function(){{el.style.filter='';}}, {duration}); }}
        """
    elif etype == "scroll":
        to = p.get("to", "top")
        top_expr = "0" if to == "top" else "window.parent.document.body.scrollHeight"
        js = f"window.parent.scrollTo({{top: {top_expr}, behavior: 'smooth'}});"
    elif etype == "hide":
        selector = p.get("selector", ".quote-card")
        js = f"""
        var el = window.parent.document.querySelector('{selector}');
        if(el){{ el.style.transition='opacity 0.4s'; el.style.opacity='0'; setTimeout(function(){{el.style.opacity='1';}}, {duration}); }}
        """
    elif etype == "freeze":
        color = p.get("color", "#ff3b3b")
        js = f"""
        var d=document.createElement('div'); d.id='{uid}';
        d.style.cssText='position:fixed;inset:0;background:{color};opacity:0.32;z-index:999999;pointer-events:none;';
        window.parent.document.body.appendChild(d);
        setTimeout(function(){{ d.remove(); }}, {duration});
        """
    elif etype == "no_scroll":
        js = f"""
        var pd = window.parent.document;
        var prevHtml = pd.documentElement.style.overflow; var prevBody = pd.body.style.overflow;
        pd.documentElement.style.overflow='hidden'; pd.body.style.overflow='hidden';
        setTimeout(function(){{ pd.documentElement.style.overflow=prevHtml; pd.body.style.overflow=prevBody; }}, {duration});
        """
    elif etype == "float_text":
        js = f"""
        var pd = window.parent.document;
        var style = document.createElement('style'); style.id='{uid}';
        style.textContent = '@keyframes fxfloat {{ 0%{{transform:translateY(0);}} 50%{{transform:translateY(-6px);}} 100%{{transform:translateY(0);}} }} .main .block-container p, .main .block-container span, .main .block-container li {{ display:inline-block; animation: fxfloat 1.8s ease-in-out infinite; }}';
        pd.head.appendChild(style);
        setTimeout(function(){{ style.remove(); }}, {duration});
        """
    elif etype == "buttons_fx":
        variant = p.get("variant", "shy")
        if variant == "dance":
            anim = "@keyframes fxdance { 0%,100%{transform:rotate(0deg);} 25%{transform:rotate(-6deg) translateX(-4px);} 75%{transform:rotate(6deg) translateX(4px);} }"
            rule = ".stButton>button, .stDownloadButton>button { animation: fxdance 0.35s ease-in-out infinite; }"
        else:
            anim = "@keyframes fxshy { 0%,100%{transform:translate(0,0);} 50%{transform:translate(12px,-8px);} }"
            rule = ".stButton>button, .stDownloadButton>button { animation: fxshy 0.5s ease-in-out infinite; }"
        js = f"""
        var pd = window.parent.document;
        var style = document.createElement('style'); style.id='{uid}';
        style.textContent = '{anim} {rule}';
        pd.head.appendChild(style);
        setTimeout(function(){{ style.remove(); }}, {duration});
        """
    elif etype == "scratch":
        js = f"""
        var container = document.createElement('div'); container.id='{uid}';
        container.style.cssText='position:fixed;inset:0;pointer-events:none;z-index:999999;overflow:hidden;';
        window.parent.document.body.appendChild(container);
        for(var i=0;i<5;i++){{
          var l=document.createElement('div');
          var top=(10+Math.random()*70)+'%'; var left=(Math.random()*60)+'%';
          l.style.cssText='position:absolute;top:'+top+';left:'+left+';width:2px;height:120px;background:linear-gradient(#ff3b3b,transparent);transform:rotate('+(20+Math.random()*20)+'deg);opacity:0.85;';
          container.appendChild(l);
        }}
        setTimeout(function(){{container.remove();}}, {duration});
        """
    elif etype == "ropes":
        js = f"""
        var el = window.parent.document.querySelector('.stApp');
        if(el){{
          el.style.transition='box-shadow 0.4s';
          el.style.boxShadow='inset 0 0 0 10px repeating-linear-gradient(45deg,#8a5a2b,#8a5a2b 10px,#4a2e1a 10px,#4a2e1a 20px)';
          setTimeout(function(){{ el.style.boxShadow=''; }}, {duration});
        }}
        """
    elif etype == "cut":
        js = f"""
        var d=document.createElement('div'); d.id='{uid}';
        d.style.cssText='position:fixed;top:50%;left:0;width:100%;height:4px;background:linear-gradient(90deg,transparent,#ffe066,transparent);z-index:999999;pointer-events:none;box-shadow:0 0 20px 4px #ffe066;';
        window.parent.document.body.appendChild(d);
        setTimeout(function(){{d.remove();}}, {duration});
        """
    elif etype == "duplicate":
        src = p.get("src", "")
        count = p.get("count", 10)
        js = f"""
        var container = document.createElement('div'); container.id='{uid}';
        container.style.cssText='position:fixed;inset:0;pointer-events:none;z-index:999999;display:flex;flex-wrap:wrap;align-items:center;justify-content:center;gap:6px;background:rgba(10,5,20,0.6);';
        for(var i=0;i<{count};i++){{
          var img=document.createElement('img'); img.src="{src}";
          img.style.cssText='width:56px;height:56px;border-radius:10px;border:2px solid #d4af37;background:#241049;';
          container.appendChild(img);
        }}
        window.parent.document.body.appendChild(container);
        setTimeout(function(){{container.remove();}}, {duration});
        """
    elif etype == "dark_mark":
        js = f"""
        var d=document.createElement('div'); d.id='{uid}';
        d.textContent='💀';
        d.style.cssText='position:fixed;top:50%;left:50%;transform:translate(-50%,-50%);font-size:9rem;opacity:0;color:#2fff8a;z-index:999998;pointer-events:none;filter:drop-shadow(0 0 30px #2fff8a);transition:opacity 1s;';
        window.parent.document.body.appendChild(d);
        setTimeout(function(){{d.style.opacity='0.28';}}, 30);
        setTimeout(function(){{d.style.opacity='0';}}, {max(0,duration-800)});
        setTimeout(function(){{d.remove();}}, {duration});
        """
    elif etype == "slowmo":
        js = f"""
        var pd = window.parent.document;
        var style = document.createElement('style'); style.id='{uid}';
        style.textContent = '.stApp * {{ animation-duration: 4s !important; transition-duration: 1.5s !important; }}';
        pd.head.appendChild(style);
        setTimeout(function(){{ style.remove(); }}, {duration});
        """
    elif etype == "img_scale":
        selector = p.get("selector", ".hp-character-img")
        scale = p.get("scale", 2.5)
        js = f"""
        var el = window.parent.document.querySelector('{selector}');
        if(el){{
          el.style.transition='transform 0.5s'; el.style.transformOrigin='center';
          el.style.transform='scale({scale})'; el.style.position='relative'; el.style.zIndex='999999';
          setTimeout(function(){{ el.style.transform=''; }}, {duration});
        }}
        """
    elif etype == "bump_number":
        selector = p.get("selector", ".streak-card .streak-number")
        js = f"""
        var d=document.createElement('div'); d.id='{uid}';
        d.textContent='+{p.get("amount",1)} ✨';
        d.style.cssText='position:fixed;top:50%;left:50%;transform:translate(-50%,-50%);font-size:2.2rem;font-weight:900;color:#8fe3b0;z-index:999999;pointer-events:none;text-shadow:0 0 16px #2e9e50;';
        window.parent.document.body.appendChild(d);
        setTimeout(function(){{d.remove();}}, {duration});
        """
    elif etype == "grow_number":
        selector = p.get("selector", ".streak-card .streak-number")
        scale = p.get("scale", 2.5)
        js = f"""
        var el = window.parent.document.querySelector('{selector}');
        if(el){{
          el.style.transition='transform 0.5s'; el.style.display='inline-block';
          el.style.transform='scale({scale})';
          setTimeout(function(){{ el.style.transform=''; }}, {duration});
        }}
        """
    elif etype == "scourgify":
        js = f"""
        var container = document.createElement('div'); container.id='{uid}';
        container.style.cssText='position:fixed;inset:0;pointer-events:none;z-index:999999;overflow:hidden;';
        window.parent.document.body.appendChild(container);
        var style = document.createElement('style'); style.id='{uid}_s';
        style.textContent='@keyframes fxfall {{ from {{transform:translateY(-10vh);}} to {{transform:translateY(110vh);}} }}';
        window.parent.document.head.appendChild(style);
        for(var i=0;i<26;i++){{
          var s=document.createElement('div'); s.textContent='🫧';
          s.style.cssText='position:absolute;top:0;left:'+(Math.random()*100)+'%;font-size:'+(14+Math.random()*14)+'px;animation:fxfall '+(1.6+Math.random()*1.6)+'s linear forwards;animation-delay:'+(Math.random()*1)+'s;';
          container.appendChild(s);
        }}
        var flash=document.createElement('div');
        flash.style.cssText='position:fixed;inset:0;background:#ffffff;opacity:0;z-index:999998;transition:opacity 0.6s;';
        window.parent.document.body.appendChild(flash);
        setTimeout(function(){{flash.style.opacity='0.5';}}, {max(0,duration-1200)});
        setTimeout(function(){{flash.style.opacity='0';}}, {max(0,duration-600)});
        setTimeout(function(){{container.remove(); style.remove(); flash.remove();}}, {duration});
        """
    elif etype == "felix":
        js = f"""
        var container = document.createElement('div'); container.id='{uid}';
        container.style.cssText='position:fixed;inset:0;pointer-events:none;z-index:999999;overflow:hidden;';
        window.parent.document.body.appendChild(container);
        var style = document.createElement('style'); style.id='{uid}_s';
        style.textContent='@keyframes fxfall {{ from {{transform:translateY(-10vh);}} to {{transform:translateY(110vh);}} }}';
        window.parent.document.head.appendChild(style);
        var emojis=['✨','🌟','🍀'];
        for(var i=0;i<32;i++){{
          var s=document.createElement('div'); s.textContent=emojis[i%3];
          s.style.cssText='position:absolute;top:0;left:'+(Math.random()*100)+'%;font-size:'+(16+Math.random()*16)+'px;animation:fxfall '+(1.8+Math.random()*1.8)+'s linear forwards;animation-delay:'+(Math.random()*1.4)+'s;';
          container.appendChild(s);
        }}
        var d=document.createElement('div');
        d.textContent='🍀 You are The Luckiest Wizard! 🍀';
        d.style.cssText='position:fixed;top:50%;left:50%;transform:translate(-50%,-50%);font-size:1.4rem;font-weight:900;color:#ffe066;z-index:999999;pointer-events:none;background:rgba(10,5,20,0.9);padding:1rem 1.5rem;border-radius:16px;border:2px solid #ffe066;text-align:center;';
        window.parent.document.body.appendChild(d);
        setTimeout(function(){{container.remove(); style.remove(); d.remove();}}, {duration});
        """

    if js:
        components.html(f"<script>{js}</script>", height=0, width=0)

    st.session_state["last_spell_effect"] = effect


# ---------- TUTORIAL / GUIDED TOUR ----------
TUTORIAL_STEPS = [
    {"target": "title", "text": "👉 Tap this box to reveal your current title! Titles stay locked until your streak reaches that many days."},
    {"target": "character", "text": "👉 This is today's Harry Potter character — they'll cheer you on before your check-in and celebrate after it!"},
    {"target": "mood", "text": "👉 This little wizard shows how today is going — dim and sad if you haven't checked in yet, glowing and happy once you have!"},
    {"target": "streak", "text": "👉 These are your Current Streak and your all-time Highest Streak. Don't let the first one hit zero!"},
    {"target": "progress", "text": f"👉 Here's your total questions solved and any pending backlog. Keep backlog under {PENDING_LIMIT} or the streak resets!"},
    {"target": "spells", "text": "👉 Every 20 questions you solve earns 1 Magic Point (MP). Spend MP here to permanently unlock spells — once unlocked, cast them for free forever!"},
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
if "force_history_open" not in st.session_state:
    st.session_state.force_history_open = False
if "last_spell_effect" not in st.session_state:
    st.session_state.last_spell_effect = None

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

# ---------- BACKGROUND MUSIC (plays your uploaded, rights-cleared track) ----------
_audio_url = get_background_audio_url()
if _audio_url:
    if "music_playing" not in st.session_state:
        st.session_state.music_playing = False
    st.markdown(
        f'<audio id="hp-bg-audio" src="{_audio_url}" loop preload="auto"></audio>',
        unsafe_allow_html=True,
    )
    music_label = "🔇 Pause theme music" if st.session_state.music_playing else "🎵 Play theme music"
    if st.button(music_label, use_container_width=True, key="music_toggle"):
        st.session_state.music_playing = not st.session_state.music_playing
        action = "play" if st.session_state.music_playing else "pause"
        components.html(
            f"<script>var a=window.parent.document.getElementById('hp-bg-audio'); "
            f"if(a){{ a.{action}(); }}</script>",
            height=0, width=0,
        )
    st.caption("Note: Streamlit reruns the page on every interaction, so the track may briefly "
               "restart after some actions — that's a platform limitation, not a bug.")
else:
    st.caption("🎵 No background theme uploaded yet — add an audio file you're licensed to use "
               "to the 'app-audio' Supabase Storage bucket (filename starting with 'theme') to enable music.")

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
    daily_character = get_daily_character(today)
    daily_character_image_url = get_character_image_url(daily_character)
    unlocked_spells = record.get("unlocked_spells", [])
    mp_earned, mp_spent, mp_balance = compute_mp(total_solved, unlocked_spells)

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

    # ---- Today's Harry Potter character ----
    def render_character():
        st.markdown(character_card(daily_character, uploaded_today), unsafe_allow_html=True)
    section("character", render_character)

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

    # ---- Are you a wizard? MP economy + 50-spell shop ----
    def render_spells():
        st.subheader("🪄 Are you a wizard?")
        st.markdown(
            f"""
            <div class="streak-box">
                <div class="streak-card high">
                    <div class="streak-number">{mp_balance}</div>
                    <div class="streak-label">MP Available</div>
                </div>
                <div class="streak-card">
                    <div class="streak-number">{len(unlocked_spells)}/{len(SPELLS)}</div>
                    <div class="streak-label">Spells Unlocked</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.caption(f"💠 Every {MP_PER_QUESTIONS} questions solved (lifetime total) earns 1 MP. "
                   f"Unlocking a spell spends its MP cost once — after that, cast it for free, forever.")

        with st.expander("📖 Open the Spell Shop (50 spells)", expanded=False):
            search = st.text_input("🔍 Search spells", key="spell_search", placeholder="e.g. Lumos, Patronus, flash...")
            filtered = [s for s in SPELLS if search.lower() in s["name"].lower() or search.lower() in s["desc"].lower()] if search else SPELLS

            with st.container(height=520):
                for spell in filtered:
                    name = spell["name"]
                    is_unlocked = name in unlocked_spells
                    col_a, col_b = st.columns([3, 1.2])
                    with col_a:
                        status = "✅ Unlocked — cast anytime, free" if is_unlocked else f"🔒 Locked — costs {spell['cost']} MP"
                        st.markdown(
                            f"**{name}**  \n{spell['desc']}  \n"
                            f"<span style='color:{'#8fe3b0' if is_unlocked else '#cbb98f'};font-size:0.82rem;'>{status}</span>",
                            unsafe_allow_html=True,
                        )
                    with col_b:
                        if is_unlocked:
                            if st.button("✨ Cast", key=f"cast_{name}", use_container_width=True):
                                dynamic = {}
                                if spell["effect"]["type"] == "duplicate":
                                    dynamic["src"] = daily_character_image_url
                                if spell["effect"]["type"] == "reveal_total":
                                    dynamic["total_solved"] = total_solved
                                cast_effect(spell["effect"], dynamic=dynamic)
                        else:
                            can_afford = mp_balance >= spell["cost"]
                            if st.button(
                                f"🔓 Unlock ({spell['cost']} MP)",
                                key=f"unlock_{name}",
                                use_container_width=True,
                                disabled=not can_afford,
                            ):
                                unlock_spell(users, username, name)
                                st.toast(f"🪄 {name} unlocked!", icon="🪄")
                                dynamic = {}
                                if spell["effect"]["type"] == "duplicate":
                                    dynamic["src"] = daily_character_image_url
                                if spell["effect"]["type"] == "reveal_total":
                                    dynamic["total_solved"] = total_solved
                                cast_effect(spell["effect"], dynamic=dynamic)
                                st.rerun()
                    st.markdown("<hr style='border-color:rgba(212,175,55,0.15);margin:0.3rem 0;'>", unsafe_allow_html=True)
    section("spells", render_spells)

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
            with st.expander(f"View full history ({len(rows)} day(s) logged)", expanded=st.session_state.force_history_open):
                st.dataframe(df, use_container_width=True, hide_index=True)
            if st.session_state.force_history_open:
                st.session_state.force_history_open = False
        else:
            st.caption("No history yet — your daily log will build up here.")
    section("history", render_history)

    st.divider()
    st.caption("Missing a full calendar day resets your current streak (and pending backlog) to 0. Your highest streak is always saved.")
