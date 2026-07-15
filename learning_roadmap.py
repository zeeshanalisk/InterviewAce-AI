"""
InterviewAce AI — Learning Roadmap Page
"""

import streamlit as st
from core.granite_client import generate_response
from core.prompts import build_roadmap_prompt
from rag.retriever import retrieve_for_role
from utils.helpers import (
    validate_required_fields,
    format_skills_list,
    EXPERIENCE_LEVELS,
    COMMON_JOB_ROLES,
    get_default_skills,
    log_interaction,
    clean_granite_response,
    experience_to_label,
)


def render():
    """Render the Learning Roadmap page."""

    st.markdown("## 🗺️ Learning Roadmap")
    st.markdown(
        "Get a **personalized, phase-by-phase learning plan** to reach your target role. "
        "Includes specific resources, IBM SkillsBuild recommendations, "
        "and a 30-day quick-start action plan."
    )

    st.divider()

    # ── Input Form ────────────────────────────────────────────────────────────
    st.markdown("### 🎯 Your Goal")

    col1, col2 = st.columns([1, 1])

    with col1:
        job_role_option = st.selectbox(
            "Target Role",
            options=COMMON_JOB_ROLES,
            key="roadmap_role_select",
        )
        job_role = st.text_input(
            "Custom Role (optional)",
            value="" if job_role_option == "Other (type below)" else job_role_option,
            key="roadmap_role_input",
        )
        experience_level = st.selectbox(
            "Current Experience Level",
            options=EXPERIENCE_LEVELS,
            key="roadmap_exp_level",
        )

    with col2:
        default_skills = get_default_skills(job_role or job_role_option)
        skills = st.text_input(
            "Skills You Already Have",
            value=default_skills,
            placeholder="e.g. Python, basic SQL",
            help="List what you already know — the roadmap will build from there.",
            key="roadmap_skills",
        )
        timeline_months = st.slider(
            "Available Timeline (months)",
            min_value=1,
            max_value=18,
            value=6,
            help="How many months do you have to prepare?",
        )

    st.divider()

    col_btn, _ = st.columns([1.5, 3])
    with col_btn:
        roadmap_btn = st.button("🗺️ Generate My Roadmap", type="primary", use_container_width=True)

    if roadmap_btn:
        final_role = job_role.strip() or job_role_option
        final_skills = format_skills_list(skills)

        missing = validate_required_fields(job_role=final_role)
        if missing:
            st.warning("Please select or enter a target role.")
            return

        log_interaction("learning_roadmap", final_role, experience_level)

        with st.spinner("🔍 Retrieving career path knowledge..."):
            query = (
                f"learning roadmap {final_role} {experience_level} "
                f"skills courses certifications {final_skills}"
            )
            rag_context = retrieve_for_role(
                job_role=final_role,
                query=query,
                extra_sources=["general_career"],
            )

        with st.spinner("🤖 IBM Granite is building your personalized roadmap..."):
            system_prompt, user_prompt = build_roadmap_prompt(
                job_role=final_role,
                experience_level=experience_to_label(experience_level),
                skills=final_skills,
                timeline_months=timeline_months,
                rag_context=rag_context,
            )
            response = generate_response(user_prompt, system_prompt)
            response = clean_granite_response(response)

        st.success("✅ Your personalized learning roadmap is ready!")
        st.divider()

        # ── Roadmap Display ───────────────────────────────────────────────────
        st.markdown(f"### 🗺️ Learning Roadmap — {final_role}")
        st.markdown(
            f"*{experience_level} → {final_role} | Timeline: {timeline_months} months*"
        )
        st.divider()
        st.markdown(response)

        # ── Download ──────────────────────────────────────────────────────────
        st.download_button(
            label="📥 Download Roadmap",
            data=f"InterviewAce AI — Learning Roadmap\n{'='*50}\n"
                 f"Target Role: {final_role}\nCurrent Level: {experience_level}\n"
                 f"Skills: {final_skills}\nTimeline: {timeline_months} months\n\n"
                 + response,
            file_name=f"roadmap_{final_role.replace(' ', '_').lower()}.txt",
            mime="text/plain",
        )

        # ── IBM Resources Callout ─────────────────────────────────────────────
        st.info(
            "🎓 **IBM SkillsBuild** offers free courses and certifications aligned to this roadmap. "
            "Visit [skillsbuild.org](https://skillsbuild.org) to explore AI, Cloud, and Data programs."
        )

        with st.expander("🔎 Knowledge Sources Used (RAG)", expanded=False):
            st.caption("Career path context retrieved from knowledge base:")
            st.text(rag_context[:600] + ("..." if len(rag_context) > 600 else ""))
