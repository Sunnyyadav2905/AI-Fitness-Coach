"""
pages/bmi_calculator.py - Interactive BMI & Body Composition Calculator for AI-FitCoach
"""

import streamlit as st
import plotly.graph_objects as go
from typing import Dict, Any
from database import db
from utils.bmi import (
    calculate_bmi,
    get_bmi_category,
    get_bmi_color,
    get_bmi_explanation,
    calculate_healthy_weight_range,
    calculate_bmr
)
from utils.constants import MEDICAL_DISCLAIMER


def render_bmi_calculator_page(user: Dict[str, Any], profile: Dict[str, Any]) -> None:
    """Renders the dedicated interactive BMI & healthy weight calculator."""
    st.title("⚖️ BMI Calculator")
    st.caption("Calculate your Body Mass Index, understand your classification, and view healthy weight targets.")

    # Current profile values
    prof_h = float(profile.get("height") or profile.get("height_cm") or 170.0)
    prof_w = float(profile.get("weight") or profile.get("weight_kg") or 70.0)
    age = int(profile.get("age", 25))
    gender = profile.get("gender", "Male")

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("Input Measurements")
        height_cm = st.slider("Height (cm)", min_value=100.0, max_value=250.0, value=prof_h, step=0.5)
        weight_kg = st.slider("Weight (kg)", min_value=30.0, max_value=250.0, value=prof_w, step=0.5)

        # Calculation
        bmi = calculate_bmi(weight_kg, height_cm)
        category = get_bmi_category(bmi)
        color = get_bmi_color(category)
        explanation = get_bmi_explanation(category)
        min_w, max_w = calculate_healthy_weight_range(height_cm)
        bmr = calculate_bmr(weight_kg, height_cm, age, gender)

        if st.button("🔄 Sync with My Profile", type="primary", use_container_width=True):
            saved = db.save_profile(
                user_id=user["id"],
                name=profile.get("name") or profile.get("full_name", ""),
                age=age,
                gender=gender,
                height=height_cm,
                weight=weight_kg,
                activity_level=profile.get("activity_level", "Moderately Active"),
                fitness_goal=profile.get("fitness_goal", "Weight Loss"),
                target_weight=float(profile.get("target_weight") or profile.get("target_weight_kg") or 65.0)
            )
            if saved:
                st.success("✅ Profile height and weight updated!")
                st.rerun()

    with col2:
        st.subheader("Your Results")
        m1, m2 = st.columns(2)
        m1.metric("Current Height", f"{height_cm:.1f} cm", f"{(height_cm/100):.2f} m")
        m2.metric("Current Weight", f"{weight_kg:.1f} kg")

        m3, m4 = st.columns(2)
        m3.metric("BMI Value", f"{bmi:.2f}", f"Formula: kg/m²")
        m4.metric("BMI Category", category)

        # Plotly Gauge Chart for BMI
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=bmi,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': f"<b>{category}</b>", 'font': {'size': 18, 'color': color}},
            gauge={
                'axis': {'range': [10, 40], 'tickwidth': 1, 'tickcolor': "#94a3b8"},
                'bar': {'color': color, 'thickness': 0.35},
                'steps': [
                    {'range': [10, 18.5], 'color': '#38bdf8'},
                    {'range': [18.5, 25.0], 'color': '#22c55e'},
                    {'range': [25.0, 30.0], 'color': '#f59e0b'},
                    {'range': [30.0, 40.0], 'color': '#ef4444'}
                ],
                'threshold': {
                    'line': {'color': '#ffffff', 'width': 4},
                    'thickness': 0.75,
                    'value': bmi
                }
            }
        ))
        fig.update_layout(template="plotly_dark", height=240, margin=dict(l=20, r=20, t=30, b=20))
        st.plotly_chart(fig, use_container_width=True)

    st.write("---")

    # Detailed Explanation & Categories
    st.subheader("📘 Explanation & Health Insights")
    st.markdown(
        f"""
        <div style="background-color: #1e293b; padding: 16px 20px; border-radius: 8px; border-left: 5px solid {color}; margin-bottom: 15px;">
            <strong style="color: {color}; font-size: 1.05rem;">{category} Category Assessment:</strong>
            <p style="margin-top: 6px; color: #f8fafc; line-height: 1.5;">{explanation}</p>
            <p style="color: #94a3b8; font-size: 0.85rem; margin-bottom: 0;">
                For your height of {height_cm:.1f} cm, the normal healthy weight range is approximately <strong>{min_w} kg to {max_w} kg</strong>.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("#### BMI Category Breakdown")
    cat_df = {
        "Category": ["Underweight", "Normal", "Overweight", "Obese"],
        "BMI Range": ["< 18.5", "18.5 – 24.9", "25.0 – 29.9", "30.0+"],
        "Description": [
            "Body weight is below the standard healthy threshold. May suggest malnutrition or low muscle mass.",
            "Weight is in healthy proportion to height. Lowest relative risk for weight-related chronic conditions.",
            "Weight is above the normal range for height. Increased risk for hypertension and cardiometabolic issues.",
            "Excessive accumulation of adipose tissue. High clinical risk; physician guidance advised."
        ]
    }
    st.dataframe(cat_df, use_container_width=True, hide_index=True)

    # Mandatory Medical Disclaimer (Section 7)
    st.info(
        "ℹ️ **Clinical Note**: BMI is a general screening measure and not a medical diagnosis. "
        "It does not directly measure body fat percentage, muscle mass, bone density, or overall metabolic health. "
        "Athletes with higher muscle mass may show a higher BMI while maintaining very healthy body composition."
    )

