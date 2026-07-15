"""
InterviewAce AI — Career Guidance Page
"""

import streamlit as st
from core.granite_client import generate_response
from core.prompts import build_career_guidance_prompt, build_salary_negotiation_prompt
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


CAREER_QUESTION_EXAMPLES = [
    "How do I transition from software engineering to data science?",
    "I'm a fresher with no work experience. How do I get my first job?",
    "What should I focus on to get promoted to a senior role?",
    "How do I stand out in a competitive job market?",
    "How do I negotiate my salary for the first time?",
    "Should I do a Master's degree or start working immediately?",
    "How do I build a personal brand on LinkedIn?",
    "I've been rejected 10 times. What am I doing wrong?",
    "How do I switch companies after 1 year without it looking bad?",
]


def render():
    """Render the Career Guidance page."""

    st.markdown("## 🧭 Career Guidance")
    st.markdown(
        "Ask any career question and get **honest, specific, personalized advice** "
        "from InterviewAce AI — your AI-powered career mentor."
    )

    st.divider()

    # ── Tab Navigation ─────────────────────────────────────────────────────────
    tab1, tab2 = st.tabs(["💬 Ask Career Mentor", "💰 Salary Negotiation Advisor"])

    with tab1:
        _render_career_mentor()

    with tab2:
        _render_salary_advisor()


def _render_career_mentor():
    """Career Q&A sub-section."""

    st.markdown("### 👤 Your Profile")

    col1, col2 = st.columns([1, 1])

    with col1:
        name = st.text_input(
            "Your Name",
            placeholder="e.g. Arjun Mehta",
            key="career_name",
        )
        job_role_option = st.selectbox(
            "Current / Target Role",
            options=COMMON_JOB_ROLES,
            key="career_role_select",
        )
        job_role = st.text_input(
            "Custom Role (optional)",
            value="" if job_role_option == "Other (type below)" else job_role_option,
            key="career_role_input",
        )

    with col2:
        experience_level = st.selectbox(
            "Experience Level",
            options=EXPERIENCE_LEVELS,
            key="career_exp_level",
        )
        default_skills = get_default_skills(job_role or job_role_option)
        skills = st.text_input(
            "Key Skills",
            value=default_skills,
            placeholder="e.g. Python, SQL, Machine Learning",
            key="career_skills",
        )

    st.divider()
    st.markdown("### ❓ Your Career Question")

    # Example question quickfill
    st.caption("💡 Click an example question or type your own:")
    example_cols = st.columns(3)
    selected_example = None
    for i, example in enumerate(CAREER_QUESTION_EXAMPLES[:6]):
        with example_cols[i % 3]:
            if st.button(
                f'"{example[:45]}..."' if len(example) > 45 else f'"{example}"',
                key=f"career_ex_{i}",
                use_container_width=True,
            ):
                selected_example = example

    career_question = st.text_area(
        "Your Question",
        value=selected_example or "",
        height=100,
        placeholder="Type your career question here...",
        key="career_question_input",
        label_visibility="collapsed",
    )

    col_btn, _ = st.columns([1.5, 3])
    with col_btn:
        guidance_btn = st.button("🧭 Get Career Guidance", type="primary", use_container_width=True)

    if guidance_btn:
        final_role = job_role.strip() or job_role_option
        final_skills = format_skills_list(skills)
        final_name = name.strip() or "there"

        missing = validate_required_fields(career_question=career_question, job_role=final_role)
        if missing:
            st.warning("Please enter your question and target role.")
            return

        log_interaction("career_guidance", final_role, experience_level)

        with st.spinner("🔍 Retrieving career guidance knowledge..."):
            query = (
                f"career guidance {final_role} {experience_level} "
                f"job search networking {career_question}"
            )
            rag_context = retrieve_for_role(
                job_role=final_role,
                query=query,
                extra_sources=["general_career"],
            )

        with st.spinner("🤖 IBM Granite is preparing your personalized guidance..."):
            system_prompt, user_prompt = build_career_guidance_prompt(
                name=final_name,
                job_role=final_role,
                experience_level=experience_to_label(experience_level),
                skills=final_skills,
                career_question=career_question,
                rag_context=rag_context,
            )
            response = generate_response(user_prompt, system_prompt)
            response = clean_granite_response(response)

        st.success(f"✅ Guidance ready, {final_name}!")
        st.divider()
        st.markdown(f"### 🧭 Your Career Guidance")
        st.divider()
        st.markdown(response)

        st.download_button(
            label="📥 Save Guidance",
            data=f"InterviewAce AI — Career Guidance\n{'='*50}\n"
                 f"Question: {career_question}\n\n" + response,
            file_name="career_guidance.txt",
            mime="text/plain",
        )

        with st.expander("🔎 Knowledge Sources Used (RAG)", expanded=False):
            st.caption("Career knowledge context retrieved from knowledge base:")
            st.text(rag_context[:600] + ("..." if len(rag_context) > 600 else ""))


def _render_salary_advisor():
    """Salary negotiation sub-section."""

    st.markdown("### 💰 Salary Negotiation Advisor")
    st.markdown(
        "Get strategic, honest advice on how to negotiate your salary "
        "— including scripts and common mistakes to avoid."
    )

    col1, col2 = st.columns([1, 1])

    with col1:
        job_role_sal = st.selectbox(
            "Job Role",
            options=COMMON_JOB_ROLES,
            key="salary_role_select",
        )
        job_role_sal_custom = st.text_input(
            "Custom Role (optional)",
            value="" if job_role_sal == "Other (type below)" else job_role_sal,
            key="salary_role_input",
        )

    with col2:
        experience_level_sal = st.selectbox(
            "Experience Level",
            options=EXPERIENCE_LEVELS,
            key="salary_exp_level",
        )
        location = st.text_input(
            "Location / Market",
            placeholder="e.g. Bangalore, India  |  San Francisco, USA",
            key="salary_location",
        )

    col_btn, _ = st.columns([1.5, 3])
    with col_btn:
        salary_btn = st.button("💰 Get Negotiation Advice", type="primary", use_container_width=True)

    if salary_btn:
        final_role = job_role_sal_custom.strip() or job_role_sal
        final_location = location.strip() or "your location"

        with st.spinner("🤖 IBM Granite is preparing your negotiation strategy..."):
            rag_context = retrieve_for_role(
                job_role=final_role,
                query=f"salary negotiation {final_role} {final_location}",
                extra_sources=["general_career"],
            )
            system_prompt, user_prompt = build_salary_negotiation_prompt(
                job_role=final_role,
                experience_level=experience_to_label(experience_level_sal),
                location=final_location,
                rag_context=rag_context,
            )
            response = generate_response(user_prompt, system_prompt)
            response = clean_granite_response(response)

        st.success("✅ Negotiation strategy ready!")
        st.divider()
        st.markdown("### 💰 Salary Negotiation Strategy")
        st.divider()
        st.markdown(response)
