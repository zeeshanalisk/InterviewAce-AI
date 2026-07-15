"""
InterviewAce AI — Prompt Templates
====================================
All prompt templates for each feature are defined here.
Import these in page modules instead of inlining prompt strings.
"""

from core.agent_instructions import (
    SYSTEM_PROMPT,
    INTERVIEW_PREP_INSTRUCTIONS,
    RESUME_REVIEW_INSTRUCTIONS,
    ROADMAP_INSTRUCTIONS,
    CAREER_GUIDANCE_INSTRUCTIONS,
)


# ─────────────────────────────────────────────────────────────────────────────
#  INTERVIEW PREPARATION PROMPTS
# ─────────────────────────────────────────────────────────────────────────────

def build_interview_prep_prompt(
    name: str,
    job_role: str,
    experience_level: str,
    skills: str,
    rag_context: str,
    num_questions: int = 5,
) -> tuple[str, str]:
    """Return (system_prompt, user_prompt) for interview preparation."""

    system = f"{SYSTEM_PROMPT}\n\nFEATURE-SPECIFIC INSTRUCTIONS:\n{INTERVIEW_PREP_INSTRUCTIONS}"

    user = f"""
Generate a tailored interview preparation guide for the following candidate:

**Candidate Profile:**
- Name: {name}
- Target Job Role: {job_role}
- Experience Level: {experience_level}
- Key Skills: {skills}

**Relevant Knowledge Context:**
{rag_context}

**Task:**
1. Generate exactly {num_questions} interview questions tailored to this role and experience level.
2. For each question, provide:
   - The interview question
   - Why interviewers ask this question
   - A model answer (use STAR format for behavioral questions)
3. Provide 5 targeted preparation tips for this specific role.
4. List 3 topics to study before the interview.

Format your response with clear markdown headers and numbered lists.
""".strip()

    return system, user


def build_quick_tips_prompt(
    job_role: str,
    experience_level: str,
    rag_context: str,
) -> tuple[str, str]:
    """Return (system_prompt, user_prompt) for quick interview tips."""

    system = f"{SYSTEM_PROMPT}\n\nFEATURE-SPECIFIC INSTRUCTIONS:\n{INTERVIEW_PREP_INSTRUCTIONS}"

    user = f"""
Provide 7 quick, high-impact interview tips for a {experience_level} candidate interviewing for a {job_role} role.

**Relevant Context:**
{rag_context}

Format as a numbered list. Each tip should be 2–3 sentences — specific, actionable, and role-relevant.
""".strip()

    return system, user


# ─────────────────────────────────────────────────────────────────────────────
#  RESUME REVIEW PROMPTS
# ─────────────────────────────────────────────────────────────────────────────

def build_resume_review_prompt(
    resume_text: str,
    job_role: str,
    experience_level: str,
    rag_context: str,
) -> tuple[str, str]:
    """Return (system_prompt, user_prompt) for resume review."""

    system = f"{SYSTEM_PROMPT}\n\nFEATURE-SPECIFIC INSTRUCTIONS:\n{RESUME_REVIEW_INSTRUCTIONS}"

    user = f"""
Review the following resume for a candidate applying to a **{job_role}** position ({experience_level} level).

**Resume Text:**
---
{resume_text}
---

**Resume Writing Best Practices Context:**
{rag_context}

**Task:**
1. **Strengths (2–3 points):** What is already strong about this resume?
2. **Top Improvements (3–5 points):** Specific, actionable improvements with examples.
3. **Rewritten Bullet Points:** Rewrite at least 2 weak bullet points to show the improvement.
4. **ATS Optimization Tips:** 3 suggestions to improve ATS compatibility for a {job_role} role.
5. **Overall Score:** Rate this resume out of 10 with a 2-sentence justification.

Be honest, specific, and constructive.
""".strip()

    return system, user


def build_resume_bullets_prompt(
    job_role: str,
    skills: str,
    achievement_description: str,
) -> tuple[str, str]:
    """Return (system_prompt, user_prompt) for generating resume bullet points."""

    system = SYSTEM_PROMPT

    user = f"""
Write 3 strong resume bullet points for a {job_role} candidate.

Skills/Tools used: {skills}
Achievement description (raw): {achievement_description}

Requirements:
- Use strong action verbs
- Include measurable outcomes where possible
- Follow the format: [Action Verb] + [What You Did] + [Impact/Result]
- No first-person pronouns
- Each bullet should be 1–2 lines maximum
""".strip()

    return system, user


# ─────────────────────────────────────────────────────────────────────────────
#  LEARNING ROADMAP PROMPTS
# ─────────────────────────────────────────────────────────────────────────────

def build_roadmap_prompt(
    job_role: str,
    experience_level: str,
    skills: str,
    timeline_months: int,
    rag_context: str,
) -> tuple[str, str]:
    """Return (system_prompt, user_prompt) for a learning roadmap."""

    system = f"{SYSTEM_PROMPT}\n\nFEATURE-SPECIFIC INSTRUCTIONS:\n{ROADMAP_INSTRUCTIONS}"

    user = f"""
Create a personalized learning roadmap for the following candidate:

**Profile:**
- Target Role: {job_role}
- Current Level: {experience_level}
- Current Skills: {skills}
- Available Timeline: {timeline_months} months

**Career Context:**
{rag_context}

**Task:**
1. **Phase 1 — Foundation** (weeks 1–{max(4, timeline_months*2)}): Core skills to build first
2. **Phase 2 — Intermediate** (following weeks): Deepen and expand
3. **Phase 3 — Advanced / Specialized**: Role-specific expertise
4. **Phase 4 — Job-Ready**: Portfolio, certifications, interview preparation

For each phase:
- List 3–5 specific skills/topics
- Recommend 1–2 specific resources (course names, book titles, platforms)
- Give a realistic time estimate

**30-Day Quick-Start Plan:** List 5 specific actions to take in the first 30 days.

**IBM SkillsBuild Recommendations:** List 2–3 IBM-specific certifications or courses relevant to this role.
""".strip()

    return system, user


# ─────────────────────────────────────────────────────────────────────────────
#  CAREER GUIDANCE PROMPTS
# ─────────────────────────────────────────────────────────────────────────────

def build_career_guidance_prompt(
    name: str,
    job_role: str,
    experience_level: str,
    skills: str,
    career_question: str,
    rag_context: str,
) -> tuple[str, str]:
    """Return (system_prompt, user_prompt) for career guidance."""

    system = f"{SYSTEM_PROMPT}\n\nFEATURE-SPECIFIC INSTRUCTIONS:\n{CAREER_GUIDANCE_INSTRUCTIONS}"

    user = f"""
Provide personalized career guidance for:

**Candidate Profile:**
- Name: {name}
- Current / Target Role: {job_role}
- Experience Level: {experience_level}
- Skills: {skills}

**Their Question / Concern:**
{career_question}

**Career Guidance Context:**
{rag_context}

**Task:**
1. **Direct Answer:** Address their specific question first (2–3 sentences).
2. **Short-Term Actions (Next 30 Days):** 3 specific, actionable steps.
3. **Medium-Term Strategy (3–6 months):** 3 strategic recommendations.
4. **Skills Gap Analysis:** Identify 2–3 skills they should develop for their target role.
5. **Networking & Visibility:** 2 specific networking recommendations.
6. **Motivational Closing:** 1–2 sentences of genuine encouragement.

Be specific, honest, and practical. Avoid generic advice.
""".strip()

    return system, user


def build_salary_negotiation_prompt(
    job_role: str,
    experience_level: str,
    location: str,
    rag_context: str,
) -> tuple[str, str]:
    """Return (system_prompt, user_prompt) for salary negotiation advice."""

    system = SYSTEM_PROMPT

    user = f"""
Provide salary negotiation advice for a {experience_level} {job_role} professional in {location}.

**Context:**
{rag_context}

**Task:**
1. Explain the right mindset for salary negotiation (2–3 sentences).
2. Provide a step-by-step negotiation strategy (5 steps).
3. Give 3 specific scripts / example phrases to use during negotiation.
4. List 3 common mistakes to avoid.
5. Advise on negotiating the full package beyond base salary.
""".strip()

    return system, user
