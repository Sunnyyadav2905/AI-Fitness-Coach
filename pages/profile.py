"""
pages/profile.py - User Profile Management Page for AI-FitCoach
"""

import streamlit as st
from typing import Dict, Any
from database import db
from utils.constants import ACTIVITY_LEVELS, FITNESS_GOALS, GENDERS, DIETARY_PREFERENCES
from utils.validators import validate_age, validate_height, validate_weight, validate_target_weight
from utils.bmi import (
    calculate_bmi,
    get_bmi_category,
    calculate_bmr,
    calculate_tdee,
    calculate_macro_targets
)


def render_profile_page(user: Dict[str, Any], profile: Dict[str, Any]) -> None:
    """Renders the user profile editing form and biometric calculator."""
    st.title("👤 My Profile & Fitness Goals")
    st.caption("Update your physical measurements and fitness ambitions to tailor your AI plans.")

    # Retrieve current values
    curr_name = profile.get("name") or profile.get("full_name") or user.get("username", "").capitalize()
    curr_age = int(profile.get("age", 25))
    curr_gender = profile.get("gender", "Male")
    curr_height = float(profile.get("height") or profile.get("height_cm") or 170.0)
    curr_weight = float(profile.get("weight") or profile.get("weight_kg") or 70.0)
    curr_target_weight = float(profile.get("target_weight") or profile.get("target_weight_kg") or 65.0)
    curr_activity = profile.get("activity_level", "Moderately Active")
    curr_goal = profile.get("fitness_goal", "Weight Loss")
    curr_diet = profile.get("dietary_preference") or profile.get("diet_preference") or "Non-Vegetarian"
    curr_medical = profile.get("medical_notes", "") or ""

    # Profile completion check (Section 6)
    completed_fields = 0
    total_fields = 8
    if curr_name: completed_fields += 1
    if curr_age > 0: completed_fields += 1
    if curr_gender: completed_fields += 1
    if curr_height > 0: completed_fields += 1
    if curr_weight > 0: completed_fields += 1
    if curr_target_weight > 0: completed_fields += 1
    if curr_activity: completed_fields += 1
    if curr_goal: completed_fields += 1

    completion_pct = int((completed_fields / total_fields) * 100)
    st.progress(completion_pct / 100.0, text=f"Profile Completion: {completion_pct}% Complete")

    st.markdown("### 📝 Edit & Submit Profile Details")

    with st.form("profile_form", clear_on_submit=False):
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### Personal & Physical Attributes")
            name = st.text_input("Full Name", value=curr_name, placeholder="e.g. Alex Johnson")
            age = st.number_input("Age (years)", min_value=10, max_value=100, value=curr_age, step=1)

            gender_idx = GENDERS.index(curr_gender) if curr_gender in GENDERS else 0
            gender = st.selectbox("Gender", GENDERS, index=gender_idx)

            height = st.number_input("Height (cm)", min_value=100.0, max_value=250.0, value=curr_height, step=0.5)
            weight = st.number_input("Weight (kg)", min_value=30.0, max_value=300.0, value=curr_weight, step=0.5)

        with col2:
            st.markdown("#### Goals & Lifestyle Preferences")
            target_weight = st.number_input("Target Weight (kg)", min_value=30.0, max_value=300.0, value=curr_target_weight, step=0.5)

            act_idx = ACTIVITY_LEVELS.index(curr_activity) if curr_activity in ACTIVITY_LEVELS else 2
            activity_level = st.selectbox("Activity Level", ACTIVITY_LEVELS, index=act_idx)

            goal_idx = FITNESS_GOALS.index(curr_goal) if curr_goal in FITNESS_GOALS else 0
            fitness_goal = st.selectbox("Fitness Goal", FITNESS_GOALS, index=goal_idx)

            diet_idx = DIETARY_PREFERENCES.index(curr_diet) if curr_diet in DIETARY_PREFERENCES else 1
            dietary_preference = st.selectbox("Dietary Preference", DIETARY_PREFERENCES, index=diet_idx)

        st.markdown("#### Medical Conditions & Health Notes")
        medical_notes = st.text_area(
            "Medical Conditions / Injuries / Health Notes (Optional)",
            value=curr_medical,
            placeholder="e.g., Mild lower back tightness, asthma, knee surgery in 2024, etc."
        )

        st.write("")
        # Clear, prominent Submit Button (Section 6)
        col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
        with col_btn2:
            submit = st.form_submit_button("Submit Profile", type="primary", use_container_width=True)

        if submit:
            v_age, m_age = validate_age(age)
            v_h, m_h = validate_height(height)
            v_w, m_w = validate_weight(weight)
            v_tw, m_tw = validate_target_weight(target_weight)

            if not v_age:
                st.error(f"Validation Error: {m_age}")
            elif not v_h:
                st.error(f"Validation Error: {m_h}")
            elif not v_w:
                st.error(f"Validation Error: {m_w}")
            elif not v_tw:
                st.error(f"Validation Error: {m_tw}")
            else:
                saved = db.save_profile(
                    user_id=user["id"],
                    name=name.strip(),
                    age=int(age),
                    gender=gender,
                    height=float(height),
                    weight=float(weight),
                    activity_level=activity_level,
                    fitness_goal=fitness_goal,
                    target_weight=float(target_weight),
                    dietary_preference=dietary_preference,
                    medical_notes=medical_notes.strip()
                )
                if saved:
                    new_bmi = calculate_bmi(float(weight), float(height))
                    new_cat = get_bmi_category(new_bmi)
                    st.success(f"✅ Profile submitted and saved successfully! Auto-calculated BMI: **{new_bmi}** ({new_cat}).")
                    st.rerun()
                else:
                    st.error("Error saving profile to database. Please try again.")

    # Dynamic Metabolic Preview (Section 6 auto-calculation)
    st.write("---")
    st.subheader("🔬 Estimated Caloric & Energy Requirements")
    c1, c2, c3, c4 = st.columns(4)
    bmi = calculate_bmi(curr_weight, curr_height)
    cat = get_bmi_category(bmi)
    bmr = calculate_bmr(curr_weight, curr_height, curr_age, curr_gender)
    tdee = calculate_tdee(bmr, curr_activity)
    targets = calculate_macro_targets(tdee, curr_goal)

    c1.metric("Current BMI", f"{bmi}", f"{cat}")
    c2.metric("Basal Metabolic Rate", f"{int(bmr)} kcal", "BMR baseline")
    c3.metric("Estimated TDEE", f"{int(tdee)} kcal", "Daily energy expenditure")
    c4.metric("Suggested Daily Calories", f"{targets['target_calories']} kcal", f"{targets['protein_g']}g P • {targets['carbs_g']}g C • {targets['fat_g']}g F")


