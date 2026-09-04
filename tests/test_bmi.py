"""
tests/test_bmi.py - Unit Tests for BMI & Metabolic Calculations
"""

import pytest
from utils.bmi import (
    calculate_bmi,
    get_bmi_category,
    calculate_bmi_and_category,
    calculate_healthy_weight_range,
    calculate_bmr,
    calculate_tdee,
    calculate_macro_targets,
    calculate_water_target
)


def test_calculate_bmi_normal():
    # 70 kg, 175 cm -> 70 / (1.75^2) = 22.857... -> 22.86 (2 decimal places)
    bmi = calculate_bmi(70.0, 175.0)
    assert bmi == 22.86
    cat = get_bmi_category(bmi)
    assert cat == "Normal"


def test_calculate_bmi_underweight():
    # 45 kg, 170 cm -> 45 / (1.7^2) = 15.57
    bmi = calculate_bmi(45.0, 170.0)
    assert bmi < 18.5
    cat = get_bmi_category(bmi)
    assert cat == "Underweight"


def test_calculate_bmi_overweight():
    # 80 kg, 170 cm -> 80 / (1.7^2) = 27.68
    bmi = calculate_bmi(80.0, 170.0)
    assert 25.0 <= bmi <= 29.9
    cat = get_bmi_category(bmi)
    assert cat == "Overweight"


def test_calculate_bmi_obese():
    # 105 kg, 170 cm -> 105 / (1.7^2) = 36.33
    bmi = calculate_bmi(105.0, 170.0)
    assert bmi >= 30.0
    cat = get_bmi_category(bmi)
    assert cat == "Obese"


def test_calculate_bmi_invalid_values():
    assert calculate_bmi(0, 170) == 0.0
    assert calculate_bmi(70, 0) == 0.0
    assert calculate_bmi(-50, 170) == 0.0
    assert calculate_bmi(70, -170) == 0.0
    assert get_bmi_category(0.0) == "Unknown"
    assert get_bmi_category(-5.0) == "Unknown"


def test_calculate_bmi_and_category():
    bmi, cat = calculate_bmi_and_category(68.0, 172.0)
    assert isinstance(bmi, float)
    assert cat == "Normal"


def test_calculate_healthy_weight_range():
    min_w, max_w = calculate_healthy_weight_range(180.0)
    # 1.8^2 = 3.24; 18.5*3.24 = 59.94 -> 59.9; 24.9*3.24 = 80.676 -> 80.7
    assert min_w == 59.9
    assert max_w == 80.7


def test_calculate_bmr():
    # Male: 10*80 + 6.25*180 - 5*25 + 5 = 800 + 1125 - 125 + 5 = 1805
    bmr_m = calculate_bmr(80.0, 180.0, 25, "Male")
    assert bmr_m == 1805.0

    # Female: 10*60 + 6.25*165 - 5*30 - 161 = 600 + 1031.25 - 150 - 161 = 1320.25 -> 1320.2 or 1320.3
    bmr_f = calculate_bmr(60.0, 165.0, 30, "Female")
    assert 1320.0 <= bmr_f <= 1321.0


def test_calculate_tdee():
    bmr = 1800.0
    tdee = calculate_tdee(bmr, "Moderately Active")
    assert tdee == 2790.0


def test_calculate_macro_targets():
    tdee = 2500.0
    targets_cut = calculate_macro_targets(tdee, "Weight Loss")
    assert targets_cut["target_calories"] == 2000  # 2500 - 500
    assert targets_cut["protein_g"] > 0
    assert targets_cut["carbs_g"] > 0
    assert targets_cut["fat_g"] > 0


def test_calculate_water_target():
    water = calculate_water_target(70.0, workout_active=True)
    assert water >= 2.5

