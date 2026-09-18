"""
pages/diet.py - AI Diet & Nutrition Generator Page for AI-FitCoach
"""

import streamlit as st
from datetime import date
from typing import Dict, Any
from database import db
from ai.gemini_client import is_gemini_configured
from ai.diet_generator import generate_diet_plan
from utils.constants import DIETARY_PREFERENCES


def render_diet_page(user: Dict[str, Any], profile: Dict[str, Any]) -> None:
    """Renders the diet plan generation and saved diet library view."""
    user_id = user["id"]
    custom_key = st.session_state.get("custom_api_key", None)
    ai_online = is_gemini_configured(custom_key)

    st.title("🥗 Diet Generator")
    st.caption("Formulate personalized, macronutrient-balanced meal plans tailored to your lifestyle and dietary needs.")

    tab1, tab2 = st.tabs(["✨ Generate Meal Plan", "📁 Saved Diet Plans"])

    with tab1:
        if not profile or not profile.get("name") and not profile.get("full_name"):
            st.info("💡 Complete your profile in **My Profile** to unlock personalized nutrition guidance.")

        st.subheader("Dietary Preferences & Settings")
        col1, col2 = st.columns(2)

        with col1:
            dietary_preference = st.selectbox("Dietary Preference", DIETARY_PREFERENCES, index=0)
            num_meals = st.selectbox("Number of Meals per Day", [3, 4, 5, 6], index=1)

        with col2:
            allergies = st.text_input(
                "Allergies or Foods to Avoid",
                placeholder="e.g. Peanuts, lactose, gluten, shellfish, none",
                value="None"
            )

        if ai_online:
            st.caption("🟢 **AI Engine Active:** Google Gemini (gemini-1.5-flash)")
        else:
            st.caption("🟡 **Engine Mode:** Offline Metabolic Engine (Enter Gemini API key in sidebar to enable live Gemini)")

        if st.button("🚀 Generate Personalized Diet Suggestions", type="primary", use_container_width=True):
            preferences = {
                "dietary_preference": dietary_preference,
                "allergies": allergies,
                "num_meals": num_meals
            }
            custom_key = st.session_state.get("custom_api_key", None)

            with st.spinner("FitCoach AI is calculating your meal blueprint and nutrition guidance..."):
                success, plan_md = generate_diet_plan(
                    profile=profile,
                    preferences=preferences,
                    api_key=custom_key,
                    user_id=user_id
                )

            if success:
                st.session_state["active_diet_plan"] = plan_md
                st.success("✅ Your meal plan was generated and saved to your history!")
            else:
                st.error(f"Generation failed: {plan_md}")

        if "active_diet_plan" in st.session_state:
            st.write("---")
            st.markdown(st.session_state["active_diet_plan"])

            st.download_button(
                label="📥 Download Diet Plan (.md)",
                data=st.session_state["active_diet_plan"],
                file_name=f"diet_plan_{date.today()}.md",
                mime="text/markdown",
                use_container_width=True
            )

    with tab2:
        saved_diets = db.get_diet_plans(user_id)
        if not saved_diets:
            st.info("Generate your personalized meal suggestions.")
        else:
            for idx, item in enumerate(saved_diets):
                date_str = item.get("created_at", "")[:10]
                with st.expander(f"🍲 Meal Blueprint #{item.get('id', idx+1)} — Saved {date_str}"):
                    st.markdown(item.get("plan") or item.get("plan_content", ""))
                    if st.button("🗑️ Delete Meal Plan", key=f"del_diet_{item.get('id')}"):
                        db.delete_diet_plan(item.get("id"), user_id)
                        st.success("Meal plan deleted from database.")
                        st.rerun()

