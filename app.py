import streamlit as st
import re
import uuid
import pandas as pd
from dotenv import load_dotenv
from knowledge_base_loader import load_knowledge_base, search_knowledge_base
from llm_client import ask_moei
from session_store import upsert_session, save_turn, load_history, get_session_profile, analytics_summary

load_dotenv()

st.set_page_config(page_title="Ask MOEI v2.0", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Arabic:wght@300;400;600&family=IBM+Plex+Sans:ital,wght@0,300;0,400;0,600;1,400&display=swap');

:root {
  --gold:   #B8963E;
  --gold-l: #F0D98A;
  --dark:   #0D1B2A;
  --green:  #006C35;
  --red:    #C1272D;
  --bg:     #F5F4EF;
  --card:   #FFFFFF;
  --text:   #1C1C1C;
  --muted:  #6B7280;
  --border: #DDD9CF;
  --warn:   #92400E;
}

html, body, [class*="css"] {
  font-family: 'IBM Plex Sans', 'IBM Plex Sans Arabic', sans-serif;
}
.stApp { background: var(--bg); }

/* UAE flag accent bar */
.uae-bar {
  height: 5px;
  background: linear-gradient(to right, var(--green) 33.3%, var(--gold) 33.3% 66.6%, var(--red) 66.6%);
  margin: -1rem -1rem 0 -1rem;
}

/* Header */
.moei-header {
  background: var(--dark);
  padding: 1.1rem 2rem 1rem 2rem;
  margin: 0 -1rem 1.5rem -1rem;
}
.moei-header h1 {
  color: #fff; font-size: 1.35rem; font-weight: 600;
  margin: 0 0 .15rem 0; letter-spacing: -.01em;
}
.moei-header .sub {
  color: var(--gold); font-size: .8rem; font-weight: 300;
  letter-spacing: .02em;
}

/* Chat bubbles */
.user-bubble {
  background: var(--dark); color: #fff;
  padding: .7rem 1rem; border-radius: 18px 18px 4px 18px;
  margin: .6rem 0 .6rem 4rem;
  font-size: .93rem; line-height: 1.55;
}
.assistant-bubble {
  background: var(--card);
  border-left: 3px solid var(--gold);
  padding: .85rem 1.1rem; border-radius: 0 12px 12px 0;
  margin: .6rem 4rem .6rem 0;
  font-size: .93rem; line-height: 1.65;
  box-shadow: 0 1px 6px rgba(0,0,0,.06);
  color: var(--text);
}
.assistant-bubble.rtl {
  direction: rtl; text-align: right;
  border-left: none; border-right: 3px solid var(--gold);
  border-radius: 12px 0 0 12px;
  font-family: 'IBM Plex Sans Arabic', sans-serif;
}

/* Language badge */
.lang-badge {
  display: inline-block; background: var(--gold); color: var(--dark);
  font-size: .65rem; font-weight: 700; padding: 1px 5px;
  border-radius: 3px; margin-left: 6px; vertical-align: middle;
  letter-spacing: .05em;
}

/* Service link card */
.service-card {
  display: flex; align-items: center; gap: .75rem;
  background: var(--card); border: 1px solid var(--gold);
  border-left: 4px solid var(--gold);
  border-radius: 8px; padding: .65rem 1rem;
  margin: .5rem 0;
}
.service-card .sc-label { font-size: .7rem; color: var(--muted); text-transform: uppercase; letter-spacing: .06em; }
.service-card a { color: var(--dark); font-weight: 600; font-size: .9rem; text-decoration: none; }
.service-card a:hover { color: var(--gold); }

/* Nudge pills */
.nudge-pill {
  display: inline-block; background: #EEF0E8;
  border: 1px solid var(--border); border-radius: 99px;
  padding: .25rem .7rem; font-size: .8rem; color: var(--text);
  margin: .25rem .25rem 0 0;
}

/* Fallback notice */
.fallback-notice {
  background: #FFFBEB; border-left: 3px solid var(--gold);
  padding: .55rem .85rem; border-radius: 0 6px 6px 0;
  font-size: .82rem; color: var(--warn); margin-top: .5rem;
}

/* Empty state */
.empty-state {
  text-align: center; padding: 3rem 1rem 1.5rem;
}
.empty-state .title { font-size: 1.1rem; font-weight: 600; color: var(--dark); margin-bottom: .4rem; }
.empty-state .sub   { font-size: .88rem; color: var(--muted); line-height: 1.6; }

/* Stat box */
.stat-box { background: var(--card); border: 1px solid var(--border); border-radius: 8px; padding: .6rem 1rem; text-align: center; }
.stat-box .num { font-size: 1.5rem; font-weight: 700; color: var(--dark); }
.stat-box .lbl { font-size: .68rem; color: var(--muted); text-transform: uppercase; letter-spacing: .06em; }

/* Sidebar */
.sb-title { font-size: .72rem; font-weight: 700; color: var(--muted); text-transform: uppercase; letter-spacing: .06em; margin: 0 0 .15rem; line-height: 1.3; }
.sb-hr    { margin: .5rem 0; border: 0; border-top: 1px solid var(--border); }
section[data-testid="stSidebar"] .block-container { padding-top: 1.5rem; }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def get_kb():
    return load_knowledge_base("knowledge_base")

kb = get_kb()


def _init_state():
    defaults = {
        "session_id":        str(uuid.uuid4())[:8],
        "messages":          [],
        "user_profile":      "Citizen",
        "session_analytics": {"total": 0, "arabic": 0, "fallbacks": 0, "intents": {}},
        "active_tab":        "chat",
        "custom_api_key":    "",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

_init_state()


def _is_arabic(text: str) -> bool:
    return bool(re.search(r"[؀-ۿ]", text))


# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div style="font-size:1rem;font-weight:700;color:var(--dark);line-height:1.2">Ask MOEI v2.0</div>'
                '<div style="font-size:.72rem;color:var(--muted)">Maritime Services Assistant</div>', unsafe_allow_html=True)
    st.markdown('<hr class="sb-hr">', unsafe_allow_html=True)

    st.markdown('<div class="sb-title">Session</div>', unsafe_allow_html=True)
    sid_input = st.text_input("Session", value=st.session_state.session_id,
                               help="Enter any name to resume a previous conversation.",
                               label_visibility="collapsed")
    if sid_input and sid_input != st.session_state.session_id:
        st.session_state.session_id = sid_input
        past = load_history(sid_input, limit=20)
        if past:
            st.session_state.messages = past
            prof = get_session_profile(sid_input)
            if prof:
                st.session_state.user_profile = prof["user_profile"]
            st.rerun()

    st.markdown('<hr class="sb-hr">', unsafe_allow_html=True)

    st.markdown('<div class="sb-title">Profile</div>', unsafe_allow_html=True)
    profile = st.selectbox("Profile", ["Citizen", "Resident", "Business", "Visitor"],
                            index=["Citizen", "Resident", "Business", "Visitor"].index(st.session_state.user_profile),
                            label_visibility="collapsed")
    if profile != st.session_state.user_profile:
        st.session_state.user_profile = profile
        upsert_session(st.session_state.session_id, profile)

    st.markdown('<hr class="sb-hr">', unsafe_allow_html=True)

    st.markdown('<div class="sb-title">API Key</div>', unsafe_allow_html=True)
    with st.expander("Custom API Key", expanded=False):
        st.caption("Leave empty to use the key in .env")
        ck = st.text_input("Key", value=st.session_state.custom_api_key, type="password",
                            label_visibility="collapsed")
        if ck != st.session_state.custom_api_key:
            st.session_state.custom_api_key = ck
            st.success("Key updated.") if ck else st.info("Using .env key.")

    st.markdown('<hr class="sb-hr">', unsafe_allow_html=True)

    st.markdown('<div class="sb-title">Knowledge Base</div>', unsafe_allow_html=True)
    if kb:
        st.success(f"{len(set(d['name'] for d in kb))} guides · {len(kb)} chunks")
    else:
        st.warning("No guides found in knowledge_base/")

    st.markdown('<hr class="sb-hr">', unsafe_allow_html=True)

    st.markdown('<div class="sb-title">This Session</div>', unsafe_allow_html=True)
    a = st.session_state.session_analytics
    c1, c2 = st.columns(2)
    c1.metric("Queries", a["total"])
    c2.metric("Arabic", a["arabic"])
    c1.metric("Fallbacks", a["fallbacks"])
    if a["intents"]:
        c2.metric("Top Intent", max(a["intents"], key=a["intents"].get)[:10])

    if st.button("Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.session_analytics = {"total": 0, "arabic": 0, "fallbacks": 0, "intents": {}}
        st.session_state.custom_api_key = ""
        st.rerun()

    st.markdown('<hr class="sb-hr">', unsafe_allow_html=True)

    st.markdown('<div class="sb-title">View</div>', unsafe_allow_html=True)
    tab_choice = st.radio("View", ["Chat", "Admin"], label_visibility="collapsed")
    st.session_state.active_tab = "admin" if tab_choice == "Admin" else "chat"


# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="uae-bar"></div>
<div class="moei-header">
  <h1>Ask MOEI v2.0</h1>
  <div class="sub">وزارة الطاقة والبنية التحتية &nbsp;·&nbsp; Ministry of Energy &amp; Infrastructure</div>
</div>
""", unsafe_allow_html=True)


# ── Admin tab ──────────────────────────────────────────────────────────────────
if st.session_state.active_tab == "admin":
    st.subheader("Admin Analytics")
    stats = analytics_summary()

    c1, c2, c3, c4 = st.columns(4)
    lang_pct = round(stats["arabic"] / max(stats["total"], 1) * 100)
    for col, num, lbl in [
        (c1, stats["total"],        "Total Queries"),
        (c2, stats["sessions"],     "Sessions"),
        (c3, f'{stats["fallback_rate"]}%', "Fallback Rate"),
        (c4, f"{lang_pct}%",        "Arabic Queries"),
    ]:
        col.markdown(f'<div class="stat-box"><div class="num">{num}</div><div class="lbl">{lbl}</div></div>',
                     unsafe_allow_html=True)

    st.markdown("---")
    ca, cb = st.columns(2)
    with ca:
        st.markdown("**Top Intents**")
        for intent, count in stats["top_intents"]:
            pct = round(count / max(stats["total"], 1) * 100)
            st.markdown(f"`{intent}` — **{count}** ({pct}%)")
        if not stats["top_intents"]:
            st.info("No queries yet.")
    with cb:
        st.markdown("**Daily Activity**")
        if stats["daily"]:
            st.bar_chart(pd.DataFrame(stats["daily"], columns=["Date", "Queries"]).set_index("Date"))
        else:
            st.info("No data yet.")

    st.markdown("---")
    st.markdown("**Language Split**")
    if stats["total"] > 0:
        st.bar_chart(pd.DataFrame({"Count": {"English": stats["total"] - stats["arabic"], "Arabic": stats["arabic"]}}))
    else:
        st.info("No queries yet.")

    st.stop()


# ── Chat tab ───────────────────────────────────────────────────────────────────
def _render(role: str, content: str, meta: dict | None = None):
    escaped = content.replace("<", "&lt;").replace(">", "&gt;")
    if role == "user":
        badge = '<span class="lang-badge">AR</span>' if _is_arabic(content) else '<span class="lang-badge">EN</span>'
        st.markdown(f'<div class="user-bubble">{escaped}{badge}</div>', unsafe_allow_html=True)
        return

    rtl = "rtl" if _is_arabic(content) else ""
    st.markdown(f'<div class="assistant-bubble {rtl}">{escaped}</div>', unsafe_allow_html=True)

    if not meta:
        return
    if meta.get("service_link") and meta.get("service_name"):
        st.markdown(
            f'<div class="service-card">'
            f'<div><div class="sc-label">Apply Now</div>'
            f'<a href="{meta["service_link"]}" target="_blank" rel="noopener">{meta["service_name"]}</a>'
            f'</div></div>',
            unsafe_allow_html=True,
        )
    if meta.get("nudges"):
        pills = "".join(f'<span class="nudge-pill">{n}</span>' for n in meta["nudges"])
        st.markdown(f"<div style='margin-top:.4rem'>{pills}</div>", unsafe_allow_html=True)
    if meta.get("is_fallback"):
        st.markdown(
            '<div class="fallback-notice">This question is not fully covered by the knowledge base. '
            'For official answers visit <a href="https://www.moei.gov.ae" target="_blank">moei.gov.ae</a></div>',
            unsafe_allow_html=True,
        )


for msg in st.session_state.messages:
    _render(msg["role"], msg["content"], msg.get("metadata"))

if not st.session_state.messages:
    st.markdown("""
    <div class="empty-state">
      <div class="title">Welcome to Ask MOEI v2.0</div>
      <div class="sub">
        Ask about UAE maritime services in English or Arabic.<br>
        اسألني عن الخدمات البحرية باللغتين الإنجليزية والعربية
      </div>
    </div>
    """, unsafe_allow_html=True)
    cols = st.columns(2)
    for i, q in enumerate([
        "How do I renew my pleasure boat registration?",
        "What is a PRO card and how do I get one?",
        "How to apply for flag state endorsement?",
        "What is GMDSS endorsement?",
        "كيف أتقدم بطلب شهادة الكفاءة؟",
        "How do I get a Certificate of Competency?",
    ]):
        if cols[i % 2].button(q, key=f"sq_{i}", use_container_width=True):
            st.session_state["_pending"] = q

pending = st.session_state.pop("_pending", None)
user_input = st.chat_input("Ask about MOEI maritime services / اسأل عن الخدمات البحرية") or pending

if user_input:
    arabic = _is_arabic(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.session_state.session_analytics["total"] += 1
    if arabic:
        st.session_state.session_analytics["arabic"] += 1
    upsert_session(st.session_state.session_id, st.session_state.user_profile)
    save_turn(st.session_state.session_id, "user", user_input, {"is_arabic": arabic})

    with st.spinner("جاري البحث..." if arabic else "Searching..."):
        result = ask_moei(
            query=user_input,
            context_chunks=search_knowledge_base(kb, user_input, top_k=4),
            chat_history=st.session_state.messages[:-1],
            user_profile=st.session_state.user_profile,
            custom_api_key=st.session_state.custom_api_key,
        )

    intent = result.get("intent", "general")
    if result.get("is_fallback"):
        st.session_state.session_analytics["fallbacks"] += 1
    st.session_state.session_analytics["intents"][intent] = \
        st.session_state.session_analytics["intents"].get(intent, 0) + 1

    meta = {k: result.get(k) for k in ("service_link", "service_name", "nudges", "is_fallback", "intent")}
    meta.setdefault("nudges", [])
    meta.setdefault("is_fallback", False)
    st.session_state.messages.append({"role": "assistant", "content": result["answer"], "metadata": meta})
    save_turn(st.session_state.session_id, "assistant", result["answer"],
              {"intent": intent, "is_fallback": result.get("is_fallback"), "is_arabic": arabic})
    st.rerun()
