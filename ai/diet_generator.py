"""
ai/diet_generator.py - AI Meal & Nutrition Plan Generator for AI-FitCoach
Produces personalized macronutrient-balanced meal plans, hydration advice,
and nutrition guidance using OpenAI GPT.
"""

from typing import Dict, Any, Optional, Tuple
from ai.openai_client import generate_completion, DIET_SYSTEM_PROMPT
from database import db
from utils.constants import MEDICAL_DISCLAIMER


def generate_diet_plan(
    profile: Dict[str, Any],
    preferences: Dict[str, Any],
    api_key: Optional[str] = None,
    user_id: Optional[int] = None
) -> Tuple[bool, str]:
    """
    Generates personalized meal suggestions matching user metrics, dietary style, and allergies.
    Saves the plan into SQLite if user_id is provided.
    Returns (success: bool, plan_markdown: str).
    """
    name = profile.get("name") or profile.get("full_name", "Athlete")
    age = profile.get("age", 25)
    gender = profile.get("gender", "Male")
    height = profile.get("height") or profile.get("height_cm", 170.0)
    weight = profile.get("weight") or profile.get("weight_kg", 70.0)
    target_weight = profile.get("target_weight") or profile.get("target_weight_kg", 65.0)
    activity_level = profile.get("activity_level", "Moderately Active")
    fitness_goal = profile.get("fitness_goal", "Weight Loss")

    dietary_pref = preferences.get("dietary_preference", preferences.get("diet_preference", "Vegetarian"))
    allergies = preferences.get("allergies", preferences.get("medical_notes", "None"))
    num_meals = preferences.get("num_meals", preferences.get("meals_per_day", 4))

    prompt = f"""
Create a personalized, evidence-based daily meal plan and nutrition guide for this user:

**User Profile & Metrics:**
- Name: {name}
- Age: {age} years
- Gender: {gender}
- Height: {height} cm
- Current Weight: {weight} kg
- Target Weight: {target_weight} kg
- Activity Level: {activity_level}
- Fitness Goal: {fitness_goal}

**Dietary Specifications:**
- Dietary Preference: {dietary_pref} (e.g., Vegetarian, Non-Vegetarian, Vegan, Eggetarian, Indian, Custom)
- Allergies / Foods to Avoid: {allergies}
- Number of Meals Requested: {num_meals} meals per day

**Required Response Structure (Formatted in clear GitHub Markdown):**
1. **Target Calorie & Macro Estimate**: Estimated daily calories (no dangerous extreme deficits) and protein/carbs/fat targets.
2. **Daily Meals Breakdown**:
   - **Breakfast**: Ingredients, portions, and quick preparation notes
   - **Morning Snack**: Nutrient-dense fuel
   - **Lunch**: Balanced main course with protein & complex carbs
   - **Evening Snack**: Pre- or post-workout energy
   - **Dinner**: Wholesome, satisfying meal supporting overnight recovery
3. **Hydration Suggestions**: Daily fluid intake volume (liters) and electrolyte guidance.
4. **General Nutrition Guidance**: Practical sustainable eating habits, whole-food swaps, and dining-out tips.
"""

    success, content = generate_completion(
        prompt=prompt,
        system_message=DIET_SYSTEM_PROMPT,
        api_key=api_key,
        temperature=0.7,
        max_tokens=2500
    )

    if not success:
        offline_diet = generate_fallback_diet_plan(profile, preferences)
        final_plan = (
            f"> 💡 **Offline Metabolic Engine Active**: Generated using nutritional physiology formulas because an active OpenAI API key was not detected. "
            f"Add your API key in the sidebar anytime for real-time GPT-4o-mini generation.\n\n"
            f"{offline_diet}\n\n---\n\n{MEDICAL_DISCLAIMER}"
        )
    else:
        final_plan = f"{content.strip()}\n\n---\n\n{MEDICAL_DISCLAIMER}"

    if user_id:
        try:
            db.save_diet_plan(user_id=user_id, plan=final_plan)
        except Exception as e:
            print(f"Error saving diet plan to DB: {e}")

    return True, final_plan


def generate_fallback_diet_plan(profile: Dict[str, Any], preferences: Dict[str, Any]) -> str:
    """Generates an evidence-based daily meal plan and macro distribution without external API calls."""
    from utils.bmi import calculate_bmr, calculate_tdee, calculate_macro_targets, calculate_water_target

    name = profile.get("name") or profile.get("full_name", "Athlete")
    age = int(profile.get("age", 25))
    gender = profile.get("gender", "Male")
    height = float(profile.get("height") or profile.get("height_cm", 170.0))
    weight = float(profile.get("weight") or profile.get("weight_kg", 70.0))
    activity = profile.get("activity_level", "Moderately Active")
    goal = profile.get("fitness_goal", "Weight Loss")

    dietary_pref = preferences.get("dietary_preference", preferences.get("diet_preference", "Vegetarian"))
    allergies = preferences.get("allergies", preferences.get("medical_notes", "None"))
    num_meals = preferences.get("num_meals", preferences.get("meals_per_day", 4))

    bmr = calculate_bmr(weight, height, age, gender)
    tdee = calculate_tdee(bmr, activity)
    targets = calculate_macro_targets(tdee, goal)
    water_l = calculate_water_target(weight)

    target_cal = targets["target_calories"]
    p_g = targets["protein_g"]
    c_g = targets["carbs_g"]
    f_g = targets["fat_g"]

    is_veg = "veg" in dietary_pref.lower() and "non" not in dietary_pref.lower()
    is_vegan = "vegan" in dietary_pref.lower()
    is_egg = "egg" in dietary_pref.lower()

    if is_vegan:
        p_sources = "Tofu, Tempeh, Lentils, Chickpeas, Edamame, Pea Protein"
        b_item = "Overnight oats with chia seeds, soy milk, plant-based protein powder, and fresh berries."
        l_item = "Warm quinoa bowl with roasted spiced chickpeas, sautéed tofu cubes, avocado, and steamed broccoli with tahini drizzle."
        d_item = "Hearty red lentil curry (Dal) served with brown basmati rice, steamed asparagus, and baby spinach salad."
    elif is_veg or is_egg:
        p_sources = "Paneer, Greek Yogurt, Whey Isolate, Eggs, Lentils, Cottage Cheese"
        b_item = "3 scrambled eggs (or 100g grilled paneer bhurji) with 2 slices of 100% whole grain toast and sliced avocado."
        l_item = "150g grilled low-fat paneer or seasoned tofu, 1 cup cooked brown rice, and a bowl of mixed dal with steamed greens."
        d_item = "High-protein vegetable & lentil stew, 1 multigrain roti, mixed green salad with olive oil and fresh lemon."
    else: # Non-veg
        p_sources = "Chicken Breast, Turkey, Atlantic Salmon, Whole Eggs, Greek Yogurt, Whey"
        b_item = "3 whole eggs scrambled with baby spinach and mushrooms, paired with 60g rolled oats cooked in water with cinnamon."
        l_item = "180g herb-grilled chicken breast or lean ground turkey, 150g sweet potato or brown rice, and steamed green beans."
        d_item = "180g pan-seared salmon fillet or white fish with baked asparagus, roasted zucchini, and mixed garden salad."

    md = f"""# 🥗 Personalized Daily Nutrition & Meal Plan

**Client:** {name} | **Dietary Style:** {dietary_pref} | **Goal:** {goal}  
**Caloric Target:** ~{target_cal} kcal/day | **Water Intake:** ~{water_l} Liters/day  
**Excluded / Allergies:** {allergies}

---

## 📊 Target Macronutrient Distribution
| Nutrient | Daily Target | % of Total Energy | Purpose |
| :--- | :--- | :--- | :--- |
| **Protein** | **{p_g} grams** | ~{int((p_g * 4 / target_cal) * 100)}% | Muscle synthesis, metabolic support & satiety |
| **Carbohydrates** | **{c_g} grams** | ~{int((c_g * 4 / target_cal) * 100)}% | Glycogen replenishment & daily energy |
| **Healthy Fats** | **{f_g} grams** | ~{int((f_g * 9 / target_cal) * 100)}% | Hormone regulation & joint lubrication |

**Recommended Protein Sources:** {p_sources}

---

## 🍽️ Daily Meal Schedule ({num_meals} Meals)

### 🍳 Meal 1: Breakfast (Power Starter)
* **Dish:** {b_item}
* **Hydration:** 500ml water + black coffee or green tea (antioxidant support).
* **Estimated:** ~{int(target_cal * 0.25)} kcal | ~{int(p_g * 0.25)}g Protein

### 🍏 Meal 2: Mid-Morning Micronutrient Snack
* **Dish:** 170g 0% plain Greek yogurt (or plant yogurt) with 15g raw almonds and a small green apple.
* **Estimated:** ~{int(target_cal * 0.15)} kcal | ~{int(p_g * 0.15)}g Protein

### 🥗 Meal 3: Balanced Lunch
* **Dish:** {l_item}
* **Estimated:** ~{int(target_cal * 0.30)} kcal | ~{int(p_g * 0.30)}g Protein

### ⚡ Meal 4: Afternoon Energy / Pre-Workout Primer
* **Dish:** 1 medium banana paired with 1 scoop Whey/Plant protein isolate in 300ml cold water (or a handful of roasted edamame).
* **Estimated:** ~{int(target_cal * 0.10)} kcal | ~{int(p_g * 0.15)}g Protein

### 🍲 Meal 5: Recovery Dinner
* **Dish:** {d_item}
* **Estimated:** ~{int(target_cal * 0.20)} kcal | ~{int(p_g * 0.15)}g Protein

---

## 💧 Hydration & Sustainable Habits
* **Baseline Goal:** Drink **{water_l} Liters** of clean water distributed evenly between waking and 8:00 PM.
* **The 80/20 Rule:** Keep 80%+ of daily nutrition from unrefined, nutrient-dense whole foods. Allow 20% flexibility for social enjoyment.
"""
    return md


def generate_meal_plan(
    profile: Dict[str, Any],
    targets: Dict[str, Any],
    preferences: Dict[str, Any],
    api_key: Optional[str] = None
) -> str:
    """Backwards-compatible wrapper returning markdown string directly."""
    combined_prefs = dict(preferences)
    combined_prefs.update(targets)
    success, plan = generate_diet_plan(profile, combined_prefs, api_key=api_key)
    return plan

