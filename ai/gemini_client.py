"""
ai/gemini_client.py - Centralized Google Gemini API Client for AI-FitCoach
Handles API key resolution, Google GenAI client instantiation, configurable models,
timeouts, and resilient error reporting using google-genai SDK.
"""

import os
from typing import Optional, Tuple, List, Dict, Any
from dotenv import load_dotenv

load_dotenv()

# Default Gemini model
DEFAULT_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

# Standardized Safe System Prompts
WORKOUT_SYSTEM_PROMPT = (
    "You are an AI fitness assistant. Generate safe, realistic, personalized general fitness guidance. "
    "Do not diagnose medical conditions. Do not recommend dangerous exercises or extreme training. "
    "Adapt suggestions to the user's experience and stated goals."
)

DIET_SYSTEM_PROMPT = (
    "You are an AI nutrition assistant providing general meal suggestions. "
    "Avoid extreme diets and dangerous calorie restrictions. "
    "Consider the user's preferences and allergies. "
    "Do not diagnose or treat medical conditions."
)

CHATBOT_SYSTEM_PROMPT = (
    "You are AI FitCoach, a general fitness education assistant. "
    "Provide practical and safe fitness guidance. You are not a doctor or medical professional. "
    "Do not diagnose conditions. For serious symptoms or emergencies, advise the user to seek qualified medical care."
)

RECOMMENDATION_SYSTEM_PROMPT = (
    "You are AI FitCoach, an encouraging and scientific fitness progress analyst. "
    "Analyze the user's recent weight, workout, hydration, and sleep logs to provide actionable, "
    "supportive recommendations. Never diagnose health conditions. Keep advice safe and sustainable."
)


def get_effective_api_key(custom_key: Optional[str] = None) -> str:
    """
    Returns the custom key if provided, else reads from environment (GEMINI_API_KEY)
    or Streamlit secrets.
    """
    if custom_key and custom_key.strip():
        return custom_key.strip()
    env_key = os.getenv("GEMINI_API_KEY", "").strip()
    if env_key:
        return env_key
    try:
        import streamlit as st
        if hasattr(st, "secrets") and "GEMINI_API_KEY" in st.secrets:
            sec_val = str(st.secrets["GEMINI_API_KEY"]).strip()
            if sec_val:
                return sec_val
    except Exception:
        pass
    return ""


def is_gemini_configured(custom_key: Optional[str] = None) -> bool:
    """Returns True if a valid Google Gemini API key is configured."""
    key = get_effective_api_key(custom_key)
    return bool(key and len(key) >= 15)


def get_gemini_client(api_key: Optional[str] = None):
    """Instantiates and returns the Google GenAI client."""
    from google import genai
    key = get_effective_api_key(api_key)
    if not key:
        raise ValueError(
            "Gemini API key is missing. Please configure GEMINI_API_KEY in the Render environment variables."
        )
    return genai.Client(api_key=key)


def get_configured_model() -> str:
    """Returns the model name from env, st.secrets, or defaults to gemini-1.5-flash."""
    env_model = os.getenv("GEMINI_MODEL", "").strip()
    if env_model:
        return env_model
    try:
        import streamlit as st
        if hasattr(st, "secrets") and "GEMINI_MODEL" in st.secrets:
            sec_m = str(st.secrets["GEMINI_MODEL"]).strip()
            if sec_m:
                return sec_m
    except Exception:
        pass
    return DEFAULT_MODEL


def validate_api_key(api_key: str) -> Tuple[bool, str]:
    """
    Validates the provided Gemini API key format and performs a lightweight test call.
    Returns (is_valid, message).
    """
    clean_key = (api_key or "").strip()
    if not clean_key:
        return False, "Gemini API key cannot be empty."
    if len(clean_key) < 15:
        return False, "Invalid key format. Gemini API key appears too short."

    try:
        from google import genai
        client = genai.Client(api_key=clean_key)
        # Lightweight check: get model metadata
        client.models.get(model=get_configured_model())
        return True, "Google Gemini API key validated successfully!"
    except Exception as e:
        err_msg = str(e)
        if "API_KEY_INVALID" in err_msg or "400" in err_msg or "403" in err_msg:
            return False, "Invalid Gemini API key. Please check your credentials at Google AI Studio."
        elif "quota" in err_msg.lower() or "RESOURCE_EXHAUSTED" in err_msg or "429" in err_msg:
            return False, "Gemini API key has exceeded its quota limit."
        return False, f"API test connection failed: {err_msg}"


def generate_completion(
    prompt: str = "",
    system_message: str = CHATBOT_SYSTEM_PROMPT,
    messages: Optional[List[Dict[str, str]]] = None,
    api_key: Optional[str] = None,
    model: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: int = 2000
) -> Tuple[bool, str]:
    """
    Executes a content generation call using the Google GenAI client with comprehensive error handling.
    Returns (success: bool, content_or_error_message: str).
    """
    effective_key = get_effective_api_key(api_key)
    if not effective_key:
        return (
            False,
            "Gemini API key is not configured. Please add GEMINI_API_KEY in the Render environment variables or enter it in the sidebar."
        )

    chosen_model = model or get_configured_model()

    try:
        from google import genai
        from google.genai import types

        client = get_gemini_client(effective_key)

        # Build contents and system instruction
        active_system_instruction = system_message.strip() if system_message else None
        contents_payload: Any = []

        if messages:
            for msg in messages:
                role = msg.get("role", "user").lower()
                content_text = msg.get("content", "").strip()
                if not content_text:
                    continue

                if role == "system":
                    if active_system_instruction:
                        active_system_instruction = f"{active_system_instruction}\n\n{content_text}"
                    else:
                        active_system_instruction = content_text
                else:
                    gemini_role = "model" if role in ["assistant", "model", "coach"] else "user"
                    contents_payload.append(
                        types.Content(
                            role=gemini_role,
                            parts=[types.Part.from_text(text=content_text)]
                        )
                    )
            # If prompt was also provided separately, append it as user message
            if prompt and prompt.strip():
                contents_payload.append(
                    types.Content(
                        role="user",
                        parts=[types.Part.from_text(text=prompt.strip())]
                    )
                )
        elif prompt and prompt.strip():
            contents_payload = prompt.strip()
        else:
            return False, "No prompt or message content was provided for generation."

        # Configure generation parameters
        config = types.GenerateContentConfig(
            system_instruction=active_system_instruction if active_system_instruction else None,
            temperature=temperature,
            max_output_tokens=max_tokens
        )

        response = client.models.generate_content(
            model=chosen_model,
            contents=contents_payload,
            config=config
        )

        if response and response.text:
            return True, response.text.strip()
        return False, "Received an empty response from Gemini API."

    except Exception as e:
        err_str = str(e)
        if "RESOURCE_EXHAUSTED" in err_str or "429" in err_str:
            return False, "Gemini API rate limit or quota reached. Please wait a moment and try again."
        elif "API_KEY_INVALID" in err_str or "401" in err_str or "403" in err_str:
            return False, "Authentication failed. Please verify your GEMINI_API_KEY."
        elif "timeout" in err_str.lower() or "DEADLINE_EXCEEDED" in err_str:
            return False, "The request to Gemini API timed out. Please check your internet connection."
        return False, f"Gemini API Error: {err_str}"
