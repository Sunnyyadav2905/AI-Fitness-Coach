"""
utils/validators.py - Input Validation Utilities for AI-FitCoach
Ensures data integrity, correct ranges, and secure input formats.
"""

import re
from typing import Tuple, Union


def validate_email(email: str) -> Tuple[bool, str]:
    """Validates email format using regex."""
    if not email or not isinstance(email, str):
        return False, "Email address cannot be empty."
    email_clean = email.strip()
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    if not re.match(pattern, email_clean):
        return False, "Please enter a valid email address."
    return True, "Valid email."


def validate_username(username: str) -> Tuple[bool, str]:
    """Validates username length and permitted characters."""
    if not username or not isinstance(username, str):
        return False, "Username cannot be empty."
    clean = username.strip()
    if len(clean) < 3:
        return False, "Username must be at least 3 characters long."
    if len(clean) > 30:
        return False, "Username cannot exceed 30 characters."
    if not re.match(r"^[a-zA-Z0-9_.-]+$", clean):
        return False, "Username may only contain letters, numbers, dots, underscores, and dashes."
    return True, "Valid username."


def validate_password(password: str) -> Tuple[bool, str]:
    """Validates password strength."""
    if not password or not isinstance(password, str):
        return False, "Password cannot be empty."
    if len(password) < 6:
        return False, "Password must be at least 6 characters long."
    return True, "Valid password."


def validate_numeric_range(
    value: Union[int, float], min_val: float, max_val: float, field_name: str = "Field"
) -> Tuple[bool, str]:
    """Checks whether a numeric measurement falls within realistic physiological bounds and is not negative."""
    try:
        val = float(value)
    except (ValueError, TypeError):
        return False, f"{field_name} must be a valid number."

    if val < 0:
        return False, f"{field_name} cannot be negative."
    if val < min_val:
        return False, f"{field_name} cannot be less than {min_val}."
    if val > max_val:
        return False, f"{field_name} cannot exceed {max_val}."
    return True, f"{field_name} is valid."


def validate_age(age: Union[int, float]) -> Tuple[bool, str]:
    """Validates user age (years: 5 - 120)."""
    return validate_numeric_range(age, 5, 120, "Age")


def validate_height(height: Union[int, float]) -> Tuple[bool, str]:
    """Validates user height in cm (50 - 280 cm)."""
    return validate_numeric_range(height, 50.0, 280.0, "Height")


def validate_weight(weight: Union[int, float]) -> Tuple[bool, str]:
    """Validates user weight in kg (20 - 450 kg)."""
    return validate_numeric_range(weight, 20.0, 450.0, "Weight")


def validate_target_weight(target_weight: Union[int, float]) -> Tuple[bool, str]:
    """Validates target goal weight in kg (20 - 450 kg)."""
    return validate_numeric_range(target_weight, 20.0, 450.0, "Target weight")


def validate_water(water: Union[int, float]) -> Tuple[bool, str]:
    """Validates daily water intake in liters (0 - 20 L)."""
    return validate_numeric_range(water, 0.0, 20.0, "Water intake")


def validate_sleep(sleep: Union[int, float]) -> Tuple[bool, str]:
    """Validates sleep duration in hours (0 - 24 hours)."""
    return validate_numeric_range(sleep, 0.0, 24.0, "Sleep hours")


def validate_calories(calories: Union[int, float]) -> Tuple[bool, str]:
    """Validates daily calorie consumption (0 - 15000 kcal)."""
    return validate_numeric_range(calories, 0, 15000, "Calories")


def validate_steps(steps: Union[int, float]) -> Tuple[bool, str]:
    """Validates daily step count (0 - 100000 steps)."""
    return validate_numeric_range(steps, 0, 100000, "Steps")

