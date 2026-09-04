"""
tests/test_database.py - Unit Tests for SQLite Database CRUD Operations
"""

import os
import tempfile
import pytest
from database import db


@pytest.fixture
def temp_db():
    """Creates an isolated temporary SQLite database for testing."""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    db.init_db(db_path=path)
    yield path
    if os.path.exists(path):
        os.remove(path)


def test_user_crud(temp_db):
    # Create user
    user_id = db.create_user("testuser", "test@fitcoach.ai", "hash12345", db_path=temp_db)
    assert user_id is not None

    # Duplicate username should fail
    dup_id = db.create_user("testuser", "other@fitcoach.ai", "hash12345", db_path=temp_db)
    assert dup_id is None

    # Fetch user
    u = db.get_user_by_username("testuser", db_path=temp_db)
    assert u is not None
    assert u["email"] == "test@fitcoach.ai"


def test_profile_upsert(temp_db):
    user_id = db.create_user("profileuser", "profile@fitcoach.ai", "hash123", db_path=temp_db)

    profile_data = {
        "full_name": "Test Athlete",
        "age": 28,
        "gender": "Female",
        "height_cm": 165.0,
        "weight_kg": 62.0,
        "target_weight_kg": 58.0,
        "activity_level": "Moderately Active",
        "fitness_goal": "Weight Loss",
        "diet_preference": "Vegetarian",
        "medical_notes": "None"
    }
    success = db.upsert_profile(user_id, profile_data, db_path=temp_db)
    assert success is True

    loaded = db.get_profile(user_id, db_path=temp_db)
    assert loaded["full_name"] == "Test Athlete"
    assert loaded["height_cm"] == 165.0
    assert loaded["weight_kg"] == 62.0


def test_plans_crud(temp_db):
    user_id = db.create_user("planuser", "plan@fitcoach.ai", "hash123", db_path=temp_db)

    # Workout plan - legacy call style
    w_id = db.save_workout_plan(user_id, "PPL Routine", "PPL", 4, "Plan text details", db_path=temp_db)
    assert w_id is not None

    # Workout plan - schema call style
    w_id2 = db.save_workout_plan(user_id, plan="Standard Upper Lower Plan", db_path=temp_db)
    assert w_id2 is not None

    w_plans = db.get_workout_plans(user_id, db_path=temp_db)
    assert len(w_plans) == 2

    # Delete workout plan
    del_res = db.delete_workout_plan(w_id, user_id, db_path=temp_db)
    assert del_res is True
    assert len(db.get_workout_plans(user_id, db_path=temp_db)) == 1

    # Diet plan - legacy call style
    d_id = db.save_diet_plan(user_id, "High Protein Plan", 2200, "Meal breakdown", db_path=temp_db)
    assert d_id is not None

    # Diet plan - schema call style
    d_id2 = db.save_diet_plan(user_id, plan="Mediterranean Diet Plan", db_path=temp_db)
    assert d_id2 is not None

    d_plans = db.get_diet_plans(user_id, db_path=temp_db)
    assert len(d_plans) == 2

    # Delete diet plan
    del_diet_res = db.delete_diet_plan(d_id, user_id, db_path=temp_db)
    assert del_diet_res is True
    assert len(db.get_diet_plans(user_id, db_path=temp_db)) == 1


def test_progress_logs(temp_db):
    user_id = db.create_user("loguser", "log@fitcoach.ai", "hash123", db_path=temp_db)

    log_id = db.log_progress(
        user_id=user_id,
        log_date="2026-09-04",
        weight_kg=71.2,
        calories_consumed=2100,
        water_liters=3.0,
        sleep_hours=8.0,
        workout_completed=1,
        workout_notes="Leg day completed",
        mood="Energetic",
        steps=8500,
        db_path=temp_db
    )
    assert log_id is not None

    logs = db.get_progress_logs(user_id, limit=10, db_path=temp_db)
    assert len(logs) == 1
    assert logs[0]["sleep_hours"] == 8.0
    assert logs[0]["weight_kg"] == 71.2
    assert logs[0]["steps"] == 8500

    # Test latest progress log
    latest = db.get_latest_progress_log(user_id, db_path=temp_db)
    assert latest is not None
    assert latest["steps"] == 8500


def test_chat_history(temp_db):
    user_id = db.create_user("chatuser", "chat@fitcoach.ai", "hash123", db_path=temp_db)

    m1 = db.save_chat_message(user_id, "user", "What is the best post-workout snack?", db_path=temp_db)
    m2 = db.save_chat_message(user_id, "assistant", "Greek yogurt with fruit or a whey shake.", db_path=temp_db)
    assert m1 is not None
    assert m2 is not None

    history = db.get_chat_history(user_id, limit=10, db_path=temp_db)
    assert len(history) == 2
    assert history[0]["role"] == "user"
    assert history[1]["role"] == "assistant"

    # Clear chat
    db.clear_chat_history(user_id, db_path=temp_db)
    assert len(db.get_chat_history(user_id, limit=10, db_path=temp_db)) == 0
