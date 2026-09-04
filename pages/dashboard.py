"""
pages/dashboard.py - Main User Dashboard Page for AI-FitCoach
"""

import streamlit as st
import pandas as pd
from typing import Dict, Any
from database import db
from utils.bmi import calculate_bmi, get_bmi_category, get_bmi_color
from utils.constants import DAILY_TIPS_COLLECTION
from components.cards import render_metric_card, render_tip_card
from components.charts import create_weight_trend_chart
from ai.recommendations import generate_progress_recommendations


def render_dashboard_page(user: Dict[str, Any], profile: Dict[str, Any]) -> None:
    """Renders the executive dashboard with biometric status and quick shortcuts."""
    user_id = user["id"]
    name = profile.get("name") or profile.get("full_name") or user.get("username", "Athlete")
    st.markdown(f"# Welcome back, {name}!")
    st.caption("Here is your personal fitness and wellness overview for today.")

    # Biometric Data
    weight = float(profile.get("weight") or profile.get("weight_kg") or 70.0)
    target_weight = float(profile.get("target_weight") or profile.get("target_weight_kg") or 65.0)
    height = float(profile.get("height") or profile.get("height_cm") or 170.0)
    goal = profile.get("fitness_goal", "General Fitness")

    # Fetch recent progress
    recent_logs = db.get_progress(user_id, limit=30)
    latest_log = recent_logs[-1] if recent_logs else {}

    # Extract dynamic stats from latest log if available
    current_weight = float(latest_log.get("weight", weight)) if latest_log.get("weight") is not None else weight
    workout_done = int(latest_log.get("workout_completed", 0)) == 1 if latest_log else False
    workout_status = "✅ Completed" if workout_done else "⏳ Pending / Rest"
    water_val = float(latest_log.get("water", 0.0)) if latest_log.get("water") is not None else 0.0
    water_display = f"{water_val:.1f} L" if water_val > 0 else "Not logged yet"

    # BMI calculation
    bmi = calculate_bmi(current_weight, height)
    category = get_bmi_category(bmi)
    bmi_color = get_bmi_color(category)

    # -------------------------------------------------------------
    # 6 Specified Dashboard Cards (Section 14)
    # -------------------------------------------------------------
    st.subheader("📊 Your Fitness Metrics")
    c1, c2, c3 = st.columns(3)
    with c1:
        render_metric_card("Current Weight", f"{current_weight} kg", f"Starting: {weight} kg")
    with c2:
        render_metric_card("Target Weight", f"{target_weight} kg", f"Goal: {goal}")
    with c3:
        render_metric_card("BMI", f"{bmi}", f"Category: {category}", color=bmi_color)

    c4, c5, c6 = st.columns(3)
    with c4:
        render_metric_card("Fitness Goal", goal, "Active Program")
    with c5:
        render_metric_card("Workout Status", workout_status, "Today's Session")
    with c6:
        render_metric_card("Water Intake", water_display, "Daily Hydration")

    st.markdown("---")

    # -------------------------------------------------------------
    # Weight Progress Chart & Daily Tip
    # -------------------------------------------------------------
    col_left, col_right = st.columns([3, 2])

    with col_left:
        st.subheader("📈 Weight Progress Trend")
        if len(recent_logs) >= 2:
            df = pd.DataFrame(recent_logs)
            chart = create_weight_trend_chart(df, target_weight=target_weight)
            st.plotly_chart(chart, use_container_width=True)
        elif len(recent_logs) == 1:
            st.info("You have logged 1 entry so far. Log at least 2 entries to see the weight trend chart!")
        else:
            st.info("Start tracking your progress to see charts and AI recommendations.")

    with col_right:
        st.subheader("💡 Daily Fitness Tip")
        tip_item = DAILY_TIPS_COLLECTION[0]
        render_tip_card(tip_item["category"], tip_item["tip"])

        st.subheader("🤖 AI Recommendation")
        if recent_logs:
            custom_key = st.session_state.get("custom_api_key")
            with st.spinner("Analyzing your recent progress..."):
                ok, rec = generate_progress_recommendations(profile, recent_logs, api_key=custom_key)
            if ok:
                st.markdown(
                    f"""
                    <div style="background-color: #1e293b; padding: 14px 16px; border-radius: 8px; border-left: 4px solid #38bdf8;">
                        <div style="font-size: 0.9rem; color: #f8fafc; line-height: 1.5;">{rec[:320]}...</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            else:
                st.info(rec)
        else:
            st.info("Start tracking your progress to see charts and AI recommendations.")

    st.markdown("---")

    # -------------------------------------------------------------
    # Recent Activity Table
    # -------------------------------------------------------------
    st.subheader("🕒 Recent Activity")
    if recent_logs:
        display_df = pd.DataFrame(recent_logs)[["date", "weight", "water", "sleep", "calories", "workout_completed", "steps", "notes"]]
        display_df.columns = ["Date", "Weight (kg)", "Water (L)", "Sleep (h)", "Calories (kcal)", "Workout", "Steps", "Notes"]
        display_df["Workout"] = display_df["Workout"].apply(lambda x: "✅ Completed" if int(x) == 1 else "❌ Rest/Missed")
        st.dataframe(display_df.iloc[::-1].head(7), use_container_width=True, hide_index=True)
    else:
        st.info("No activity recorded yet. Go to **Progress Tracking** to log today's workout, water, and weight!")

