"""
tests/test_validators.py - Unit Tests for Input Validators
"""

import pytest
from utils.validators import (
    validate_email,
    validate_username,
    validate_password,
    validate_numeric_range,
    validate_age,
    validate_height,
    validate_weight,
    validate_target_weight,
    validate_water,
    validate_sleep,
    validate_calories,
    validate_steps
)


def test_validate_email():
    ok1, _ = validate_email("user@example.com")
    assert ok1 is True
    ok2, _ = validate_email("fitness.coach+test@domain.co.in")
    assert ok2 is True
    ok3, _ = validate_email("invalid-email")
    assert ok3 is False
    ok4, _ = validate_email("@no-user.com")
    assert ok4 is False
    ok5, _ = validate_email("")
    assert ok5 is False


def test_validate_username():
    ok, _ = validate_username("john_doe")
    assert ok is True

    short, msg = validate_username("ab")
    assert short is False
    assert "at least 3 characters" in msg

    invalid, _ = validate_username("user with spaces!")
    assert invalid is False


def test_validate_password():
    ok, _ = validate_password("secret123")
    assert ok is True

    short, msg = validate_password("12345")
    assert short is False
    assert "at least 6 characters" in msg


def test_validate_numeric_range():
    ok, _ = validate_numeric_range(75, 30, 250, "Weight")
    assert ok is True

    under, _ = validate_numeric_range(20, 30, 250, "Weight")
    assert under is False

    over, _ = validate_numeric_range(300, 30, 250, "Weight")
    assert over is False

    negative, _ = validate_numeric_range(-10, 0, 100, "Weight")
    assert negative is False

    bad_type, _ = validate_numeric_range("not_a_number", 30, 250, "Weight")
    assert bad_type is False


def test_specific_metrics_validation():
    # Age
    assert validate_age(25)[0] is True
    assert validate_age(3)[0] is False
    assert validate_age(-5)[0] is False

    # Height
    assert validate_height(175.0)[0] is True
    assert validate_height(30.0)[0] is False

    # Weight & Target Weight
    assert validate_weight(70.0)[0] is True
    assert validate_weight(10.0)[0] is False
    assert validate_target_weight(65.0)[0] is True
    assert validate_target_weight(-65.0)[0] is False

    # Water & Sleep
    assert validate_water(3.0)[0] is True
    assert validate_water(-1.0)[0] is False
    assert validate_sleep(8.0)[0] is True
    assert validate_sleep(30.0)[0] is False

    # Calories & Steps
    assert validate_calories(2200)[0] is True
    assert validate_calories(-500)[0] is False
    assert validate_steps(10000)[0] is True
    assert validate_steps(-100)[0] is False

