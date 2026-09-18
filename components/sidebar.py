"""
components/sidebar.py - Sidebar Navigation & Settings Component for AI-FitCoach
"""

import streamlit as st
from typing import Dict, Any
from ai.gemini_client import validate_api_key, is_gemini_configured
from utils.constants import APP_NAME, APP_VERSION


def render_sidebar(user: Dict[str, Any], profile: Dict[str, Any]) -> str:
    """
    Renders the sidebar navigation and configuration panel.
    Returns the selected page string.
    """
    with st.sidebar:
        st.markdown(f"## 🏋️ **{APP_NAME}**")
        st.caption(f"v{APP_VERSION} • Personal Fitness Assistant")

        # User quick profile summary card
        display_name = profile.get("name") or profile.get("full_name") or user.get("username", "User")
        goal = profile.get("fitness_goal", "Weight Loss")
        weight = profile.get("weight") or profile.get("weight_kg", 70.0)
        height = profile.get("height") or profile.get("height_cm", 170.0)

        st.markdown(
            f"""
            <div style="background-color: #1e293b; padding: 12px 14px; border-radius: 8px; border: 1px solid #334155; margin-bottom: 15px;">
                <div style="font-weight: 600; color: #f8fafc; font-size: 0.95rem;">👤 {display_name}</div>
                <div style="font-size: 0.8rem; color: #38bdf8;">Goal: {goal}</div>
                <div style="font-size: 0.75rem; color: #94a3b8;">Weight: {weight} kg • Height: {height} cm</div>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Exact Navigation Items per Prompt Section 15
        pages = [
            "Dashboard",
            "My Profile",
            "BMI Calculator",
            "Workout Generator",
            "Diet Generator",
            "Fitness Chatbot",
            "Progress Tracking",
            "Daily Fitness Tip"
        ]

        page_labels = {
            "Dashboard": "🏠 Dashboard",
            "My Profile": "👤 My Profile",
            "BMI Calculator": "⚖️ BMI Calculator",
            "Workout Generator": "🏋️ Workout Generator",
            "Diet Generator": "🥗 Diet Generator",
            "Fitness Chatbot": "💬 Fitness Chatbot",
            "Progress Tracking": "📈 Progress Tracking",
            "Daily Fitness Tip": "💡 Daily Fitness Tip"
        }

        current = st.session_state.get("current_page", "Dashboard")
        curr_idx = pages.index(current) if current in pages else 0

        selected = st.radio(
            "Navigation",
            pages,
            index=curr_idx,
            format_func=lambda x: page_labels.get(x, x),
            label_visibility="collapsed"
        )
        st.session_state.current_page = selected

        st.markdown("<hr style='border-color: #334155; margin: 15px 0;'>", unsafe_allow_html=True)

        # AI API Configuration Expander
        with st.expander("⚙️ Gemini API Settings", expanded=False):
            api_key_input = st.text_input(
                "Google Gemini API Key",
                value=st.session_state.get("custom_api_key", ""),
                type="password",
                placeholder="AIzaSy...",
                help="Enter your personal Google Gemini API key. Stored only in your local session."
            )

            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                if st.button("Test & Save", use_container_width=True):
                    if api_key_input:
                        valid, msg = validate_api_key(api_key_input)
                        if valid:
                            st.session_state.custom_api_key = api_key_input
                            st.success("Key validated & saved!")
                            st.rerun()
                        else:
                            st.error(msg)
                    else:
                        st.warning("Please enter an API key.")
            with col_btn2:
                if st.button("Clear Key", use_container_width=True):
                    st.session_state.custom_api_key = ""
                    st.info("Cleared custom key.")
                    st.rerun()

            if is_gemini_configured(st.session_state.get("custom_api_key")):
                st.caption("Status: 🟢 **Gemini Live Connected**")
            else:
                st.caption("Status: 🟡 **Using Environment / Offline Engine**")

        st.markdown("<hr style='border-color: #334155; margin: 15px 0;'>", unsafe_allow_html=True)

        # Logout button
        if st.button("🚪 Logout", key="sidebar_logout_btn", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.user = None
            st.session_state.user_id = None
            st.session_state.username = None
            st.session_state.email = None
            st.session_state.current_page = "Dashboard"
            st.rerun()

    return selected

