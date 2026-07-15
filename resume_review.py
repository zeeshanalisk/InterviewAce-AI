"""
InterviewAce AI — Resume Review Page
"""

import streamlit as st
from core.granite_client import generate_response
from core.prompts import build_resume_review_prompt, build_resume_bullets_prompt
from rag.retriever import retrieve_for_role
from utils.helpers import (
    validate_required_fields,
    sanitize_text,
    format_skills_list,
    EXPERIENCE_LEVELS,
    COMMON_JOB_ROLES,
    get_default_skills,
    log_interaction,
    clean_granite_response,
    experience_to_label,
)


def render():
    """Render the Resume Review page."""

    st.markdown("## 📄 Resume Review")
    st.markdown(
        "Paste your resume text and get an **AI-powered critique** with specific improvements, "
        "ATS optimization tips, rewritten bullet points, and an overall score — "
        "all tailored to your target role."
    )

    st.divider()

    # ── Input Section ─────────────────────────────────────────────────────────
    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("### 🎯 Target Role Details")
        job_role_option = st.selectbox(
            "Target Job Role",
            options=COMMON_JOB_ROLES,
            key="resume_role_select",
        )
        job_role = st.text_input(
            "Custom Role (optional)",
            value="" if job_role_option == "Other (type below)" else job_role_option,
            key="resume_role_input",
        )
        experience_level = st.selectbox(
            "Experience Level",
            options=EXPERIENCE_LEVELS,
            key="resume_exp_level",
        )

    with col2:
        st.markdown("### 📊 Review Options")
        review_type = st.radio(
            "What would you like?",
            options=[
                "Full Resume Review",
                "Quick Bullet Point Generator",
            ],
            help="Full Review: paste your resume. Bullet Generator: describe an achievement.",
        )

    st.divider()

    # ── Resume Text Input ─────────────────────────────────────────────────────
    if review_type == "Full Resume Review":
        _render_full_review(job_role, experience_level)
    else:
        _render_bullet_generator(job_role)


def _render_full_review(job_role: str, experience_level: str):
    """Full resume review sub-section."""

    st.markdown("### 📋 Paste Your Resume Text")
    st.caption(
        "💡 Tip: Copy and paste your resume text directly. "
        "Images and PDF formatting won't transfer — use plain text."
    )

    resume_text = st.text_area(
        "Resume Content",
        height=350,
        placeholder=(
            "Paste your full resume here...\n\n"
            "Example:\n"
            "Priya Sharma | priya@email.com | github.com/priya\n\n"
            "SUMMARY\nFinal-year CS student with 2 projects in ML...\n\n"
            "SKILLS\nPython, TensorFlow, SQL, Pandas...\n\n"
            "PROJECTS\nChurn Prediction Model — Built using XGBoost..."
        ),
        label_visibility="collapsed",
    )

    col_btn, _ = st.columns([1, 2])
    with col_btn:
        review_btn = st.button("🔍 Review My Resume", type="primary", use_container_width=True)

    if review_btn:
        final_role = job_role.strip() or "Software Engineer"
        resume_clean = sanitize_text(resume_text, max_length=4000)

        missing = validate_required_fields(resume_text=resume_clean, job_role=final_role)
        if missing:
            st.warning("Please paste your resume text and ensure a job role is selected.")
            return

        log_interaction("resume_review", final_role, experience_level)

        with st.spinner("🔍 Retrieving resume best practices..."):
            query = f"resume review {final_role} {experience_level} ATS optimization bullet points"
            rag_context = retrieve_for_role(
                job_role=final_role,
                query=query,
                extra_sources=["resume_tips"],
            )

        with st.spinner("🤖 IBM Granite is reviewing your resume..."):
            system_prompt, user_prompt = build_resume_review_prompt(
                resume_text=resume_clean,
                job_role=final_role,
                experience_level=experience_to_label(experience_level),
                rag_context=rag_context,
            )
            response = generate_response(user_prompt, system_prompt)
            response = clean_granite_response(response)

        st.success("✅ Resume review complete!")
        st.divider()
        st.markdown(f"### 📊 Resume Review — {final_role}")
        st.divider()
        st.markdown(response)

        st.download_button(
            label="📥 Download Review",
            data=f"InterviewAce AI — Resume Review\n{'='*50}\n"
                 f"Role: {final_role}\nLevel: {experience_level}\n\n" + response,
            file_name="resume_review.txt",
            mime="text/plain",
        )

        with st.expander("🔎 Knowledge Sources Used (RAG)", expanded=False):
            st.caption("Resume best-practices context retrieved from knowledge base:")
            st.text(rag_context[:600] + ("..." if len(rag_context) > 600 else ""))


def _render_bullet_generator(job_role: str):
    """Bullet point generator sub-section."""

    st.markdown("### ✍️ Resume Bullet Point Generator")
    st.caption(
        "Describe what you did in plain language — "
        "InterviewAce will transform it into a strong, ATS-optimized resume bullet."
    )

    col1, col2 = st.columns([1, 1])
    with col1:
        skills_used = st.text_input(
            "Skills / Tools Used",
            placeholder="e.g. Python, Pandas, Scikit-learn, SQL",
            key="bullet_skills",
        )
    with col2:
        achievement = st.text_area(
            "Describe Your Achievement (plain language)",
            height=120,
            placeholder=(
                "e.g. I built a model that predicted customer churn. "
                "It worked really well and my manager was happy with it."
            ),
            key="bullet_achievement",
        )

    col_btn, _ = st.columns([1, 2])
    with col_btn:
        bullet_btn = st.button("✨ Generate Bullet Points", type="primary", use_container_width=True)

    if bullet_btn:
        final_role = job_role.strip() or "Software Engineer"
        missing = validate_required_fields(
            skills_used=skills_used,
            achievement=achievement,
        )
        if missing:
            st.warning(f"Please fill in: {', '.join(missing).replace('_', ' ').title()}")
            return

        with st.spinner("🤖 Crafting strong bullet points..."):
            from core.agent_instructions import SYSTEM_PROMPT
            system_prompt, user_prompt = build_resume_bullets_prompt(
                job_role=final_role,
                skills=skills_used,
                achievement_description=achievement,
            )
            response = generate_response(user_prompt, system_prompt)
            response = clean_granite_response(response)

        st.success("✅ Here are your improved bullet points:")
        st.markdown(response)

        st.info(
            "💡 **Tip:** Pick the strongest bullet, add specific numbers/percentages "
            "if you have them, and drop it into your resume."
        )
