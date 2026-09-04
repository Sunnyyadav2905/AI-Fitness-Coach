"""
utils/bmi.py - Scientific Body Composition & Metabolic Calculator
Calculates BMI, WHO classification categories, healthy weight boundaries,
Basal Metabolic Rate (BMR via Mifflin-St Jeor), TDEE, macronutrient distributions,
and fluid hydration requirements.
"""

from typing import Tuple, Dict, Any


def calculate_bmi(weight: float, height: float) -> float:
    """
    Calculates Body Mass Index (BMI).
    Formula: weight (kg) / (height (m))^2
    Height input is in cm and converted to meters.
    Rounds BMI to two decimal places.
    """
    if height <= 0 or weight <= 0:
        return 0.0
    height_m = height / 100.0
    return round(weight / (height_m ** 2), 2)


def get_bmi_category(bmi: float) -> str:
    """
    Returns the BMI category string.
    BMI < 18.5 -> Underweight
    18.5 - 24.9 -> Normal
    25 - 29.9 -> Overweight
    30+ -> Obese
    """
    if bmi <= 0:
        return "Unknown"
    elif bmi < 18.5:
        return "Underweight"
    elif bmi < 25.0:
        return "Normal"
    elif bmi < 30.0:
        return "Overweight"
    else:
        return "Obese"


def calculate_bmi_and_category(weight: float, height: float) -> Tuple[float, str]:
    """Calculates BMI and returns (bmi_value, category)."""
    bmi = calculate_bmi(weight, height)
    category = get_bmi_category(bmi)
    return bmi, category


def get_bmi_color(category: str) -> str:
    """Returns hexadecimal color code for UI cards and badges."""
    colors = {
        "Underweight": "#38bdf8",
        "Normal": "#22c55e",
        "Overweight": "#f59e0b",
        "Obese": "#ef4444",
        "Unknown": "#64748b"
    }
    return colors.get(category, "#64748b")


def get_bmi_explanation(category: str) -> str:
    """Returns educational explanation for a BMI category."""
    explanations = {
        "Underweight": (
            "Your BMI is below 18.5, indicating you may be underweight. Focus on nutrient-dense meals "
            "with healthy fats, lean proteins, and complex carbohydrates, alongside progressive resistance training."
        ),
        "Normal": (
            "Your BMI is within the healthy reference range (18.5–24.9). Maintain this balanced metabolic state "
            "with consistent strength/cardio training, adequate hydration, and balanced whole-food nutrition."
        ),
        "Overweight": (
            "Your BMI is between 25.0 and 29.9, which falls in the overweight range. A moderate calorie deficit "
            "(300–500 kcal/day) combined with regular daily activity and resistance training can support healthy fat loss."
        ),
        "Obese": (
            "Your BMI is 30.0 or higher. Prioritize sustainable lifestyle changes, consistent daily walking, "
            "mindful portion control, and consult a qualified healthcare provider for personalized medical support."
        ),
        "Unknown": "Please provide valid height and weight values to calculate your BMI."
    }
    return explanations.get(category, "General health guidance: stay active and eat a balanced diet.")



def calculate_healthy_weight_range(height_cm: float) -> Tuple[float, float]:
    """
    Returns healthy weight range (min_kg, max_kg) corresponding
    to the normal BMI range (18.5 - 24.9).
    """
    if height_cm <= 0:
        return 0.0, 0.0
    height_m = height_cm / 100.0
    min_w = round(18.5 * (height_m ** 2), 1)
    max_w = round(24.9 * (height_m ** 2), 1)
    return min_w, max_w


def calculate_bmr(weight_kg: float, height_cm: float, age: int, gender: str) -> float:
    """
    Calculates Basal Metabolic Rate using the Mifflin-St Jeor formula.
    Men: BMR = 10 * W(kg) + 6.25 * H(cm) - 5 * A(years) + 5
    Women: BMR = 10 * W(kg) + 6.25 * H(cm) - 5 * A(years) - 161
    """
    if weight_kg <= 0 or height_cm <= 0 or age <= 0:
        return 0.0
    base = (10.0 * weight_kg) + (6.25 * height_cm) - (5.0 * age)
    if str(gender).strip().lower().startswith("m"):
        bmr = base + 5.0
    else:
        bmr = base - 161.0
    return round(max(bmr, 800.0), 1)


def calculate_tdee(bmr: float, activity_level: str) -> float:
    """
    Calculates Total Daily Energy Expenditure (TDEE).
    """
    from utils.constants import ACTIVITY_MULTIPLIERS

    mult = 1.375
    act_str = str(activity_level).lower()
    for name, factor in ACTIVITY_MULTIPLIERS.items():
        key_term = name.lower().split()[0]
        if key_term in act_str:
            mult = factor
            break
    return round(bmr * mult, 0)


def calculate_macro_targets(
    tdee: float, fitness_goal: str, diet_preference: str = "Balanced"
) -> Dict[str, Any]:
    """
    Calculates target calories and macronutrient breakdown (protein, carbs, fat) in grams and percentages.
    """
    goal_str = str(fitness_goal).lower()
    diet_str = str(diet_preference).lower()

    if "loss" in goal_str or "cut" in goal_str:
        target_calories = max(1200, int(tdee - 500))  # 500 kcal deficit
        ratio = {"protein": 0.35, "carbs": 0.35, "fat": 0.30}
    elif "muscle" in goal_str or "gain" in goal_str or "bulk" in goal_str:
        target_calories = int(tdee + 350)  # Lean bulk surplus
        ratio = {"protein": 0.30, "carbs": 0.50, "fat": 0.20}
    elif "endurance" in goal_str:
        target_calories = int(tdee)
        ratio = {"protein": 0.25, "carbs": 0.55, "fat": 0.20}
    else:  # Maintenance
        target_calories = int(tdee)
        ratio = {"protein": 0.25, "carbs": 0.50, "fat": 0.25}

    # Dietary modifications
    if "keto" in diet_str:
        ratio = {"protein": 0.25, "carbs": 0.05, "fat": 0.70}
    elif "low-carb" in diet_str or "low carb" in diet_str:
        ratio = {"protein": 0.35, "carbs": 0.20, "fat": 0.45}

    protein_g = round((target_calories * ratio["protein"]) / 4.0)
    carbs_g = round((target_calories * ratio["carbs"]) / 4.0)
    fat_g = round((target_calories * ratio["fat"]) / 9.0)

    return {
        "target_calories": target_calories,
        "protein_g": protein_g,
        "carbs_g": carbs_g,
        "fat_g": fat_g,
        "protein_pct": int(ratio["protein"] * 100),
        "carbs_pct": int(ratio["carbs"] * 100),
        "fat_pct": int(ratio["fat"] * 100)
    }


def calculate_water_target(weight_kg: float, workout_active: bool = True) -> float:
    """
    Calculates recommended daily water intake in liters.
    35 ml per kg bodyweight + 0.5L for training session.
    """
    if weight_kg <= 0:
        return 2.5
    target = (weight_kg * 35.0) / 1000.0
    if workout_active:
        target += 0.5
    return round(max(target, 2.0), 1)
