"""
InterviewAce AI — Interview Preparation Page
"""

import streamlit as st
from core.granite_client import generate_response
from core.prompts import build_interview_prep_prompt, build_quick_tips_prompt
from rag.retriever import retrieve_for_role
from utils.helpers import (
    validate_required_fields,
    sanitize_text,
    format_skills_list,
    experience_to_label,
    EXPERIENCE_LEVELS,
    COMMON_JOB_ROLES,
    get_default_skills,
    log_interaction,
    clean_granite_response,
)


def render():
    """Render the Interview Preparation page."""

    st.markdown("## 🎯 Interview Preparation")
    st.markdown(
        "Generate tailored interview questions, model answers, and personalized "
        "preparation tips powered by **IBM Granite** — with relevant knowledge retrieved "
        "from a built-in career guidance knowledge base."
    )

    st.divider()

    # ── Profile Input ────────────────────────────────────────────────────────
    with st.container():
        st.markdown("### 👤 Your Profile")

        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input(
                "Your Name",
                placeholder="e.g. Priya Sharma",
                help="Used to personalize the response.",
            )
            job_role_option = st.selectbox(
                "Target Job Role",
                options=COMMON_JOB_ROLES,
                index=0,
            )
            job_role = st.text_input(
                "Custom Role (if 'Other' selected or to refine)",
                value="" if job_role_option == "Other (type below)" else job_role_option,
                placeholder="e.g. AI Research Engineer",
            )

        with col2:
            experience_level = st.selectbox(
                "Experience Level",
                options=EXPERIENCE_LEVELS,
                index=0,
            )
            default_skills = get_default_skills(job_role or job_role_option)
            skills = st.text_input(
                "Key Skills (comma-separated)",
                value=default_skills,
                placeholder="e.g. Python, Machine Learning, SQL",
                help="The more specific, the better the questions.",
            )
            num_questions = st.slider(
                "Number of Questions to Generate",
                min_value=3,
                max_value=10,
                value=5,
            )

    # ── Action Buttons ────────────────────────────────────────────────────────
    st.divider()
    col_btn1, col_btn2, _ = st.columns([1.5, 1.5, 2])

    with col_btn1:
        generate_btn = st.button("🚀 Generate Interview Questions", type="primary", use_container_width=True)
    with col_btn2:
        tips_btn = st.button("💡 Quick Tips Only", use_container_width=True)

    # ── Generate Interview Questions ──────────────────────────────────────────
    if generate_btn:
        final_role = job_role.strip() or job_role_option
        final_skills = format_skills_list(skills)

        missing = validate_required_fields(name=name, job_role=final_role, skills=final_skills)
        if missing:
            st.warning(f"Please fill in: {', '.join(missing).replace('_', ' ').title()}")
            return

        log_interaction("interview_prep", final_role, experience_level)

        with st.spinner("🔍 Retrieving relevant knowledge..."):
            query = f"{final_role} {experience_level} interview questions {final_skills}"
            rag_context = retrieve_for_role(
                job_role=final_role,
                query=query,
                extra_sources=["behavioral_hr"],
            )

        with st.spinner("🤖 IBM Granite is preparing your interview guide..."):
            system_prompt, user_prompt = build_interview_prep_prompt(
                name=name,
                job_role=final_role,
                experience_level=experience_level_label(experience_level),
                skills=final_skills,
                rag_context=rag_context,
                num_questions=num_questions,
            )
            response = generate_response(user_prompt, system_prompt)
            response = clean_granite_response(response)

        # ── Display Result ────────────────────────────────────────────────────
        st.success("✅ Your personalized interview guide is ready!")
        st.divider()

        with st.container():
            st.markdown(f"### 📋 Interview Guide — {final_role}")
            st.markdown(f"*Generated for {name} | {experience_level} | Skills: {final_skills}*")
            st.divider()
            st.markdown(response)

        # ── Download ──────────────────────────────────────────────────────────
        st.download_button(
            label="📥 Download as Text",
            data=f"InterviewAce AI — Interview Guide\n{'='*50}\n"
                 f"Role: {final_role}\nLevel: {experience_level}\nSkills: {final_skills}\n\n"
                 + response,
            file_name=f"interview_guide_{final_role.replace(' ', '_').lower()}.txt",
            mime="text/plain",
        )

        # ── RAG Source Info ───────────────────────────────────────────────────
        with st.expander("🔎 Knowledge Sources Used (RAG)", expanded=False):
            st.caption("The following knowledge base context was retrieved and sent to IBM Granite:")
            st.text(rag_context[:800] + ("..." if len(rag_context) > 800 else ""))

    # ── Quick Tips ────────────────────────────────────────────────────────────
    if tips_btn:
        final_role = job_role.strip() or job_role_option

        if not final_role.strip():
            st.warning("Please select or enter a job role.")
            return

        with st.spinner("🤖 Generating quick tips..."):
            query = f"{final_role} {experience_level} interview tips"
            rag_context = retrieve_for_role(
                job_role=final_role,
                query=query,
            )
            system_prompt, user_prompt = build_quick_tips_prompt(
                job_role=final_role,
                experience_level=experience_level_label(experience_level),
                rag_context=rag_context,
            )
            response = generate_response(user_prompt, system_prompt)
            response = clean_granite_response(response)

        st.info("💡 **Quick Interview Tips**")
        st.markdown(response)


def experience_level_label(level: str) -> str:
    return experience_to_label(level)
