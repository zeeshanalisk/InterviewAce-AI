"""
InterviewAce AI — IBM Granite / watsonx.ai Connection Module
=============================================================
Handles authentication and text generation via IBM watsonx.ai SDK.
"""

import os
import logging
from functools import lru_cache
from dotenv import load_dotenv

from ibm_watsonx_ai import Credentials
from ibm_watsonx_ai.foundation_models import ModelInference
from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams

from core.agent_instructions import GENERATION_PARAMS

load_dotenv()
logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
#  Configuration loader
# ─────────────────────────────────────────────────────────────────────────────

def get_config() -> dict:
    """Load and validate IBM watsonx.ai credentials from environment."""
    config = {
        "api_key":    os.getenv("IBM_API_KEY", "").strip(),
        "project_id": os.getenv("IBM_PROJECT_ID", "").strip(),
        "url":        os.getenv("IBM_WATSONX_URL", "https://us-south.ml.cloud.ibm.com").strip(),
        "model_id":   os.getenv("IBM_MODEL_ID", "ibm/granite-3-8b-instruct").strip(),
    }

    missing = [k for k, v in config.items() if not v]
    if missing:
        raise EnvironmentError(
            f"Missing required environment variables: {', '.join(missing).upper().replace('_', ' ')}. "
            "Please check your .env file."
        )
    return config


# ─────────────────────────────────────────────────────────────────────────────
#  Model client (cached per session)
# ─────────────────────────────────────────────────────────────────────────────

@lru_cache(maxsize=1)
def _get_model_client() -> tuple:
    """Return a cached (ModelInference instance, model_id) tuple."""
    config = get_config()

    credentials = Credentials(
        url=config["url"],
        api_key=config["api_key"],
    )

    params = {
        GenParams.MAX_NEW_TOKENS:      GENERATION_PARAMS["max_new_tokens"],
        GenParams.MIN_NEW_TOKENS:      GENERATION_PARAMS["min_new_tokens"],
        GenParams.TEMPERATURE:         GENERATION_PARAMS["temperature"],
        GenParams.TOP_P:               GENERATION_PARAMS["top_p"],
        GenParams.TOP_K:               GENERATION_PARAMS["top_k"],
        GenParams.REPETITION_PENALTY:  GENERATION_PARAMS["repetition_penalty"],
    }

    model = ModelInference(
        model_id=config["model_id"],
        credentials=credentials,
        project_id=config["project_id"],
        params=params,
    )

    logger.info("IBM Granite model client initialized: %s", config["model_id"])
    return model, config["model_id"]


# ─────────────────────────────────────────────────────────────────────────────
#  Public API
# ─────────────────────────────────────────────────────────────────────────────

def generate_response(prompt: str, system_prompt: str = "") -> str:
    """
    Send a prompt to IBM Granite and return the generated text.

    Args:
        prompt:        The user/task prompt.
        system_prompt: Optional system-level instructions prepended to the prompt.

    Returns:
        Generated text string, or an error message.
    """
    try:
        model, model_id = _get_model_client()

        # Granite models accept a combined prompt; prepend system context if provided
        full_prompt = _build_full_prompt(system_prompt, prompt)

        logger.debug("Sending prompt to %s (length: %d chars)", model_id, len(full_prompt))

        response = model.generate_text(prompt=full_prompt)

        # SDK returns a string directly from generate_text
        if isinstance(response, str):
            return response.strip()

        # Fallback: handle dict response shape
        if isinstance(response, dict):
            results = response.get("results", [{}])
            return results[0].get("generated_text", "").strip()

        return str(response).strip()

    except EnvironmentError as e:
        logger.error("Configuration error: %s", e)
        return f"⚠️ **Configuration Error:** {e}"

    except Exception as e:
        logger.error("Granite API error: %s", e, exc_info=True)
        return (
            f"⚠️ **API Error:** Unable to connect to IBM Granite. "
            f"Please verify your credentials in `.env`.\n\nDetails: {e}"
        )


def check_connection() -> tuple[bool, str]:
    """
    Test IBM watsonx.ai connectivity.

    Returns:
        (success: bool, message: str)
    """
    try:
        _, model_id = _get_model_client()
        return True, f"Connected to IBM Granite — Model: `{model_id}`"
    except EnvironmentError as e:
        return False, str(e)
    except Exception as e:
        return False, f"Connection failed: {e}"


def _build_full_prompt(system_prompt: str, user_prompt: str) -> str:
    """
    Assemble system + user prompt for Granite instruct models.
    Uses the <|system|> / <|user|> / <|assistant|> format for instruct models.
    Falls back to plain concatenation for base models.
    """
    config = get_config()
    model_id = config["model_id"].lower()

    # Instruct / chat models support structured prompting
    if "instruct" in model_id or "chat" in model_id:
        parts = []
        if system_prompt:
            parts.append(f"<|system|>\n{system_prompt}\n<|end|>")
        parts.append(f"<|user|>\n{user_prompt}\n<|end|>")
        parts.append("<|assistant|>")
        return "\n".join(parts)

    # Base models: plain text with clear separation
    if system_prompt:
        return f"{system_prompt}\n\n---\n\n{user_prompt}\n\nResponse:"
    return f"{user_prompt}\n\nResponse:"
