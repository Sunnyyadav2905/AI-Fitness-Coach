"""
database/db.py - SQLite Database Management Layer for AI-FitCoach
Provides connection management and CRUD operations for all application entities.
"""

import sqlite3
import os
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv

load_dotenv()

# Database path resolution
DEFAULT_DB_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.getenv("DATABASE_PATH", os.path.join(DEFAULT_DB_DIR, "fitcoach.db"))
SCHEMA_FILE = os.path.join(DEFAULT_DB_DIR, "schema.sql")


def get_connection(db_path: Optional[str] = None) -> sqlite3.Connection:
    """Creates and returns an SQLite database connection with row factory enabled."""
    target_db = db_path or DB_FILE
    # Ensure parent directory exists
    os.makedirs(os.path.dirname(os.path.abspath(target_db)), exist_ok=True)
    conn = sqlite3.connect(target_db, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: Optional[str] = None) -> None:
    """Executes schema.sql to initialize database tables and applies non-breaking migrations."""
    conn = get_connection(db_path)
    try:
        with open(SCHEMA_FILE, "r", encoding="utf-8") as f:
            schema_sql = f.read()
        conn.executescript(schema_sql)

        # Check and migrate profiles table columns if missing
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(profiles)")
        cols = [r[1] for r in cursor.fetchall()]
        if "dietary_preference" not in cols:
            cursor.execute("ALTER TABLE profiles ADD COLUMN dietary_preference TEXT DEFAULT 'None'")
        if "medical_notes" not in cols:
            cursor.execute("ALTER TABLE profiles ADD COLUMN medical_notes TEXT DEFAULT ''")
        conn.commit()
    finally:
        conn.close()


# =====================================================================
# User CRUD
# =====================================================================

def create_user(username: str, email: str, password_hash: str, db_path: Optional[str] = None) -> Optional[int]:
    """Creates a new user record. Returns user id if successful, None on duplicate."""
    conn = get_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
            (username.strip().lower(), email.strip().lower(), password_hash)
        )
        conn.commit()
        return cursor.lastrowid
    except sqlite3.IntegrityError:
        return None
    finally:
        conn.close()


def get_user_by_username(username: str, db_path: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Retrieves user by username."""
    conn = get_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username.strip().lower(),))
        row = cursor.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def get_user_by_email(email: str, db_path: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Retrieves user by email address."""
    conn = get_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ?", (email.strip().lower(),))
        row = cursor.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def get_user_by_id(user_id: int, db_path: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Retrieves user by ID."""
    conn = get_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


# =====================================================================
# Profiles CRUD
# =====================================================================

def save_profile(
    user_id: int,
    name: Optional[str] = None,
    age: Optional[int] = None,
    gender: Optional[str] = None,
    height: Optional[float] = None,
    weight: Optional[float] = None,
    activity_level: Optional[str] = None,
    fitness_goal: Optional[str] = None,
    target_weight: Optional[float] = None,
    dietary_preference: Optional[str] = None,
    medical_notes: Optional[str] = None,
    db_path: Optional[str] = None,
    **kwargs: Any
) -> bool:
    """Inserts or updates a user's fitness profile."""
    # Support dictionary mapping if passed via kwargs or alias
    if "full_name" in kwargs and not name:
        name = kwargs["full_name"]
    if "height_cm" in kwargs and height is None:
        height = kwargs["height_cm"]
    if "weight_kg" in kwargs and weight is None:
        weight = kwargs["weight_kg"]
    if "target_weight_kg" in kwargs and target_weight is None:
        target_weight = kwargs["target_weight_kg"]
    if "diet_preference" in kwargs and not dietary_preference:
        dietary_preference = kwargs["diet_preference"]

    conn = get_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO profiles (
                user_id, name, age, gender, height, weight,
                activity_level, fitness_goal, target_weight,
                dietary_preference, medical_notes, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(user_id) DO UPDATE SET
                name = excluded.name,
                age = excluded.age,
                gender = excluded.gender,
                height = excluded.height,
                weight = excluded.weight,
                activity_level = excluded.activity_level,
                fitness_goal = excluded.fitness_goal,
                target_weight = excluded.target_weight,
                dietary_preference = excluded.dietary_preference,
                medical_notes = excluded.medical_notes,
                updated_at = CURRENT_TIMESTAMP
        """, (
            user_id,
            name or "",
            age or 25,
            gender or "Male",
            height or 170.0,
            weight or 70.0,
            activity_level or "Moderately Active",
            fitness_goal or "Weight Loss",
            target_weight or 65.0,
            dietary_preference or "None",
            medical_notes or ""
        ))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error in save_profile: {e}")
        return False
    finally:
        conn.close()


def upsert_profile(user_id: int, profile_data: Dict[str, Any], db_path: Optional[str] = None) -> bool:
    """Helper alias for save_profile accepting a dictionary."""
    return save_profile(
        user_id=user_id,
        name=profile_data.get("name") or profile_data.get("full_name"),
        age=profile_data.get("age"),
        gender=profile_data.get("gender"),
        height=profile_data.get("height") or profile_data.get("height_cm"),
        weight=profile_data.get("weight") or profile_data.get("weight_kg"),
        activity_level=profile_data.get("activity_level"),
        fitness_goal=profile_data.get("fitness_goal"),
        target_weight=profile_data.get("target_weight") or profile_data.get("target_weight_kg"),
        dietary_preference=profile_data.get("dietary_preference") or profile_data.get("diet_preference"),
        medical_notes=profile_data.get("medical_notes"),
        db_path=db_path
    )


def get_profile(user_id: int, db_path: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Retrieves user fitness profile by user ID."""
    conn = get_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM profiles WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        if not row:
            return None
        data = dict(row)
        # Add compatibility keys for display if needed
        data["full_name"] = data.get("name")
        data["height_cm"] = data.get("height")
        data["weight_kg"] = data.get("weight")
        data["target_weight_kg"] = data.get("target_weight")
        return data
    finally:
        conn.close()


# =====================================================================
# Progress Tracking CRUD
# =====================================================================

def save_progress(
    user_id: int,
    date: str,
    weight: Optional[float] = None,
    water: Optional[float] = None,
    sleep: Optional[float] = None,
    calories: Optional[int] = None,
    workout_completed: int = 0,
    steps: int = 0,
    notes: Optional[str] = "",
    db_path: Optional[str] = None,
    **kwargs: Any
) -> int:
    """Logs daily progress metrics including weight, water, sleep, calories, workout, steps, notes."""
    # Compatibility checks for legacy kwargs
    if "weight_kg" in kwargs and weight is None:
        weight = kwargs["weight_kg"]
    if "water_liters" in kwargs and water is None:
        water = kwargs["water_liters"]
    if "sleep_hours" in kwargs and sleep is None:
        sleep = kwargs["sleep_hours"]
    if "calories_consumed" in kwargs and calories is None:
        calories = kwargs["calories_consumed"]
    if "workout_notes" in kwargs and not notes:
        notes = kwargs["workout_notes"]

    conn = get_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO progress (
                user_id, date, weight, water, sleep, calories,
                workout_completed, steps, notes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user_id,
            date,
            weight,
            water,
            sleep,
            calories,
            1 if workout_completed else 0,
            steps or 0,
            notes or ""
        ))
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def log_progress(
    user_id: int, log_date: str, weight_kg: Optional[float] = None,
    calories_consumed: Optional[int] = None, water_liters: Optional[float] = None,
    sleep_hours: Optional[float] = None, workout_completed: int = 0,
    workout_notes: str = "", mood: str = "Good", steps: int = 0, db_path: Optional[str] = None
) -> int:
    """Alias for save_progress for backwards compatibility."""
    return save_progress(
        user_id=user_id,
        date=log_date,
        weight=weight_kg,
        water=water_liters,
        sleep=sleep_hours,
        calories=calories_consumed,
        workout_completed=workout_completed,
        steps=steps,
        notes=workout_notes,
        db_path=db_path
    )


def get_progress(user_id: int, limit: int = 60, db_path: Optional[str] = None) -> List[Dict[str, Any]]:
    """Retrieves progress logs for a user ordered by date ascending."""
    conn = get_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM progress WHERE user_id = ? ORDER BY date ASC, id ASC LIMIT ?",
            (user_id, limit)
        )
        rows = cursor.fetchall()
        result = []
        for r in rows:
            d = dict(r)
            # Add compatibility keys
            d["log_date"] = d.get("date")
            d["weight_kg"] = d.get("weight")
            d["water_liters"] = d.get("water")
            d["sleep_hours"] = d.get("sleep")
            d["calories_consumed"] = d.get("calories")
            d["workout_notes"] = d.get("notes")
            result.append(d)
        return result
    finally:
        conn.close()


def get_progress_logs(user_id: int, limit: int = 60, db_path: Optional[str] = None) -> List[Dict[str, Any]]:
    """Alias for get_progress."""
    return get_progress(user_id, limit=limit, db_path=db_path)


def get_latest_progress_log(user_id: int, db_path: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Returns the single most recent progress log."""
    conn = get_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM progress WHERE user_id = ? ORDER BY date DESC, id DESC LIMIT 1",
            (user_id,)
        )
        row = cursor.fetchone()
        if not row:
            return None
        d = dict(row)
        d["log_date"] = d.get("date")
        d["weight_kg"] = d.get("weight")
        d["water_liters"] = d.get("water")
        d["sleep_hours"] = d.get("sleep")
        d["calories_consumed"] = d.get("calories")
        d["workout_notes"] = d.get("notes")
        return d
    finally:
        conn.close()


# =====================================================================
# Workout Plans CRUD
# =====================================================================

def save_workout_plan(user_id: int, *args: Any, plan: Optional[str] = None, db_path: Optional[str] = None, **kwargs: Any) -> int:
    """Saves a workout plan to the database. Supports (user_id, plan) or legacy positional signatures."""
    actual_plan = plan
    if not actual_plan and args:
        actual_plan = str(args[-1])
    if "plan_content" in kwargs and not actual_plan:
        actual_plan = kwargs["plan_content"]
    if not actual_plan:
        actual_plan = "Workout Plan"

    conn = get_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO workout_plans (user_id, plan) VALUES (?, ?)",
            (user_id, actual_plan)
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def get_workout_plans(user_id: int, db_path: Optional[str] = None) -> List[Dict[str, Any]]:
    """Fetches all saved workout plans for a user, newest first."""
    conn = get_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM workout_plans WHERE user_id = ? ORDER BY created_at DESC", (user_id,))
        rows = cursor.fetchall()
        result = []
        for r in rows:
            d = dict(r)
            d["plan_content"] = d.get("plan")
            d["title"] = "Workout Plan"
            result.append(d)
        return result
    finally:
        conn.close()


def delete_workout_plan(plan_id: int, user_id: int, db_path: Optional[str] = None) -> bool:
    """Deletes a workout plan owned by user."""
    conn = get_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM workout_plans WHERE id = ? AND user_id = ?", (plan_id, user_id))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()


# =====================================================================
# Diet Plans CRUD
# =====================================================================

def save_diet_plan(user_id: int, *args: Any, plan: Optional[str] = None, db_path: Optional[str] = None, **kwargs: Any) -> int:
    """Saves a diet plan to the database. Supports (user_id, plan) or legacy positional signatures."""
    actual_plan = plan
    if not actual_plan and args:
        actual_plan = str(args[-1])
    if "plan_content" in kwargs and not actual_plan:
        actual_plan = kwargs["plan_content"]
    if not actual_plan:
        actual_plan = "Diet Plan"

    conn = get_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO diet_plans (user_id, plan) VALUES (?, ?)",
            (user_id, actual_plan)
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def get_diet_plans(user_id: int, db_path: Optional[str] = None) -> List[Dict[str, Any]]:
    """Fetches all saved diet plans for a user, newest first."""
    conn = get_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM diet_plans WHERE user_id = ? ORDER BY created_at DESC", (user_id,))
        rows = cursor.fetchall()
        result = []
        for r in rows:
            d = dict(r)
            d["plan_content"] = d.get("plan")
            d["title"] = "Diet Plan"
            result.append(d)
        return result
    finally:
        conn.close()


def delete_diet_plan(plan_id: int, user_id: int, db_path: Optional[str] = None) -> bool:
    """Deletes a diet plan owned by user."""
    conn = get_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM diet_plans WHERE id = ? AND user_id = ?", (plan_id, user_id))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()


# =====================================================================
# Chat History CRUD
# =====================================================================

def save_chat_message(user_id: int, role: str, message: str, db_path: Optional[str] = None) -> int:
    """Saves a chat message turn to the database."""
    conn = get_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO chat_history (user_id, role, message) VALUES (?, ?, ?)",
            (user_id, role, message)
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def get_chat_history(user_id: int, limit: int = 50, db_path: Optional[str] = None) -> List[Dict[str, Any]]:
    """Fetches chat history in chronological order."""
    conn = get_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM (SELECT * FROM chat_history WHERE user_id = ? ORDER BY id DESC LIMIT ?) ORDER BY id ASC",
            (user_id, limit)
        )
        rows = cursor.fetchall()
        result = []
        for r in rows:
            d = dict(r)
            d["timestamp"] = d.get("created_at")
            result.append(d)
        return result
    finally:
        conn.close()


def clear_chat_history(user_id: int, db_path: Optional[str] = None) -> bool:
    """Clears all chat history for a user."""
    conn = get_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM chat_history WHERE user_id = ?", (user_id,))
        conn.commit()
        return True
    finally:
        conn.close()


# Auto-initialize DB schema on load
init_db()

