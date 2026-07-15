"""
InterviewAce AI — Main Application Entry Point
================================================
Run with:  streamlit run app.py
"""

import sys
import os
import logging

import streamlit as st

# ── Make sure project root is on the path ────────────────────────────────────
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# ── Logging configuration ────────────────────────────────────────────────────
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
#  Page Configuration  (must be first Streamlit call)
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="InterviewAce AI",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": "https://github.com/your-repo/interviewace-ai",
        "Report a bug": "https://github.com/your-repo/interviewace-ai/issues",
        "About": (
            "**InterviewAce AI** — AI-powered Interview Trainer\n\n"
            "Built with IBM Granite via IBM watsonx.ai | IBM SkillsBuild Internship Project"
        ),
    },
)


# ─────────────────────────────────────────────────────────────────────────────
#  Custom CSS
# ─────────────────────────────────────────────────────────────────────────────
def inject_css():
    st.markdown(
        """
        <style>
        /* ── Global ── */
        .main .block-container {
            padding-top: 1.5rem;
            padding-bottom: 2rem;
            max-width: 1100px;
        }

        /* ── Sidebar ── */
        [data-testid="stSidebar"] {
            background-color: #0f1729;
        }
        [data-testid="stSidebar"] * {
            color: #e8eaf0 !important;
        }
        [data-testid="stSidebar"] .stRadio label {
            font-size: 0.97rem;
            padding: 0.3rem 0;
        }

        /* ── Hero Banner ── */
        .hero-banner {
            background: linear-gradient(135deg, #0f1729 0%, #1a2a6c 50%, #0b5394 100%);
            border-radius: 14px;
            padding: 2.2rem 2rem 1.8rem;
            margin-bottom: 1.5rem;
            color: white;
            text-align: center;
        }
        .hero-banner h1 {
            font-size: 2.4rem;
            font-weight: 800;
            letter-spacing: -0.5px;
            margin: 0 0 0.3rem 0;
        }
        .hero-banner p {
            font-size: 1.05rem;
            opacity: 0.88;
            margin: 0;
        }
        .hero-badge {
            display: inline-block;
            background: rgba(255,255,255,0.15);
            border: 1px solid rgba(255,255,255,0.3);
            border-radius: 20px;
            padding: 0.3rem 1rem;
            font-size: 0.82rem;
            margin-top: 0.9rem;
            letter-spacing: 0.3px;
        }

        /* ── Feature Cards ── */
        .feature-card {
            background: #f8f9fc;
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            padding: 1.4rem 1.2rem;
            height: 100%;
            transition: border-color 0.2s;
        }
        .feature-card:hover {
            border-color: #3b82f6;
        }
        .feature-card h4 {
            font-size: 1.05rem;
            font-weight: 700;
            margin: 0.4rem 0 0.5rem 0;
            color: #1e293b;
        }
        .feature-card p {
            font-size: 0.88rem;
            color: #475569;
            margin: 0;
            line-height: 1.5;
        }
        .feature-icon {
            font-size: 1.8rem;
        }

        /* ── Status badges ── */
        .status-ok {
            background: #dcfce7;
            color: #166534;
            padding: 0.2rem 0.7rem;
            border-radius: 12px;
            font-size: 0.8rem;
            font-weight: 600;
        }
        .status-err {
            background: #fee2e2;
            color: #991b1b;
            padding: 0.2rem 0.7rem;
            border-radius: 12px;
            font-size: 0.8rem;
            font-weight: 600;
        }

        /* ── Divider ── */
        hr {
            margin: 1rem 0;
            border: 0;
            border-top: 1px solid #e2e8f0;
        }

        /* ── Button overrides ── */
        .stButton > button[kind="primary"] {
            background-color: #1a2a6c;
            border: none;
            font-weight: 600;
        }
        .stButton > button[kind="primary"]:hover {
            background-color: #0b5394;
        }

        /* ── Footer ── */
        .app-footer {
            text-align: center;
            color: #94a3b8;
            font-size: 0.78rem;
            padding: 1.5rem 0 0.5rem;
            border-top: 1px solid #e2e8f0;
            margin-top: 2rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────────────────────────────────────────
#  Sidebar Navigation
# ─────────────────────────────────────────────────────────────────────────────
def render_sidebar() -> str:
    """Render sidebar and return the selected page name."""
    with st.sidebar:
        st.markdown(
            """
            <div style="text-align:center; padding: 1rem 0 0.5rem;">
                <div style="font-size:2.2rem;">🎯</div>
                <div style="font-size:1.15rem; font-weight:800; letter-spacing:0.3px;">
                    InterviewAce AI
                </div>
                <div style="font-size:0.72rem; opacity:0.65; margin-top:0.2rem;">
                    Powered by IBM Granite
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.divider()

        st.markdown("**Navigation**")
        page = st.radio(
            "Navigation",
            options=[
                "🏠  Home",
                "🎯  Interview Preparation",
                "📄  Resume Review",
                "🗺️  Learning Roadmap",
                "🧭  Career Guidance",
            ],
            label_visibility="collapsed",
        )

        st.divider()

        # ── Connection Status ──────────────────────────────────────────────
        st.markdown("**Connection Status**")
        if st.button("🔌 Check IBM Watsonx", use_container_width=True):
            with st.spinner("Checking..."):
                from core.granite_client import check_connection
                ok, msg = check_connection()
                if ok:
                    st.success(msg)
                else:
                    st.error(msg)

        st.divider()

        # ── Info ────────────────────────────────────────────────────────────
        st.markdown(
            """
            <div style="font-size:0.78rem; opacity:0.7; line-height:1.6;">
            <strong>IBM SkillsBuild Internship</strong><br>
            Interview Trainer Agent<br><br>
            🤖 IBM Granite 3 (8B Instruct)<br>
            🔍 TF-IDF RAG Retrieval<br>
            ☁️ IBM watsonx.ai Cloud
            </div>
            """,
            unsafe_allow_html=True,
        )

    return page


# ─────────────────────────────────────────────────────────────────────────────
#  Home Page
# ─────────────────────────────────────────────────────────────────────────────
def render_home():
    """Render the application home / landing page."""

    # Hero banner
    st.markdown(
        """
        <div class="hero-banner">
            <h1>🎯 InterviewAce AI</h1>
            <p>Your AI-powered interview trainer and career mentor</p>
            <div class="hero-badge">⚡ Powered by IBM Granite via IBM watsonx.ai</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Tagline
    st.markdown(
        "**InterviewAce AI** uses IBM Granite large language models with a built-in "
        "RAG (Retrieval-Augmented Generation) layer to deliver personalized, role-specific "
        "interview coaching, resume feedback, and career guidance — all in one place."
    )

    st.divider()

    # ── Feature Cards ──────────────────────────────────────────────────────────
    st.markdown("### 🛠️ What Can InterviewAce Do For You?")

    feature_data = [
        {
            "icon": "🎯",
            "title": "Interview Preparation",
            "desc": (
                "Generate tailored interview questions, model answers (STAR format), "
                "and preparation tips for your specific role and experience level."
            ),
        },
        {
            "icon": "📄",
            "title": "Resume Review",
            "desc": (
                "Get an honest AI critique of your resume with specific rewrites, "
                "ATS optimization tips, and an overall score."
            ),
        },
        {
            "icon": "🗺️",
            "title": "Learning Roadmap",
            "desc": (
                "Receive a phase-by-phase learning plan with specific resources, "
                "IBM SkillsBuild recommendations, and a 30-day quick-start plan."
            ),
        },
        {
            "icon": "🧭",
            "title": "Career Guidance",
            "desc": (
                "Ask any career question and get honest, actionable advice — "
                "from role transitions to salary negotiation strategies."
            ),
        },
    ]

    cols = st.columns(4)
    for i, feat in enumerate(feature_data):
        with cols[i]:
            st.markdown(
                f"""
                <div class="feature-card">
                    <div class="feature-icon">{feat["icon"]}</div>
                    <h4>{feat["title"]}</h4>
                    <p>{feat["desc"]}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.divider()

    # ── How It Works ───────────────────────────────────────────────────────────
    st.markdown("### ⚙️ How It Works")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(
            "**1. You Provide Your Profile**\n\n"
            "Enter your name, target role, experience level, and skills. "
            "Optionally paste your resume text."
        )
    with col2:
        st.markdown(
            "**2. RAG Retrieves Context**\n\n"
            "The RAG engine searches the knowledge base for the most relevant "
            "interview guides, HR tips, and role-specific content."
        )
    with col3:
        st.markdown(
            "**3. IBM Granite Generates**\n\n"
            "The retrieved context + your profile are sent to IBM Granite, "
            "which generates a fully personalized, actionable response."
        )

    st.divider()

    # ── Quick Start ────────────────────────────────────────────────────────────
    st.markdown("### 🚀 Quick Start")
    st.markdown(
        "1. **Select a section** from the left sidebar.\n"
        "2. **Fill in your profile** (role, experience level, skills).\n"
        "3. **Click generate** — IBM Granite will respond in seconds.\n"
        "4. **Download** your personalized guide as a text file."
    )

    st.info(
        "🔑 **First-time setup:** Copy `.env.example` to `.env` and add your IBM API Key, "
        "Project ID, and watsonx URL. Click **Check IBM Watsonx** in the sidebar to verify."
    )

    st.divider()

    # ── Tech Stack ─────────────────────────────────────────────────────────────
    st.markdown("### 🏗️ Technology Stack")

    tech_cols = st.columns(4)
    tech_items = [
        ("🐍", "Python + Streamlit", "UI & App Framework"),
        ("🤖", "IBM Granite 3 8B Instruct", "Core Language Model"),
        ("☁️", "IBM watsonx.ai", "Enterprise AI Platform"),
        ("🔍", "TF-IDF RAG", "Retrieval-Augmented Generation"),
    ]
    for i, (icon, name, desc) in enumerate(tech_items):
        with tech_cols[i]:
            st.markdown(f"**{icon} {name}**\n\n{desc}")

    # ── Footer ────────────────────────────────────────────────────────────────
    st.markdown(
        """
        <div class="app-footer">
            InterviewAce AI — IBM SkillsBuild Internship Project &nbsp;|&nbsp;
            Built with IBM Granite via IBM watsonx.ai &nbsp;|&nbsp;
            &copy; 2025
        </div>
        """,
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────────────────────────────────────────
#  Main Router
# ─────────────────────────────────────────────────────────────────────────────
def main():
    inject_css()

    # Pre-load RAG index in the background on first run
    if "rag_loaded" not in st.session_state:
        with st.spinner("🔍 Loading knowledge base..."):
            try:
                from rag.retriever import get_retriever
                get_retriever()  # triggers index build and caches it
                st.session_state["rag_loaded"] = True
            except Exception as e:
                logger.warning("RAG pre-load failed: %s", e)
                st.session_state["rag_loaded"] = False

    page = render_sidebar()

    # Route to the correct page
    if "Home" in page:
        render_home()

    elif "Interview Preparation" in page:
        from pages.interview_prep import render
        render()

    elif "Resume Review" in page:
        from pages.resume_review import render
        render()

    elif "Learning Roadmap" in page:
        from pages.learning_roadmap import render
        render()

    elif "Career Guidance" in page:
        from pages.career_guidance import render
        render()


if __name__ == "__main__":
    main()
