"""
AI Study Assistant - Modern Interactive Web Application
======================================================
Coordinated Palette: Midnight Navy, Indigo, and Vibrant Teal.
Features:
- High-Speed Concept Doubts (Ask a Question)
- Rapid Notes Summarization (Summarize Notes)
- Practice Quiz Generator (Generate Quiz)
- Privacy-conscious Collapsible Settings
- Sidebar History Browser with Instant Result Replay
"""

import os
import uuid
from datetime import datetime
import streamlit as st
from dotenv import load_dotenv
from agent import route_task, get_supported_gemini_models, resolve_active_gemini_model, PREFERRED_GEMINI_MODEL

# Load environment variables
load_dotenv()

# =====================================================================
# PAGE CONFIGURATION
# =====================================================================
st.set_page_config(
    page_title="AI Study Assistant",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =====================================================================
# SESSION STATE INITIALIZATION
# =====================================================================
if "history" not in st.session_state:
    st.session_state.history = []
if "selected_history_id" not in st.session_state:
    st.session_state.selected_history_id = None
if "confirm_clear_history" not in st.session_state:
    st.session_state.confirm_clear_history = False
if "nav_view" not in st.session_state:
    st.session_state.nav_view = "Workspace"

# Model discovery wrapper (caches in-memory per API key hash and refreshes on key change)
def fetch_cached_gemini_models(api_key: str):
    return get_supported_gemini_models(api_key)

def add_to_history(task_type: str, icon: str, title: str, subtitle: str, input_payload: str, output_result: str, provider: str, model: str):
    entry = {
        "id": str(uuid.uuid4())[:8],
        "timestamp": datetime.now().strftime("%b %d, %H:%M"),
        "task_type": task_type,
        "icon": icon,
        "title": title[:65] + ("..." if len(title) > 65 else ""),
        "subtitle": subtitle,
        "input_payload": input_payload,
        "output_result": output_result,
        "provider": provider,
        "model": model,
    }
    st.session_state.history.insert(0, entry)

# =====================================================================
# COORDINATED MIDNIGHT NAVY, INDIGO & TEAL STYLING
# =====================================================================
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

    :root {
        --midnight-900: #070a13;
        --midnight-800: #0b1120;
        --midnight-700: #111a2e;
        --indigo-600: #4f46e5;
        --indigo-500: #6366f1;
        --indigo-400: #818cf8;
        --teal-500: #14b8a6;
        --teal-400: #2dd4bf;
        --teal-300: #5eead4;
        --slate-100: #f1f5f9;
        --slate-200: #e2e8f0;
        --slate-700: #334155;
        --slate-900: #0f172a;
    }

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Main Container */
    .main .block-container {
        padding-top: 1.25rem;
        padding-bottom: 3rem;
        max-width: 1240px;
    }

    /* Dark Gradient Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #070a13 0%, #0b1120 45%, #0f172a 100%) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.08) !important;
    }
    [data-testid="stSidebar"] * {
        color: #e2e8f0;
    }
    [data-testid="stSidebar"] .stRadio label {
        color: #e2e8f0 !important;
        font-weight: 500 !important;
    }

    /* Hero Banner with Midnight Navy & Teal Accents */
    .hero-banner {
        background: linear-gradient(135deg, #0b1120 0%, #1e1b4b 50%, #0f2b38 100%);
        border-radius: 20px;
        padding: 2.2rem 2.6rem;
        color: #ffffff;
        margin-bottom: 1.8rem;
        box-shadow: 0 12px 32px -6px rgba(7, 10, 19, 0.45);
        display: flex;
        align-items: center;
        justify-content: space-between;
        border: 1px solid rgba(45, 212, 191, 0.2);
        position: relative;
        overflow: hidden;
    }
    .hero-banner::after {
        content: '';
        position: absolute;
        top: -40%;
        right: 10%;
        width: 300px;
        height: 300px;
        background: radial-gradient(circle, rgba(20, 184, 166, 0.18) 0%, rgba(79, 70, 229, 0) 70%);
        border-radius: 50%;
        pointer-events: none;
    }
    .hero-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(20, 184, 166, 0.15);
        border: 1px solid rgba(45, 212, 191, 0.35);
        color: #5eead4;
        padding: 4px 12px;
        border-radius: 9999px;
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 0.5px;
        text-transform: uppercase;
        margin-bottom: 0.7rem;
    }
    .hero-title {
        font-size: 2.2rem;
        font-weight: 800;
        margin: 0;
        letter-spacing: -0.02em;
        color: #ffffff !important;
    }
    .hero-title span {
        background: linear-gradient(90deg, #67e8f9 0%, #a5b4fc 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .hero-desc {
        color: #cbd5e1;
        font-size: 1.02rem;
        margin: 0.5rem 0 0 0;
        max-width: 720px;
        line-height: 1.5;
    }
    .hero-artwork {
        display: flex;
        align-items: center;
        justify-content: center;
        filter: drop-shadow(0 10px 20px rgba(0, 0, 0, 0.3));
        animation: floatArt 4.5s ease-in-out infinite;
    }
    @keyframes floatArt {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-7px); }
    }

    /* Feature Cards Grid on Welcome */
    .feature-overview-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
        gap: 1.2rem;
        margin-bottom: 1.8rem;
    }
    .overview-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 1.4rem 1.5rem;
        box-shadow: 0 4px 14px rgba(15, 23, 42, 0.04);
        transition: all 0.25s ease;
        position: relative;
    }
    .overview-card:hover {
        transform: translateY(-3px);
        border-color: #2dd4bf;
        box-shadow: 0 10px 24px -4px rgba(20, 184, 166, 0.15);
    }
    .overview-icon {
        font-size: 1.6rem;
        margin-bottom: 0.5rem;
        display: inline-block;
    }
    .overview-title {
        font-size: 1.1rem;
        font-weight: 700;
        color: #0f172a;
        margin: 0 0 0.3rem 0;
    }
    .overview-desc {
        font-size: 0.88rem;
        color: #64748b;
        margin: 0;
        line-height: 1.45;
    }

    /* Output Card */
    .output-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-top: 3px solid #14b8a6;
        border-radius: 16px;
        padding: 1.6rem 1.8rem;
        margin-top: 1.3rem;
        box-shadow: 0 8px 24px -4px rgba(15, 23, 42, 0.06);
    }
    .output-badge {
        font-size: 0.76rem;
        font-weight: 700;
        padding: 3px 10px;
        border-radius: 9999px;
        background: #f0fdfa;
        color: #0d9488;
        border: 1px solid #ccfbf1;
        letter-spacing: 0.4px;
        text-transform: uppercase;
    }

    /* Compact Loading Animation */
    .compact-loader {
        display: inline-flex;
        align-items: center;
        gap: 10px;
        background: #f0fdfa;
        border: 1px solid #99f6e4;
        padding: 0.65rem 1.1rem;
        border-radius: 10px;
        color: #0f766e;
        font-weight: 600;
        font-size: 0.88rem;
        margin: 1rem 0;
    }
    .loader-dots {
        display: flex;
        gap: 5px;
    }
    .loader-dot {
        width: 8px;
        height: 8px;
        background: #14b8a6;
        border-radius: 50%;
        animation: pulseDots 1.2s infinite ease-in-out both;
    }
    .loader-dot:nth-child(1) { animation-delay: -0.32s; }
    .loader-dot:nth-child(2) { animation-delay: -0.16s; }
    @keyframes pulseDots {
        0%, 80%, 100% { transform: scale(0.3); opacity: 0.4; }
        40% { transform: scale(1); opacity: 1; }
    }

    /* Sidebar History Items */
    .sidebar-history-card {
        background: rgba(255, 255, 255, 0.04);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 10px;
        padding: 0.65rem 0.8rem;
        margin-bottom: 0.5rem;
        cursor: pointer;
        transition: all 0.2s ease;
    }
    .sidebar-history-card:hover {
        background: rgba(45, 212, 191, 0.1);
        border-color: rgba(45, 212, 191, 0.3);
    }
    .sidebar-history-title {
        font-size: 0.82rem;
        font-weight: 600;
        color: #f1f5f9;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }
    .sidebar-history-sub {
        font-size: 0.72rem;
        color: #94a3b8;
        display: flex;
        justify-content: space-between;
        margin-top: 2px;
    }

    /* Modern Buttons */
    div.stButton > button {
        border-radius: 10px !important;
        font-weight: 600 !important;
        transition: all 0.2s ease !important;
    }
    div.stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 16px rgba(20, 184, 166, 0.25) !important;
    }

    @media (max-width: 768px) {
        .hero-banner {
            flex-direction: column-reverse;
            text-align: center;
            padding: 1.6rem 1.2rem;
            gap: 1rem;
        }
        .hero-title {
            font-size: 1.8rem;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# =====================================================================
# SIDEBAR - PRIVACY-CONSCIOUS & STREAMLINED
# =====================================================================
with st.sidebar:
    # Minimalist Branding
    st.markdown(
        """
        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 1.2rem;">
            <svg width="34" height="34" viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg">
                <rect width="64" height="64" rx="14" fill="#14b8a6" />
                <path d="M16 42C16 42 22 39 32 39C42 39 48 42 48 42V20C48 20 42 17 32 17C22 17 16 20 16 20V42Z" stroke="#070a13" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M32 17V39" stroke="#070a13" stroke-width="3" stroke-linecap="round"/>
                <circle cx="32" cy="24" r="3" fill="#ffffff" />
            </svg>
            <div>
                <h3 style="margin: 0; font-size: 1.15rem; font-weight: 700; color: #f8fafc;">Study Assistant</h3>
                <span style="font-size: 0.74rem; color: #2dd4bf; font-weight: 600;">High-Speed AI</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Primary Navigation (Clean & uncluttered)
    nav_option = st.radio(
        "Navigation",
        options=["⚡ Workspace", f"🕒 History ({len(st.session_state.history)})"],
        label_visibility="collapsed",
    )
    st.session_state.nav_view = "History" if "History" in nav_option else "Workspace"

    st.markdown("<hr style='margin: 1.2rem 0; border: none; border-top: 1px solid rgba(255,255,255,0.08);'/>", unsafe_allow_html=True)

    # Sidebar History Quick-Access
    st.markdown("<p style='font-size: 0.78rem; font-weight: 700; letter-spacing: 0.5px; color: #94a3b8; text-transform: uppercase; margin-bottom: 0.5rem;'>RECENT SESSIONS</p>", unsafe_allow_html=True)

    if not st.session_state.history:
        st.markdown("<p style='font-size: 0.8rem; color: #64748b;'>No study sessions recorded yet.</p>", unsafe_allow_html=True)
    else:
        for idx, item in enumerate(st.session_state.history[:5]):
            if st.button(f"{item['icon']} {item['title']}", key=f"sb_hist_{item['id']}", use_container_width=True):
                st.session_state.selected_history_id = item["id"]
                st.session_state.nav_view = "History"
                st.rerun()

        if len(st.session_state.history) > 5:
            st.caption(f"+ {len(st.session_state.history) - 5} more in History tab")

    st.markdown("<hr style='margin: 1.2rem 0; border: none; border-top: 1px solid rgba(255,255,255,0.08);'/>", unsafe_allow_html=True)

    # Privacy-Conscious Collapsible Settings (CLOSED BY DEFAULT)
    with st.expander("⚙️ Settings & Credentials", expanded=False):
        st.caption("Credentials remain masked and are never displayed or logged.")
        
        provider = st.selectbox(
            "Provider",
            options=["Google Gemini", "OpenAI"],
            index=0,
            key="cfg_provider"
        )

        env_key_name = "GEMINI_API_KEY" if provider == "Google Gemini" else "OPENAI_API_KEY"
        env_val = os.getenv(env_key_name, "")

        user_api_key = st.text_input(
            f"{provider} API Key",
            value=env_val,
            type="password",
            placeholder="Key is securely masked",
            help=f"Loaded securely from {env_key_name} if configured in .env."
        )

        # Fast model options (cached discovery)
        if provider == "Google Gemini":
            model_options = fetch_cached_gemini_models(user_api_key)
            try:
                default_m = resolve_active_gemini_model(user_api_key)
            except RuntimeError as err:
                st.warning(f"⚠️ {str(err)}")
                default_m = model_options[0] if model_options else PREFERRED_GEMINI_MODEL

            if default_m and default_m not in model_options:
                model_options.insert(0, default_m)
        else:
            model_options = ["gpt-4o-mini", "gpt-4o"]
            default_m = "gpt-4o-mini"

        m_idx = model_options.index(default_m) if default_m in model_options else 0
        selected_model = st.selectbox("Model", options=model_options, index=m_idx)

    # Fallback resolution if expander wasn't opened
    if "user_api_key" not in locals():
        provider = "Google Gemini"
        env_key_name = "GEMINI_API_KEY"
        user_api_key = os.getenv("GEMINI_API_KEY", "")
        try:
            selected_model = resolve_active_gemini_model(user_api_key)
        except RuntimeError:
            selected_model = PREFERRED_GEMINI_MODEL


# =====================================================================
# WELCOME HERO BANNER WITH CUSTOM SVG ARTWORK
# =====================================================================
st.markdown(
    """
    <div class="hero-banner">
        <div style="z-index: 1;">
            <div class="hero-badge">⚡ High-Speed Learning Intelligence</div>
            <h1 class="hero-title">AI Study <span>Assistant</span></h1>
            <p class="hero-desc">Accelerate your study workflow with concise conceptual explanations, rapid lecture note synthesis, and exam-focused practice quizzes.</p>
        </div>
        <div class="hero-artwork">
            <svg width="92" height="92" viewBox="0 0 80 80" fill="none" xmlns="http://www.w3.org/2000/svg">
                <!-- Base Rounded Frame -->
                <rect width="80" height="80" rx="20" fill="url(#hero-art-grad)" />
                <rect x="1" y="1" width="78" height="78" rx="19" stroke="url(#hero-art-border)" stroke-width="1.5" />
                <!-- Holographic Open Book -->
                <path d="M20 54C20 54 28 50 40 50C52 50 60 54 60 54V26C60 26 52 22 40 22C28 22 20 26 20 26V54Z" stroke="#ffffff" stroke-width="2.8" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M40 22V50" stroke="#ffffff" stroke-width="2.8" stroke-linecap="round"/>
                <!-- Synaptic Neural Rays -->
                <circle cx="30" cy="35" r="3" fill="#2dd4bf" />
                <circle cx="50" cy="35" r="3" fill="#2dd4bf" />
                <circle cx="40" cy="29" r="3.5" fill="#fde047" />
                <path d="M30 35L40 29L50 35" stroke="#2dd4bf" stroke-width="1.8" stroke-dasharray="2 2"/>
                <!-- Glowing Particle Burst -->
                <path d="M40 12L41.5 16.5L46 18L41.5 19.5L40 24L38.5 19.5L34 18L38.5 16.5L40 12Z" fill="#5eead4"/>
                <defs>
                    <linearGradient id="hero-art-grad" x1="0" y1="0" x2="80" y2="80" gradientUnits="userSpaceOnUse">
                        <stop stop-color="#0f172a"/>
                        <stop offset="0.5" stop-color="#1e1b4b"/>
                        <stop offset="1" stop-color="#0d9488"/>
                    </linearGradient>
                    <linearGradient id="hero-art-border" x1="0" y1="0" x2="80" y2="80" gradientUnits="userSpaceOnUse">
                        <stop stop-color="#2dd4bf"/>
                        <stop offset="1" stop-color="#818cf8"/>
                    </linearGradient>
                </defs>
            </svg>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# =====================================================================
# VIEW ROUTING: WORKSPACE vs HISTORY
# =====================================================================

if st.session_state.nav_view == "History":
    # -----------------------------------------------------------------
    # HISTORY VIEW
    # -----------------------------------------------------------------
    col_h_title, col_h_clear = st.columns([3, 1])
    with col_h_title:
        st.markdown("### 🕒 Study Session History")
        st.caption("Review, export, or replay past explanations and practice quizzes.")

    with col_h_clear:
        if st.session_state.history:
            if not st.session_state.confirm_clear_history:
                if st.button("🗑️ Clear History", type="secondary", use_container_width=True):
                    st.session_state.confirm_clear_history = True
                    st.rerun()
            else:
                st.warning("Confirm delete?")
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("Yes", type="primary", use_container_width=True):
                        st.session_state.history = []
                        st.session_state.selected_history_id = None
                        st.session_state.confirm_clear_history = False
                        st.rerun()
                with c2:
                    if st.button("Cancel", type="secondary", use_container_width=True):
                        st.session_state.confirm_clear_history = False
                        st.rerun()

    if not st.session_state.history:
        st.markdown(
            """
            <div style="text-align: center; padding: 3.5rem 2rem; background: #ffffff; border: 2px dashed #cbd5e1; border-radius: 16px; margin-top: 1rem;">
                <span style="font-size: 2.6rem;">📚</span>
                <h4 style="color: #1e293b; margin: 0.6rem 0 0.3rem 0;">No Stored Sessions Yet</h4>
                <p style="color: #64748b; font-size: 0.9rem; margin: 0;">Your queries and practice quizzes will automatically appear here as you study.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        col_list, col_view = st.columns([1.1, 1.9])

        if not st.session_state.selected_history_id and st.session_state.history:
            st.session_state.selected_history_id = st.session_state.history[0]["id"]

        with col_list:
            st.markdown("##### 📋 Activity Log")
            for item in st.session_state.history:
                is_sel = (item["id"] == st.session_state.selected_history_id)
                card_border = "#14b8a6" if is_sel else "#e2e8f0"
                card_bg = "#f0fdfa" if is_sel else "#ffffff"

                st.markdown(
                    f"""
                    <div style="border: 2px solid {card_border}; background: {card_bg}; border-radius: 12px; padding: 0.8rem 1rem; margin-bottom: 0.5rem; transition: all 0.2s;">
                        <div style="display: flex; justify-content: space-between; font-size: 0.74rem; color: #64748b; margin-bottom: 0.2rem;">
                            <span>{item['icon']} <b>{item['task_type']}</b></span>
                            <span>{item['timestamp']}</span>
                        </div>
                        <div style="font-size: 0.88rem; font-weight: 600; color: #0f172a; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
                            {item['title']}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                if st.button(f"Open #{item['id']}", key=f"hist_open_{item['id']}", use_container_width=True):
                    st.session_state.selected_history_id = item["id"]
                    st.rerun()

        with col_view:
            selected_item = next((i for i in st.session_state.history if i["id"] == st.session_state.selected_history_id), None)
            if selected_item:
                st.markdown(
                    f"""
                    <div class="output-card" style="margin-top: 0;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.8rem;">
                            <span class="output-badge">{selected_item['task_type']}</span>
                            <span style="font-size: 0.78rem; color: #64748b;">{selected_item['timestamp']}</span>
                        </div>
                        <h4 style="margin: 0 0 0.8rem 0; color: #0f172a;">{selected_item['title']}</h4>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                with st.expander("🔍 View Source Material / Input", expanded=False):
                    st.code(selected_item["input_payload"], language="text")

                st.markdown("##### 📖 Stored Result")
                st.markdown(selected_item["output_result"])

                st.download_button(
                    label="📥 Export Result (.md)",
                    data=selected_item["output_result"],
                    file_name=f"study_result_{selected_item['id']}.md",
                    mime="text/markdown",
                    use_container_width=True,
                    key=f"dl_stored_{selected_item['id']}"
                )


else:
    # -----------------------------------------------------------------
    # WORKSPACE VIEW: FEATURE OVERVIEW CARDS & WORKSPACE TABS
    # -----------------------------------------------------------------
    
    # 3 Coordinated Feature Cards
    st.markdown(
        """
        <div class="feature-overview-grid">
            <div class="overview-card">
                <span class="overview-icon">💡</span>
                <h4 class="overview-title">Ask a Question</h4>
                <p class="overview-desc">Concise conceptual breakdown, key steps, and memorable real-world analogies.</p>
            </div>
            <div class="overview-card">
                <span class="overview-icon">📝</span>
                <h4 class="overview-title">Summarize Notes</h4>
                <p class="overview-desc">Condense raw lecture transcripts and chapter excerpts into structured revision points.</p>
            </div>
            <div class="overview-card">
                <span class="overview-icon">🎯</span>
                <h4 class="overview-title">Generate Quiz</h4>
                <p class="overview-desc">High-yield practice MCQs or conceptual review questions with instant answer keys.</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    tab_ask, tab_summary, tab_quiz = st.tabs(
        ["💡 Ask a Question", "📝 Summarize Notes", "🎯 Generate Quiz"]
    )

    # -----------------------------------------------------------------
    # TAB 1: ASK A QUESTION
    # -----------------------------------------------------------------
    with tab_ask:
        col_q1, col_q2 = st.columns([1, 2])
        with col_q1:
            subject = st.text_input(
                "Subject / Context (Optional)",
                placeholder="e.g. Operating Systems, ML",
                key="wk_subject"
            )
        with col_q2:
            quick_q = st.selectbox(
                "⚡ Quick Fill Suggested Topics",
                options=[
                    "— Select a sample doubt —",
                    "What is the difference between Process and Thread in OS?",
                    "Explain Gradient Descent in Machine Learning with a simple analogy.",
                    "How does Dijkstra's Algorithm compute shortest paths in graphs?",
                    "Explain Public Key vs Private Key Cryptography simply."
                ],
                key="wk_quick_q"
            )

        default_q_val = quick_q if quick_q != "— Select a sample doubt —" else ""
        user_question = st.text_area(
            "Your Question:",
            value=default_q_val,
            placeholder="Type your study doubt or concept here (e.g. Explain Virtual Memory and Paging in Operating Systems)...",
            height=110,
            key="wk_question_text"
        )

        col_ask_btn, col_ask_space = st.columns([1.2, 3])
        with col_ask_btn:
            ask_pressed = st.button("✨ Explain Concept", type="primary", use_container_width=True)

        if ask_pressed:
            if not user_api_key:
                st.error("⚠️ Please configure an API key in '⚙️ Settings & Credentials' (sidebar) to proceed.")
            elif not user_question.strip():
                st.warning("Please type a question before submitting.")
            else:
                loader = st.empty()
                loader.markdown(
                    """
                    <div class="compact-loader">
                        <div class="loader-dots">
                            <span class="loader-dot"></span>
                            <span class="loader-dot"></span>
                            <span class="loader-dot"></span>
                        </div>
                        <span>Formulating high-yield conceptual explanation...</span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                try:
                    response = route_task(
                        task_type="ask",
                        payload={"question": user_question, "subject": subject},
                        provider=provider,
                        model=selected_model,
                        api_key=user_api_key
                    )
                finally:
                    loader.empty()  # Stops immediately when request finishes or fails

                if response["status"] == "success":
                    add_to_history(
                        task_type="Ask a Question",
                        icon="💡",
                        title=user_question,
                        subtitle=subject or "General Concept",
                        input_payload=f"Subject: {subject}\nQuestion: {user_question}",
                        output_result=response["data"],
                        provider=provider,
                        model=selected_model
                    )

                    st.markdown(
                        """
                        <div class="output-card">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.8rem;">
                                <span class="output-badge">Conceptual Breakdown</span>
                                <span style="font-size: 0.78rem; color: #0d9488; font-weight: 600;">✓ Ready</span>
                            </div>
                        """,
                        unsafe_allow_html=True,
                    )
                    st.markdown(response["data"])
                    st.markdown("</div>", unsafe_allow_html=True)

                    st.download_button(
                        label="📥 Download Answer (.md)",
                        data=response["data"],
                        file_name="concept_explanation.md",
                        mime="text/markdown"
                    )
                else:
                    st.error(response["message"])

    # -----------------------------------------------------------------
    # TAB 2: SUMMARIZE NOTES
    # -----------------------------------------------------------------
    with tab_summary:
        col_s_left, col_s_right = st.columns([2.3, 1])

        with col_s_right:
            summary_mode = st.radio(
                "Summary Mode",
                options=["Standard", "Quick Bullets", "Key Definitions & Terms"],
                index=0
            )
            load_sample = st.button("📄 Load Sample Notes", use_container_width=True)

        sample_text = (
            "Artificial Intelligence agents perceive their environment through sensors and act upon it using actuators. "
            "A rational agent is one that selects an action expected to maximize its performance measure, based on the evidence "
            "provided by the percept sequence and built-in knowledge. Agents can be categorized into five basic types based on "
            "their architecture: Simple Reflex Agents (condition-action rules), Model-Based Reflex Agents (internal state to track "
            "unseen aspects), Goal-Based Agents (deliberate actions to achieve desired states), Utility-Based Agents (maximize a "
            "preference utility function), and Learning Agents (capable of learning from feedback to improve performance over time)."
        )

        with col_s_left:
            notes_input = st.text_area(
                "Paste Study Notes / Textbook Text:",
                value=sample_text if load_sample else "",
                placeholder="Paste your raw lecture notes, article excerpts, or book paragraphs here...",
                height=160,
                key="wk_notes_text"
            )
            word_count = len(notes_input.split()) if notes_input else 0
            st.caption(f"Word count: {word_count} words")

        col_sum_btn, col_sum_space = st.columns([1.2, 3])
        with col_sum_btn:
            sum_pressed = st.button("✨ Summarize Notes", type="primary", use_container_width=True)

        if sum_pressed:
            if not user_api_key:
                st.error("⚠️ Please configure an API key in '⚙️ Settings & Credentials' (sidebar) to proceed.")
            elif not notes_input.strip():
                st.warning("Please paste notes before submitting.")
            else:
                loader = st.empty()
                loader.markdown(
                    """
                    <div class="compact-loader">
                        <div class="loader-dots">
                            <span class="loader-dot"></span>
                            <span class="loader-dot"></span>
                            <span class="loader-dot"></span>
                        </div>
                        <span>Extracting key takeaways & definitions...</span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                try:
                    response = route_task(
                        task_type="summarize",
                        payload={"notes": notes_input, "mode": summary_mode},
                        provider=provider,
                        model=selected_model,
                        api_key=user_api_key
                    )
                finally:
                    loader.empty()

                if response["status"] == "success":
                    title_preview = notes_input.strip().split(".")[0] or "Study Notes Summary"
                    add_to_history(
                        task_type="Summarize Notes",
                        icon="📝",
                        title=title_preview,
                        subtitle=f"{summary_mode} Mode ({word_count} words)",
                        input_payload=notes_input,
                        output_result=response["data"],
                        provider=provider,
                        model=selected_model
                    )

                    st.markdown(
                        """
                        <div class="output-card">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.8rem;">
                                <span class="output-badge">Executive Summary</span>
                                <span style="font-size: 0.78rem; color: #0d9488; font-weight: 600;">✓ Synthesized</span>
                            </div>
                        """,
                        unsafe_allow_html=True,
                    )
                    st.markdown(response["data"])
                    st.markdown("</div>", unsafe_allow_html=True)

                    st.download_button(
                        label="📥 Download Summary (.md)",
                        data=response["data"],
                        file_name="notes_summary.md",
                        mime="text/markdown"
                    )
                else:
                    st.error(response["message"])

    # -----------------------------------------------------------------
    # TAB 3: GENERATE PRACTICE QUIZ
    # -----------------------------------------------------------------
    with tab_quiz:
        col_q1, col_q2, col_q3 = st.columns([1.5, 1.5, 1.2])
        with col_q1:
            quiz_type = st.selectbox(
                "Quiz Format",
                options=["Multiple Choice", "Conceptual Short Answer"],
                index=0,
                key="wk_quiz_type"
            )
        with col_q2:
            num_questions = st.slider("Number of Questions", min_value=1, max_value=6, value=3)
        with col_q3:
            st.write("")
            st.write("")
            load_sample_quiz = st.button("🎯 Sample Topic", use_container_width=True)

        sample_quiz_topic = "Database Normalization (1NF, 2NF, 3NF, BCNF) and Functional Dependencies"
        quiz_topic_input = st.text_area(
            "Topic or Study Passage for Quiz Generation:",
            value=sample_quiz_topic if load_sample_quiz else "",
            placeholder="e.g. TCP vs UDP, OSI 7-Layer Model, or paste your lecture content...",
            height=110,
            key="wk_quiz_topic"
        )

        col_quiz_btn, col_quiz_space = st.columns([1.2, 3])
        with col_quiz_btn:
            quiz_pressed = st.button("🎲 Generate Practice Quiz", type="primary", use_container_width=True)

        if quiz_pressed:
            if not user_api_key:
                st.error("⚠️ Please configure an API key in '⚙️ Settings & Credentials' (sidebar) to proceed.")
            elif not quiz_topic_input.strip():
                st.warning("Please provide a topic or notes to generate quiz questions.")
            else:
                loader = st.empty()
                loader.markdown(
                    f"""
                    <div class="compact-loader">
                        <div class="loader-dots">
                            <span class="loader-dot"></span>
                            <span class="loader-dot"></span>
                            <span class="loader-dot"></span>
                        </div>
                        <span>Crafting {num_questions} {quiz_type} questions with explanations...</span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                try:
                    response = route_task(
                        task_type="quiz",
                        payload={
                            "topic_or_notes": quiz_topic_input,
                            "num_questions": num_questions,
                            "quiz_type": quiz_type
                        },
                        provider=provider,
                        model=selected_model,
                        api_key=user_api_key
                    )
                finally:
                    loader.empty()

                if response["status"] == "success":
                    add_to_history(
                        task_type="Practice Quiz",
                        icon="🎯",
                        title=quiz_topic_input.strip().split("\n")[0] or "Practice Quiz",
                        subtitle=f"{num_questions} Questions ({quiz_type})",
                        input_payload=f"Format: {quiz_type}\nCount: {num_questions}\nMaterial: {quiz_topic_input}",
                        output_result=response["data"],
                        provider=provider,
                        model=selected_model
                    )

                    st.markdown(
                        """
                        <div class="output-card">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.8rem;">
                                <span class="output-badge">Practice Quiz</span>
                                <span style="font-size: 0.78rem; color: #0d9488; font-weight: 600;">✓ Generated</span>
                            </div>
                        """,
                        unsafe_allow_html=True,
                    )
                    st.markdown(response["data"])
                    st.markdown("</div>", unsafe_allow_html=True)

                    st.download_button(
                        label="📥 Download Quiz (.md)",
                        data=response["data"],
                        file_name="practice_quiz.md",
                        mime="text/markdown"
                    )
                else:
                    st.error(response["message"])
