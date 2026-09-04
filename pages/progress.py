"""
pages/progress.py - Daily Progress Tracking & Analytics Page for AI-FitCoach
Handles daily metric logging (date, weight, water, sleep, calories, steps, workout, notes),
Plotly visual charts (weight, water, sleep, steps, workout completion),
and starting/current/target/change/progress percentage metrics.
"""

import streamlit as st
import pandas as pd
from datetime import date
from typing import Dict, Any
from database import db
from ai.recommendations import generate_progress_recommendations
from utils.helpers import calculate_adherence_rate, export_dataframe_to_csv, format_float
from utils.validators import (
    validate_weight,
    validate_water,
    validate_sleep,
    validate_calories,
    validate_steps
)
from components.charts import (
    create_weight_trend_chart,
    create_water_chart,
    create_sleep_chart,
    create_steps_chart,
    create_workout_completion_chart,
    create_adherence_gauge
)


def render_progress_page(user: Dict[str, Any], profile: Dict[str, Any]) -> None:
    """Renders the comprehensive progress logging, analytics, and AI recommendations page."""
    user_id = user["id"]
    st.title("📈 Progress Tracking")
    st.caption("Log your daily metrics, visualize your physical progression over time, and view key milestone indicators.")

    tab1, tab2, tab3 = st.tabs(["📝 Log Daily Entry", "📊 Progress Charts & Metrics", "🤖 AI Recommendations"])

    # -------------------------------------------------------------
    # TAB 1: Log Daily Entry Form (Section 12)
    # -------------------------------------------------------------
    with tab1:
        st.subheader("Daily Metric Log")
        with st.form("daily_progress_form"):
            col1, col2 = st.columns(2)

            with col1:
                entry_date = st.date_input("Date", value=date.today())
                weight_val = st.number_input(
                    "Weight (kg)",
                    min_value=20.0,
                    max_value=450.0,
                    value=float(profile.get("weight") or profile.get("weight_kg") or 70.0),
                    step=0.1
                )
                water_val = st.number_input(
                    "Water Intake (Liters)",
                    min_value=0.0,
                    max_value=20.0,
                    value=2.5,
                    step=0.25
                )
                sleep_val = st.number_input(
                    "Sleep Duration (Hours)",
                    min_value=0.0,
                    max_value=24.0,
                    value=7.5,
                    step=0.5
                )

            with col2:
                calories_val = st.number_input(
                    "Calories Consumed (kcal)",
                    min_value=0,
                    max_value=15000,
                    value=2000,
                    step=50
                )
                steps_val = st.number_input(
                    "Steps",
                    min_value=0,
                    max_value=100000,
                    value=8000,
                    step=500
                )
                workout_completed = st.checkbox("Workout Completed Today", value=True)
                notes_val = st.text_input(
                    "Notes",
                    placeholder="e.g. Upper body hypertrophy, felt strong, good energy."
                )

            submit_log = st.form_submit_button("📥 Save Progress Entry", type="primary", use_container_width=True)

            if submit_log:
                vw, mw = validate_weight(weight_val)
                vwa, mwa = validate_water(water_val)
                vs, ms = validate_sleep(sleep_val)
                vc, mc = validate_calories(calories_val)
                vst, mst = validate_steps(steps_val)

                if not vw:
                    st.error(mw)
                elif not vwa:
                    st.error(mwa)
                elif not vs:
                    st.error(ms)
                elif not vc:
                    st.error(mc)
                elif not vst:
                    st.error(mst)
                else:
                    db.save_progress(
                        user_id=user_id,
                        date=str(entry_date),
                        weight=float(weight_val),
                        water=float(water_val),
                        sleep=float(sleep_val),
                        calories=int(calories_val),
                        workout_completed=1 if workout_completed else 0,
                        steps=int(steps_val),
                        notes=notes_val.strip()
                    )
                    st.success("✅ Progress entry successfully recorded in database!")
                    st.rerun()

    # -------------------------------------------------------------
    # TAB 2: Progress Charts & Milestone Metrics
    # -------------------------------------------------------------
    with tab2:
        logs = db.get_progress(user_id, limit=90)
        if not logs:
            st.info("Start tracking your progress to see charts and AI recommendations.")
        else:
            df = pd.DataFrame(logs)
            df["date"] = pd.to_datetime(df["date"])
            df = df.sort_values("date")

            # Calculate Starting weight, Current weight, Target weight, Weight change, Progress percentage
            starting_weight = float(profile.get("weight") or profile.get("weight_kg") or df["weight"].iloc[0])
            current_weight = float(df["weight"].iloc[-1])
            target_weight = float(profile.get("target_weight") or profile.get("target_weight_kg") or 65.0)
            weight_change = round(current_weight - starting_weight, 2)

            # Progress Percentage Calculation
            if starting_weight != target_weight:
                if starting_weight > target_weight:  # Weight loss
                    pct = ((starting_weight - current_weight) / (starting_weight - target_weight)) * 100.0
                else:  # Weight gain
                    pct = ((current_weight - starting_weight) / (target_weight - starting_weight)) * 100.0
                progress_percentage = max(0.0, min(100.0, round(pct, 1)))
            else:
                progress_percentage = 100.0

            st.subheader("🎯 Key Weight Milestones")
            m1, m2, m3, m4, m5 = st.columns(5)
            m1.metric("Starting Weight", f"{starting_weight} kg")
            m2.metric("Current Weight", f"{current_weight} kg")
            m3.metric("Target Weight", f"{target_weight} kg")
            m4.metric("Weight Change", f"{weight_change:+.1f} kg")
            m5.metric("Progress", f"{progress_percentage:.1f}%")

            st.progress(progress_percentage / 100.0)

            st.write("---")
            st.subheader("📊 Visual Progress Charts")

            # 1. Weight trend chart
            fig_w = create_weight_trend_chart(df, target_weight=target_weight)
            st.plotly_chart(fig_w, use_container_width=True)

            # 2. Water trend & 3. Sleep trend
            col_a, col_b = st.columns(2)
            with col_a:
                fig_wat = create_water_chart(df)
                st.plotly_chart(fig_wat, use_container_width=True)
            with col_b:
                fig_sleep = create_sleep_chart(df)
                st.plotly_chart(fig_sleep, use_container_width=True)

            # 4. Steps trend & 5. Workout completion
            col_c, col_d = st.columns(2)
            with col_c:
                fig_steps = create_steps_chart(df)
                st.plotly_chart(fig_steps, use_container_width=True)
            with col_d:
                fig_wo = create_workout_completion_chart(df)
                st.plotly_chart(fig_wo, use_container_width=True)

            # Adherence Gauge
            total_logged = len(df)
            completed_sessions = int(df["workout_completed"].sum())
            adherence_rate = calculate_adherence_rate(completed_sessions, total_logged)
            fig_adh = create_adherence_gauge(adherence_rate)
            st.plotly_chart(fig_adh, use_container_width=True)

            # Logged Data Table & CSV Download
            st.write("---")
            st.subheader("📋 Detailed History")
            display_df = df[["date", "weight", "water", "sleep", "calories", "steps", "workout_completed", "notes"]].copy()
            display_df["date"] = display_df["date"].dt.strftime("%Y-%m-%d")
            display_df.columns = ["Date", "Weight (kg)", "Water (L)", "Sleep (h)", "Calories (kcal)", "Steps", "Workout Completed", "Notes"]
            display_df["Workout Completed"] = display_df["Workout Completed"].apply(lambda x: "✅ Yes" if int(x) == 1 else "❌ No")
            st.dataframe(display_df.iloc[::-1], use_container_width=True, hide_index=True)

            csv_bytes = export_dataframe_to_csv(display_df)
            st.download_button(
                label="📥 Export Progress History (CSV)",
                data=csv_bytes,
                file_name=f"fitcoach_progress_{date.today()}.csv",
                mime="text/csv",
                use_container_width=True
            )

    # -------------------------------------------------------------
    # TAB 3: AI Recommendations (Section 13)
    # -------------------------------------------------------------
    with tab3:
        st.subheader("AI Recommendations Based on Progress")
        history_logs = db.get_progress(user_id, limit=30)
        if not history_logs:
            st.info("Start tracking your progress to see charts and AI recommendations.")
        else:
            st.write(f"Evaluating **{len(history_logs)}** progress entries for **{profile.get('name') or user.get('username')}**.")

            if st.button("🤖 Generate AI Progress Recommendations", type="primary", use_container_width=True):
                with st.spinner("FitCoach AI is analyzing your progress curves, consistency, and targets..."):
                    custom_key = st.session_state.get("custom_api_key", None)
                    success, rec = generate_progress_recommendations(profile, history_logs, api_key=custom_key)
                    if success:
                        st.session_state["saved_progress_recs"] = rec
                    else:
                        st.error(rec)

            if "saved_progress_recs" in st.session_state:
                st.write("---")
                st.markdown(st.session_state["saved_progress_recs"])

