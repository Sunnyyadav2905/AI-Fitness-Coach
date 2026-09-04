"""
ai/openai_client.py - Centralized OpenAI API Client for AI-FitCoach
Handles API key validation, client instantiation, configurable models,
timeouts, and resilient error reporting.
"""

import os
from typing import Optional, Tuple, List, Dict, Any
from dotenv import load_dotenv

load_dotenv()

# Configurable OpenAI Model
DEFAULT_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# Standardized Safe System Prompts (Prompt Section 30)
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
    """Returns the custom key if provided, else reads from environment."""
    if custom_key and custom_key.strip():
        return custom_key.strip()
    return os.getenv("OPENAI_API_KEY", "").strip()


def is_openai_configured(custom_key: Optional[str] = None) -> bool:
    """Returns True if a non-empty OpenAI API key is detected."""
    key = get_effective_api_key(custom_key)
    return bool(key and key.startswith("sk-") and len(key) > 20)


def get_openai_client(api_key: Optional[str] = None):
    """Instantiates and returns the OpenAI client."""
    from openai import OpenAI
    key = get_effective_api_key(api_key)
    if not key:
        raise ValueError("OpenAI API key is missing. Please configure OPENAI_API_KEY.")
    return OpenAI(api_key=key, timeout=30.0)


def validate_api_key(api_key: str) -> Tuple[bool, str]:
    """
    Validates the provided OpenAI API key format and performs a lightweight test call.
    Returns (is_valid, message).
    """
    clean_key = (api_key or "").strip()
    if not clean_key:
        return False, "API key cannot be empty. Please provide a valid key starting with 'sk-'."
    if not clean_key.startswith("sk-"):
        return False, "Invalid format. OpenAI API keys typically start with 'sk-'."
    if len(clean_key) < 20:
        return False, "API key appears too short to be valid."

    try:
        from openai import OpenAI
        client = OpenAI(api_key=clean_key, timeout=10.0)
        # Lightweight test request
        client.models.list()
        return True, "OpenAI API key validated successfully!"
    except Exception as e:
        err_msg = str(e)
        if "Incorrect API key" in err_msg or "invalid_api_key" in err_msg or "401" in err_msg:
            return False, "Invalid OpenAI API key. Please check your credentials."
        elif "quota" in err_msg.lower() or "429" in err_msg:
            return False, "OpenAI API key has exceeded its quota or billing is inactive."
        return False, f"API test connection failed: {err_msg}"


def generate_completion(
    prompt: str,
    system_message: str = CHATBOT_SYSTEM_PROMPT,
    messages: Optional[List[Dict[str, str]]] = None,
    api_key: Optional[str] = None,
    model: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: int = 2000
) -> Tuple[bool, str]:
    """
    Executes a chat completion call using the OpenAI client with comprehensive error handling.
    Returns (success: bool, content_or_error_message: str).
    """
    effective_key = get_effective_api_key(api_key)
    if not effective_key:
        return False, "OpenAI API key is not configured. Please add OPENAI_API_KEY to your .env file or enter it in the sidebar."

    chosen_model = model or DEFAULT_MODEL

    try:
        client = get_openai_client(effective_key)

        chat_messages = []
        if system_message:
            chat_messages.append({"role": "system", "content": system_message})

        if messages:
            chat_messages.extend(messages)
        elif prompt:
            chat_messages.append({"role": "user", "content": prompt})

        response = client.chat.completions.create(
            model=chosen_model,
            messages=chat_messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        content = response.choices[0].message.content
        if content:
            return True, content.strip()
        return False, "Received an empty response from OpenAI."
    except Exception as e:
        err_str = str(e)
        if "rate_limit" in err_str.lower() or "429" in err_str:
            return False, "OpenAI rate limit reached. Please wait a moment and try again."
        elif "timeout" in err_str.lower():
            return False, "The request to OpenAI timed out. Please check your internet connection."
        elif "authentication" in err_str.lower() or "401" in err_str:
            return False, "Authentication failed. Please verify your OpenAI API key."
        return False, f"OpenAI API Error: {err_str}"

