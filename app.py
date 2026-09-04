"""
app.py - Main Streamlit Application Entrypoint for AI FitCoach
Generative AI Based Personal Fitness Assistant.
"""

import streamlit as st
from database import db
from auth import login_user, register_user
from ai.openai_client import is_openai_configured
from components.navbar import render_navbar
from components.sidebar import render_sidebar
from pages.dashboard import render_dashboard_page
from pages.profile import render_profile_page
from pages.bmi_calculator import render_bmi_calculator_page
from pages.workout import render_workout_page
from pages.diet import render_diet_page
from pages.chatbot import render_chatbot_page
from pages.progress import render_progress_page
from pages.daily_tip import render_daily_tip_page

# -------------------------------------------------------------
# 1. Initialize Database & Page Configuration
# -------------------------------------------------------------
db.init_db()

st.set_page_config(
    page_title="AI FitCoach – Personal Fitness Assistant",
    page_icon="🏋️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Global Custom CSS for sleek Dark/Light fitness theme
st.markdown("""
<style>
    /* Main background */
    .stApp {
        background-color: #0b0f19;
        color: #f8fafc;
    }
    
    /* Input field styling */
    .stTextInput>div>div>input, .stNumberInput>div>div>input {
        background-color: #1e293b;
        color: #f8fafc;
        border: 1px solid #334155;
        border-radius: 8px;
    }

    /* Buttons */
    .stButton>button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.2s ease-in-out;
    }

    /* Expanders */
    .streamlit-expanderHeader {
        background-color: #1e293b;
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)


# -------------------------------------------------------------
# Session State Initialization (Section 5)
# -------------------------------------------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user" not in st.session_state:
    st.session_state.user = None
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "username" not in st.session_state:
    st.session_state.username = None
if "email" not in st.session_state:
    st.session_state.email = None
if "current_page" not in st.session_state:
    st.session_state.current_page = "Dashboard"
if "custom_api_key" not in st.session_state:
    st.session_state.custom_api_key = ""


# -------------------------------------------------------------
# Authentication Screen (Section 5)
# -------------------------------------------------------------
def render_auth_screen():
    st.markdown("<div style='text-align:center; padding: 25px 0;'>", unsafe_allow_html=True)
    st.markdown("<h1 style='color:#38bdf8; font-size:3rem; margin-bottom:0;'>🏋️ AI FitCoach</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:#94a3b8; font-size:1.2rem;'>Generative AI Based Personal Fitness Assistant</p>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        tab_login, tab_signup = st.tabs(["🔑 Sign In", "📝 Create New Account"])

        with tab_login:
            st.subheader("Welcome Back!")
            ident = st.text_input("Username or Email", key="auth_ident")
            pwd = st.text_input("Password", type="password", key="auth_pwd")

            if st.button("Log In", type="primary", use_container_width=True):
                if ident and pwd:
                    success, msg, user_data = login_user(ident, pwd)
                    if success and user_data:
                        st.session_state.logged_in = True
                        st.session_state.user = user_data
                        st.session_state.user_id = user_data["id"]
                        st.session_state.username = user_data["username"]
                        st.session_state.email = user_data["email"]
                        st.session_state.current_page = "Dashboard"
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)
                else:
                    st.warning("Please fill in both fields.")

        with tab_signup:
            st.subheader("Start Your Fitness Journey")
            full_name = st.text_input("Full Name", placeholder="e.g. Sarah Connor")
            new_username = st.text_input("Choose Username (min 3 chars)", placeholder="e.g. sarah_c")
            new_email = st.text_input("Email Address", placeholder="e.g. sarah@example.com")
            new_pwd = st.text_input("Password (min 6 chars)", type="password")
            confirm_pwd = st.text_input("Confirm Password", type="password")

            if st.button("Create My Account", type="primary", use_container_width=True):
                success, msg, user_id = register_user(
                    username=new_username,
                    email=new_email,
                    password=new_pwd,
                    confirm_password=confirm_pwd,
                    name=full_name
                )
                if success:
                    st.success(msg)
                else:
                    st.error(msg)


# -------------------------------------------------------------
# Main Application Router
# -------------------------------------------------------------
def main():
    try:
        # Check authentication status
        if not st.session_state.get("logged_in") or not st.session_state.get("user"):
            render_auth_screen()
            return

        user = st.session_state.user
        profile = db.get_profile(user["id"]) or {}

        ai_active = is_openai_configured(st.session_state.get("custom_api_key"))

        # Top navigation header
        render_navbar(user, ai_active=ai_active)

        # Sidebar navigation & API settings
        selected_page = render_sidebar(user, profile)

        # Page Dispatcher
        if selected_page == "Dashboard":
            render_dashboard_page(user, profile)
        elif selected_page in ["My Profile", "Profile & Goals"]:
            render_profile_page(user, profile)
        elif selected_page == "BMI Calculator":
            render_bmi_calculator_page(user, profile)
        elif selected_page == "Workout Generator":
            render_workout_page(user, profile)
        elif selected_page in ["Diet Generator", "Diet & Nutrition"]:
            render_diet_page(user, profile)
        elif selected_page in ["Fitness Chatbot", "AI Fitness Chatbot"]:
            render_chatbot_page(user, profile)
        elif selected_page in ["Progress Tracking", "Progress Tracker"]:
            render_progress_page(user, profile)
        elif selected_page in ["Daily Fitness Tip", "Daily Tips & Quotes"]:
            render_daily_tip_page()
        else:
            render_dashboard_page(user, profile)

    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
        st.info("Please refresh the page or contact system support.")


if __name__ == "__main__":
    main()

