# app.py  —  run with:  streamlit run app.py
import os
from datetime import datetime

import streamlit as st
from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

import mood  # your existing mood.py (MOODS dict + get_system_prompt)

load_dotenv()

st.set_page_config(page_title="Moody AI", page_icon="🔮", layout="wide")

# ----------------------------------------------------------------------------
# Mood look & feel (UI only — personalities still come from mood.py)
# ----------------------------------------------------------------------------
MOOD_UI = {
    "happy": {"emoji": "😊", "color": "#ff9d1c", "tag": "Stay positive. Keep going."},
    "sad":   {"emoji": "😢", "color": "#2f9bff", "tag": "It's okay to feel."},
    "angry": {"emoji": "😠", "color": "#ff3b30", "tag": "Breathe. You got this."},
}
DEFAULT_UI = {"emoji": "🙂", "color": "#ff9d1c", "tag": "Pick this vibe."}


def ui(m):
    return MOOD_UI.get(m, DEFAULT_UI)


# ----------------------------------------------------------------------------
# Session state
# ----------------------------------------------------------------------------
ss = st.session_state
ss.setdefault("page", "Home")
ss.setdefault("mood", "happy")
ss.setdefault("messages", [])        # [{"role": "user"/"assistant", "content", "mood"}]
ss.setdefault("mood_log", [{"time": datetime.now(), "mood": "happy"}])
ss.setdefault("temperature", 0.8)
ss.setdefault("model_name", "openrouter/free")


def set_mood(m):
    if m != ss.mood:
        ss.mood = m
        ss.mood_log.append({"time": datetime.now(), "mood": m})


def go(page):
    ss.page = page


# ----------------------------------------------------------------------------
# LLM
# ----------------------------------------------------------------------------
@st.cache_resource
def get_model(model_name: str, temperature: float):
    return ChatOpenAI(
        model=model_name,
        api_key=os.getenv("OPENROUTER_API_KEY"),
        base_url="https://openrouter.ai/api/v1",
        temperature=temperature,
    )


def ask_ai(user_text: str) -> str:
    model = get_model(ss.model_name, ss.temperature)
    msgs = [SystemMessage(content=mood.get_system_prompt(ss.mood))]
    for m in ss.messages[-12:]:  # short memory
        cls = HumanMessage if m["role"] == "user" else AIMessage
        msgs.append(cls(content=m["content"]))
    msgs.append(HumanMessage(content=user_text))
    return model.invoke(msgs).content


# ----------------------------------------------------------------------------
# CSS
# ----------------------------------------------------------------------------
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600&display=swap');

:root { --c: __C__; --c-soft: __C__55; --c-faint: __C__22; }

html, body, [class*="css"], .stApp { font-family: 'Outfit', sans-serif; }
.stApp { background: radial-gradient(ellipse at 50% 30%, #1a0d02 0%, #050505 55%, #000 100%); color: #e9e9ee; }
header[data-testid="stHeader"], #MainMenu, footer, [data-testid="stToolbar"] { display: none; }
.block-container { padding: 1.2rem 2.5rem 7rem 2.5rem; max-width: 1200px; }

/* ---------- sidebar ---------- */
section[data-testid="stSidebar"] { background: #030303; border-right: 1px solid var(--c-faint); }
section[data-testid="stSidebar"] .block-container { padding-top: 1.5rem; }
section[data-testid="stSidebar"] .stButton button {
    width: 100%; justify-content: flex-start; background: transparent; color: #aab;
    border: 1px solid transparent; border-radius: 14px; padding: .65rem 1rem; font-size: .95rem;
}
section[data-testid="stSidebar"] .stButton button:hover { color: #fff; border-color: var(--c-faint); }
section[data-testid="stSidebar"] .stButton button[kind="primary"] {
    background: linear-gradient(90deg, var(--c-faint), transparent); color: #fff;
    border: 1px solid var(--c); box-shadow: 0 0 18px var(--c-soft), inset 0 0 12px var(--c-faint);
}
.side-foot { margin-top: 14rem; color: #7a7f99; font-size: .68rem; letter-spacing: .2em; line-height: 1.8; }
.side-foot b { color: var(--c); }

/* ---------- top bar ---------- */
.topbar { display:flex; align-items:center; justify-content:space-between;
          padding-bottom:.9rem; border-bottom:1px solid var(--c-faint); }
.brand { display:flex; align-items:center; gap:14px; }
.logo { width:46px; height:46px; border-radius:50%; border:1px solid var(--c);
        background: radial-gradient(circle, var(--c) 0 10%, transparent 12%), radial-gradient(circle, var(--c-faint), transparent 70%);
        box-shadow: 0 0 20px var(--c-soft); }
.brand h1 { margin:0; font-size:1.55rem; font-weight:300; letter-spacing:.35em; color:#f2f2f2; }
.brand h1 span { color: var(--c); font-weight:500; }
.status { margin-left:10px; padding-left:16px; border-left:1px solid #333; font-size:.65rem;
          letter-spacing:.25em; color:#8fa; display:flex; align-items:center; gap:8px; }
.dot { width:8px; height:8px; border-radius:50%; background:#2ee59d; box-shadow:0 0 10px #2ee59d; }
.tagline { font-size:.68rem; letter-spacing:.3em; color:#6f86b8; }

/* ---------- orb ---------- */
.hero { display:flex; align-items:center; justify-content:space-between; min-height:430px; }
.side-note { width:170px; font-size:.68rem; letter-spacing:.3em; color:#b9bccf; line-height:1.9; }
.side-note i { display:block; width:26px; height:2px; background:var(--c); margin-top:8px; }
.side-note.r { text-align:left; }
.orb-wrap { position:relative; width:380px; height:400px; display:flex; align-items:center; justify-content:center; }
.orb { position:relative; width:320px; height:320px; border-radius:50%; }
.orb::before { content:""; position:absolute; inset:-12px; border-radius:50%; border:1px solid var(--c-soft); }
.dust { position:absolute; inset:0; border-radius:50%;
        background:
          radial-gradient(circle, transparent 52%, var(--c-soft) 53%, transparent 70%),
          repeating-conic-gradient(from 0deg, var(--c) 0 .6deg, transparent .6deg 4deg);
        -webkit-mask: radial-gradient(circle, transparent 46%, #000 48%, #000 72%, transparent 74%);
                mask: radial-gradient(circle, transparent 46%, #000 48%, #000 72%, transparent 74%);
        opacity:.55; animation: spin 40s linear infinite; }
.rays { position:absolute; inset:-60px; border-radius:50%;
        background: repeating-conic-gradient(from 8deg, var(--c) 0 .35deg, transparent .35deg 31deg);
        -webkit-mask: radial-gradient(circle, transparent 20%, #000 24%, #000 52%, transparent 66%);
                mask: radial-gradient(circle, transparent 20%, #000 24%, #000 52%, transparent 66%);
        animation: spin 60s linear infinite reverse; filter: drop-shadow(0 0 6px var(--c)); }
.ring { position:absolute; inset:48px; border-radius:50%; border:5px solid var(--c);
        box-shadow: 0 0 22px var(--c), inset 0 0 22px var(--c); opacity:.9; }
.r1 { transform: rotate(20deg) scaleY(.55); animation: wob1 9s ease-in-out infinite; }
.r2 { transform: rotate(-35deg) scaleY(.7);  animation: wob2 12s ease-in-out infinite; border-width:3px; }
.core { position:absolute; left:50%; top:50%; width:74px; height:74px; transform:translate(-50%,-50%);
        border-radius:50%; background: radial-gradient(circle, #fff 0 25%, #ffe9a8 45%, var(--c) 75%, transparent 100%);
        box-shadow: 0 0 60px 20px var(--c), 0 0 140px 50px var(--c-soft); animation: pulse 3.2s ease-in-out infinite; }
.orb-base { position:absolute; bottom:6px; width:260px; height:46px; border-radius:50%;
            border:1px solid var(--c-soft); box-shadow: 0 0 30px var(--c-soft), inset 0 0 20px var(--c-faint); }
@keyframes spin  { to { transform: rotate(360deg); } }
@keyframes pulse { 50% { transform: translate(-50%,-50%) scale(1.14); } }
@keyframes wob1  { 50% { transform: rotate(60deg) scaleY(.5); } }
@keyframes wob2  { 50% { transform: rotate(-80deg) scaleY(.62); } }
@media (prefers-reduced-motion: reduce) { .dust,.rays,.ring,.core { animation:none !important; } }

/* ---------- choose your mood ---------- */
.choose { display:flex; align-items:center; gap:18px; color:#cfd1de; font-size:.75rem;
          letter-spacing:.35em; margin:.4rem 0 1rem; }
.choose::before, .choose::after { content:""; flex:1; height:1px; background:linear-gradient(90deg, transparent, #3a2a14, transparent); }

.stButton button { transition: all .2s; }
div[class*="st-key-mood_"] button {
    width:100%; height:78px; border-radius:22px; background: rgba(255,255,255,.015);
    text-align:left; justify-content:flex-start; padding: 0 1.2rem; color:#9aa; border-width:1px; border-style:solid;
}
div[class*="st-key-mood_"] button p { margin:0; font-size:.78rem; line-height:1.5; }
div[class*="st-key-mood_"] button p strong { font-size:1rem; letter-spacing:.18em; }
.st-key-mood_happy button { border-color:#ff9d1c; color:#ffb454; box-shadow:0 0 18px #ff9d1c33, inset 0 0 14px #ff9d1c18; }
.st-key-mood_sad   button { border-color:#2f9bff; color:#6cb8ff; box-shadow:0 0 18px #2f9bff33, inset 0 0 14px #2f9bff18; }
.st-key-mood_angry button { border-color:#ff3b30; color:#ff7a70; box-shadow:0 0 18px #ff3b3033, inset 0 0 14px #ff3b3018; }
div[class*="st-key-mood_"] button:hover { transform: translateY(-2px); filter: brightness(1.25); }
.st-key-mood___M__ button { box-shadow: 0 0 34px __C__99, inset 0 0 22px __C__33 !important; background: __C__12 !important; }

/* ---------- chat ---------- */
[data-testid="stChatMessage"] { background: rgba(255,255,255,.02); border:1px solid var(--c-faint);
                                border-radius:18px; padding:.9rem 1.1rem; }
[data-testid="stChatInput"] { background:transparent; }
[data-testid="stChatInput"] > div { border-radius:999px; border:1px solid var(--c-soft); background:#0a0705;
                                    box-shadow: 0 0 20px var(--c-faint); }
[data-testid="stChatInput"] textarea { color:#eee; }
[data-testid="stBottom"] > div, [data-testid="stBottomBlockContainer"] { background: transparent; }
.stApp [data-testid="stBottom"] { background: linear-gradient(transparent, #000 40%); }

/* ---------- misc ---------- */
.card { border:1px solid var(--c-faint); border-radius:16px; padding:1rem 1.2rem; background:rgba(255,255,255,.02); margin-bottom:.6rem; }
.hist-dot { display:inline-block; width:10px; height:10px; border-radius:50%; margin-right:10px; }
h2, h3 { font-weight:400; letter-spacing:.08em; }
</style>
"""


def inject_css():
    css = CSS.replace("__M__", ss.mood).replace("__C__", ui(ss.mood)["color"])
    st.markdown(css, unsafe_allow_html=True)


# ----------------------------------------------------------------------------
# Pieces
# ----------------------------------------------------------------------------
def sidebar():
    with st.sidebar:
        st.markdown(
            '<div class="brand" style="margin-bottom:1.2rem"><div class="logo"></div></div>',
            unsafe_allow_html=True,
        )
        for label, icon in [("Home", "🏠"), ("Chat", "💬"), ("Mood History", "🕒"), ("Settings", "⚙️")]:
            st.button(
                f"{icon}  {label}",
                key=f"nav_{label}",
                type="primary" if ss.page == label else "secondary",
                on_click=go,
                args=(label,),
                use_container_width=True,
            )
        st.markdown(
            '<div class="side-foot"><b>✦</b><br>BETTER MOOD.<br>BRIGHTER YOU.</div>',
            unsafe_allow_html=True,
        )


def topbar():
    st.markdown(
        """
        <div class="topbar">
          <div class="brand">
            <div class="logo"></div>
            <h1>MOODY <span>AI</span></h1>
            <div class="status"><span class="dot"></span>CORE ONLINE</div>
          </div>
          <div class="tagline">SAME AI, DIFFERENT VIBES.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def orb():
    st.markdown(
        """
        <div class="hero">
          <div class="side-note">YOUR EMOTIONS<br>MATTER<i></i></div>
          <div class="orb-wrap">
            <div class="orb">
              <div class="rays"></div><div class="dust"></div>
              <div class="ring r1"></div><div class="ring r2"></div>
              <div class="core"></div>
            </div>
            <div class="orb-base"></div>
          </div>
          <div class="side-note r">MOODY AI<br>IS HERE FOR YOU<i></i></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def mood_picker():
    st.markdown('<div class="choose">CHOOSE YOUR MOOD</div>', unsafe_allow_html=True)
    names = list(mood.MOODS.keys())
    cols = st.columns(len(names), gap="medium")
    for col, m in zip(cols, names):
        u = ui(m)
        with col:
            st.button(
                f"{u['emoji']}  **{m.upper()}**\n\n{u['tag']}",
                key=f"mood_{m}",
                on_click=set_mood,
                args=(m,),
                use_container_width=True,
            )


def handle_input(text: str):
    # Same "mood: sad" command as the terminal version
    if text.lower().startswith("mood:"):
        wanted = text.split(":", 1)[1].strip().lower()
        if wanted in mood.MOODS:
            set_mood(wanted)
            ss.messages.append({"role": "assistant", "mood": wanted,
                                "content": f"*Switched to **{wanted.upper()}** mode.*"})
        else:
            ss.messages.append({"role": "assistant", "mood": ss.mood,
                                "content": f"Unknown mood. Available: {', '.join(mood.MOODS.keys())}"})
        ss.page = "Chat"
        return

    ss.page = "Chat"
    try:
        with st.spinner("Thinking..."):
            reply = ask_ai(text)
    except Exception as e:
        reply = f"⚠️ Couldn't reach the model: `{e}`\n\nCheck `OPENROUTER_API_KEY` in your `.env`."
    ss.messages.append({"role": "user", "content": text, "mood": ss.mood})
    ss.messages.append({"role": "assistant", "content": reply, "mood": ss.mood})


# ----------------------------------------------------------------------------
# Pages
# ----------------------------------------------------------------------------
def page_home():
    orb()
    mood_picker()


def page_chat():
    st.markdown(f"### Chat · {ui(ss.mood)['emoji']} {ss.mood.upper()} mode")
    if not ss.messages:
        st.info("Say something below. Tip: type `mood: sad` to switch personality.")
    for m in ss.messages:
        avatar = "🧑" if m["role"] == "user" else ui(m["mood"])["emoji"]
        with st.chat_message(m["role"], avatar=avatar):
            st.markdown(m["content"])
    mood_picker()


def page_history():
    st.markdown("### Mood History")
    for e in reversed(ss.mood_log):
        c = ui(e["mood"])["color"]
        st.markdown(
            f'<div class="card"><span class="hist-dot" style="background:{c};box-shadow:0 0 10px {c}"></span>'
            f'{ui(e["mood"])["emoji"]} <b>{e["mood"].upper()}</b>'
            f'<span style="float:right;color:#8a8fa8">{e["time"].strftime("%b %d, %H:%M:%S")}</span></div>',
            unsafe_allow_html=True,
        )
    counts = {}
    for e in ss.mood_log:
        counts[e["mood"]] = counts.get(e["mood"], 0) + 1
    st.bar_chart(counts)


def page_settings():
    st.markdown("### Settings")
    ss.model_name = st.text_input("Model", ss.model_name)
    ss.temperature = st.slider("Creativity (temperature)", 0.0, 1.5, ss.temperature, 0.05)
    st.write("API key:", "✅ found" if os.getenv("OPENROUTER_API_KEY") else "❌ missing (add to .env)")
    if st.button("Clear chat"):
        ss.messages = []
        st.rerun()


# ----------------------------------------------------------------------------
# Run
# ----------------------------------------------------------------------------
prompt = st.chat_input("Talk to your AI...")
if prompt:
    handle_input(prompt)

inject_css()
sidebar()
topbar()

{"Home": page_home, "Chat": page_chat, "Mood History": page_history, "Settings": page_settings}[ss.page]()