"""
pages/workout.py - AI Workout Plan Generator Page for AI-FitCoach
"""

import streamlit as st
from datetime import date
from typing import Dict, Any
from database import db
from ai.gemini_client import is_gemini_configured
from ai.workout_generator import generate_workout_plan
from utils.constants import WORKOUT_SPLITS, EQUIPMENT_OPTIONS, EXPERIENCE_LEVELS


def render_workout_page(user: Dict[str, Any], profile: Dict[str, Any]) -> None:
    """Renders the workout generation and saved workout management page."""
    user_id = user["id"]
    custom_key = st.session_state.get("custom_api_key", None)
    ai_online = is_gemini_configured(custom_key)

    st.title("🏋️ Workout Generator")
    st.caption("Generate an evidence-based, customized resistance and conditioning plan tailored to your profile and equipment.")

    tab1, tab2 = st.tabs(["✨ Generate New Plan", "📁 Saved Workout Plans"])

    with tab1:
        # Check if profile exists
        if not profile or not profile.get("name") and not profile.get("full_name"):
            st.info("💡 Complete your profile in **My Profile** to unlock personalized recommendations.")

        st.subheader("Workout Configuration")
        col1, col2 = st.columns(2)

        with col1:
            split_type = st.selectbox("Preferred Workout Split", WORKOUT_SPLITS)
            days_per_week = st.slider("Available Workout Days (per week)", min_value=1, max_value=7, value=4)
            experience = st.selectbox("Fitness Experience Level", EXPERIENCE_LEVELS, index=1)

        with col2:
            equipment = st.selectbox("Equipment Availability", EQUIPMENT_OPTIONS)
            duration = st.select_slider("Target Session Duration (Minutes)", options=[20, 30, 45, 60, 75, 90], value=45)

        if ai_online:
            st.caption("🟢 **AI Engine Active:** Google Gemini (gemini-1.5-flash)")
        else:
            st.caption("🟡 **Engine Mode:** Offline Template Engine (Enter Gemini API key in sidebar to enable live Gemini)")

        if st.button("🚀 Generate Personalized Workout Plan", type="primary", use_container_width=True):
            preferences = {
                "split_type": split_type,
                "days_per_week": days_per_week,
                "duration": duration,
                "equipment": equipment,
                "experience": experience
            }
            custom_key = st.session_state.get("custom_api_key", None)

            with st.spinner("FitCoach AI is formulating your personalized workout routine..."):
                success, plan_md = generate_workout_plan(
                    profile=profile,
                    preferences=preferences,
                    api_key=custom_key,
                    user_id=user_id
                )

            if success:
                st.session_state["active_workout_plan"] = plan_md
                st.success("✅ Your workout plan was generated and saved to your history!")
            else:
                st.error(f"Generation failed: {plan_md}")

        if "active_workout_plan" in st.session_state:
            st.write("---")
            st.markdown(st.session_state["active_workout_plan"])

            st.download_button(
                label="📥 Download Plan (.md)",
                data=st.session_state["active_workout_plan"],
                file_name=f"workout_plan_{date.today()}.md",
                mime="text/markdown",
                use_container_width=True
            )

    with tab2:
        saved_plans = db.get_workout_plans(user_id)
        if not saved_plans:
            st.info("Generate your first personalized workout plan.")
        else:
            for idx, item in enumerate(saved_plans):
                date_str = item.get("created_at", "")[:10]
                with st.expander(f"📋 Workout Routine #{item.get('id', idx+1)} — Saved {date_str}"):
                    st.markdown(item.get("plan") or item.get("plan_content", ""))
                    if st.button("🗑️ Delete Routine", key=f"del_workout_{item.get('id')}"):
                        db.delete_workout_plan(item.get("id"), user_id)
                        st.success("Plan removed from database.")
                        st.rerun()

