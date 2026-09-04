"""Database package for AI-FitCoach."""
from database.db import (
    get_connection,
    init_db,
    create_user,
    get_user_by_username,
    get_user_by_email,
    get_user_by_id,
    save_profile,
    upsert_profile,
    get_profile,
    save_workout_plan,
    get_workout_plans,
    delete_workout_plan,
    save_diet_plan,
    get_diet_plans,
    delete_diet_plan,
    save_progress,
    log_progress,
    get_progress,
    get_progress_logs,
    get_latest_progress_log,
    save_chat_message,
    get_chat_history,
    clear_chat_history
)

