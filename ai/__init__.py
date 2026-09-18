"""AI services package for AI-FitCoach."""
from ai.gemini_client import (
    validate_api_key,
    generate_completion,
    is_gemini_configured,
    get_effective_api_key
)
from ai.workout_generator import generate_workout_plan, generate_workout_routine
from ai.diet_generator import generate_diet_plan, generate_meal_plan
from ai.chatbot import chat_with_coach, get_coach_response
from ai.recommendations import generate_progress_recommendations, analyze_progress_and_recommend

