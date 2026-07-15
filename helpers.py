"""
InterviewAce AI — Utility / Helper Functions
=============================================
Shared helpers for input validation, text processing, and UI utilities.
"""

import re
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
#  Input Validation
# ─────────────────────────────────────────────────────────────────────────────

def validate_required_fields(**fields) -> list[str]:
    """
    Check that all provided keyword fields have non-empty string values.

    Returns:
        List of missing field names (empty list if all present).
    """
    return [name for name, value in fields.items() if not str(value).strip()]


def sanitize_text(text: str, max_length: int = 5000) -> str:
    """
    Clean and truncate user-provided text input.
    Removes null bytes and excessive whitespace; enforces a max length.
    """
    if not isinstance(text, str):
        return ""
    text = text.replace("\x00", "")
    text = re.sub(r"\n{4,}", "\n\n\n", text)  # collapse excessive newlines
    text = text.strip()
    if len(text) > max_length:
        text = text[:max_length] + "\n\n[...truncated for length]"
    return text


def format_skills_list(skills_input: str) -> str:
    """
    Normalize a comma-separated skills string.
    Capitalizes first letter only if the skill is all-lowercase; preserves
    existing capitalisation for abbreviations like SQL, ML, API, etc.
    Example: " python , ML,  fastapi " → "Python, ML, Fastapi"
    """
    def _cap(s: str) -> str:
        s = s.strip()
        if not s:
            return s
        # Preserve existing capitalisation if the skill is not all lowercase
        if s == s.lower():
            return s.capitalize()
        return s

    skills = [_cap(s) for s in skills_input.split(",") if s.strip()]
    return ", ".join(skills)


# ─────────────────────────────────────────────────────────────────────────────
#  Experience Level Helpers
# ─────────────────────────────────────────────────────────────────────────────

EXPERIENCE_LEVELS = [
    "Fresher / Student (0–1 year)",
    "Junior (1–3 years)",
    "Mid-Level (3–5 years)",
    "Senior (5–8 years)",
    "Lead / Principal (8+ years)",
]


def experience_to_label(level: str) -> str:
    """Return a short label for use in prompts."""
    mapping = {
        "Fresher": "fresher / entry-level",
        "Junior": "junior professional",
        "Mid-Level": "mid-level professional",
        "Senior": "senior professional",
        "Lead": "senior lead / principal",
    }
    for key, label in mapping.items():
        if key.lower() in level.lower():
            return label
    return level


# ─────────────────────────────────────────────────────────────────────────────
#  Response Formatting
# ─────────────────────────────────────────────────────────────────────────────

def clean_granite_response(text: str) -> str:
    """
    Post-process Granite output:
    - Strip leading/trailing whitespace
    - Remove repeated 'Response:' prefix artifacts
    - Ensure markdown renders cleanly in Streamlit
    """
    text = text.strip()
    # Remove common model artifacts
    artifacts = [
        "<|assistant|>", "<|end|>", "<|user|>", "<|system|>",
        "Response:", "Answer:", "Output:",
    ]
    for artifact in artifacts:
        if text.startswith(artifact):
            text = text[len(artifact):].strip()
    return text


def truncate_for_display(text: str, max_chars: int = 300, suffix: str = "…") -> str:
    """Shorten text for preview display."""
    if len(text) <= max_chars:
        return text
    return text[:max_chars].rsplit(" ", 1)[0] + suffix


# ─────────────────────────────────────────────────────────────────────────────
#  Role / Domain Helpers
# ─────────────────────────────────────────────────────────────────────────────

COMMON_JOB_ROLES = [
    "Data Scientist",
    "Machine Learning Engineer",
    "AI Engineer",
    "Data Analyst",
    "Software Engineer",
    "Backend Developer",
    "Frontend Developer",
    "Full Stack Developer",
    "DevOps Engineer",
    "Cloud Engineer",
    "Cybersecurity Analyst",
    "Product Manager",
    "Business Analyst",
    "UX Designer",
    "Other (type below)",
]

COMMON_SKILLS = {
    "Data Scientist": "Python, Pandas, NumPy, Scikit-learn, TensorFlow, SQL, Statistics",
    "Machine Learning Engineer": "Python, PyTorch, MLflow, Docker, Kubernetes, SQL, REST APIs",
    "AI Engineer": "Python, LLMs, Prompt Engineering, LangChain, IBM watsonx.ai, RAG",
    "Software Engineer": "Python, Java, JavaScript, Git, REST APIs, SQL, Docker",
    "Full Stack Developer": "React, Node.js, Python/Django, PostgreSQL, REST APIs, Git",
    "Data Analyst": "Python, SQL, Excel, Tableau, Power BI, Statistics",
    "Product Manager": "Roadmapping, User Research, Jira, SQL, A/B Testing, Stakeholder Management",
    "DevOps Engineer": "Docker, Kubernetes, Jenkins, Terraform, AWS/GCP, Linux, CI/CD",
    "Cloud Engineer": "AWS/Azure/IBM Cloud, Terraform, Docker, Python, Networking",
}


def get_default_skills(job_role: str) -> str:
    """Return a default skills suggestion string for the given job role."""
    for role, skills in COMMON_SKILLS.items():
        if role.lower() in job_role.lower():
            return skills
    return ""


# ─────────────────────────────────────────────────────────────────────────────
#  Session / Logging Helpers
# ─────────────────────────────────────────────────────────────────────────────

def get_timestamp() -> str:
    """Return a human-readable UTC timestamp string."""
    return datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")


def log_interaction(feature: str, job_role: str, experience_level: str):
    """Log a non-sensitive summary of a user interaction for debugging."""
    logger.info(
        "[%s] Feature: %s | Role: %s | Level: %s",
        get_timestamp(), feature, job_role, experience_level
    )
