"""
tests/test_gemini.py - Unit tests for Google Gemini client and fallback AI pipelines
"""

import pytest
from ai.gemini_client import (
    is_gemini_configured,
    validate_api_key,
    generate_completion,
    get_configured_model
)
from ai.chatbot import is_medical_emergency, chat_with_coach, EMERGENCY_RESPONSE
from ai.workout_generator import generate_workout_plan
from ai.diet_generator import generate_diet_plan
from ai.recommendations import generate_progress_recommendations


def test_is_gemini_configured():
    assert is_gemini_configured("") is False
    assert is_gemini_configured(None) is False
    assert is_gemini_configured("too_short") is False
    assert is_gemini_configured("AIzaSyDummyKeyForTestingPurposes12345") is True


def test_validate_api_key_empty():
    valid, msg = validate_api_key("")
    assert valid is False
    assert "cannot be empty" in msg


def test_validate_api_key_too_short():
    valid, msg = validate_api_key("short_key")
    assert valid is False
    assert "too short" in msg


def test_get_configured_model():
    model = get_configured_model()
    assert isinstance(model, str)
    assert len(model) > 0


def test_generate_completion_without_key():
    success, reply = generate_completion(
        prompt="Hello coach",
        api_key=""
    )
    assert success is False
    assert "Gemini API key is not configured" in reply


def test_chatbot_emergency_detection():
    assert is_medical_emergency("I have severe chest pain") is True
    assert is_medical_emergency("heart attack symptoms") is True
    assert is_medical_emergency("can't breathe properly") is True
    assert is_medical_emergency("What are the best bicep exercises?") is False


def test_chatbot_emergency_response_interception():
    profile = {"name": "Test User", "fitness_goal": "Strength"}
    success, reply = chat_with_coach(
        user_id=9999,
        user_message="I think I am having a heart attack",
        profile=profile,
        api_key=""
    )
    assert success is True
    assert "IMPORTANT MEDICAL ALERT" in reply


def test_workout_offline_fallback():
    profile = {
        "name": "Alex",
        "age": 28,
        "gender": "Male",
        "height_cm": 178,
        "weight_kg": 75,
        "fitness_goal": "Muscle Gain"
    }
    preferences = {
        "split_type": "Upper / Lower",
        "days_per_week": 4,
        "duration": 45,
        "equipment": "Full Gym",
        "experience": "Intermediate"
    }
    success, plan = generate_workout_plan(profile, preferences, api_key="")
    assert success is True
    assert "Offline Template Engine Active" in plan
    assert "Disclaimer" in plan


def test_diet_offline_fallback():
    profile = {
        "name": "Sarah",
        "age": 26,
        "gender": "Female",
        "height_cm": 165,
        "weight_kg": 62,
        "target_weight_kg": 58,
        "activity_level": "Moderately Active",
        "fitness_goal": "Weight Loss"
    }
    preferences = {
        "dietary_preference": "Vegetarian",
        "allergies": "None",
        "num_meals": 4
    }
    success, plan = generate_diet_plan(profile, preferences, api_key="")
    assert success is True
    assert "Offline Metabolic Engine Active" in plan
    assert "Disclaimer" in plan


def test_recommendations_offline_fallback():
    profile = {
        "name": "Jordan",
        "weight": 80,
        "target_weight": 75,
        "fitness_goal": "Weight Loss"
    }
    logs = [
        {"weight": 80.5, "water_liters": 2.5, "sleep_hours": 7.5, "calories": 2100, "steps": 8500, "workout_completed": 1},
        {"weight": 80.0, "water_liters": 3.0, "sleep_hours": 8.0, "calories": 2000, "steps": 9200, "workout_completed": 1}
    ]
    success, rec = generate_progress_recommendations(profile, logs, api_key="")
    assert success is True
    assert "Offline Progress Intelligence" in rec
    assert "Disclaimer" in rec
