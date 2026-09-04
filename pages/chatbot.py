"""
pages/chatbot.py - Conversational Fitness Assistant Interface for AI-FitCoach
"""

import streamlit as st
from typing import Dict, Any
from database import db
from ai.chatbot import chat_with_coach
from utils.constants import MEDICAL_DISCLAIMER


def render_chatbot_page(user: Dict[str, Any], profile: Dict[str, Any]) -> None:
    """Renders the conversational AI coach chat interface."""
    user_id = user["id"]
    st.title("💬 Fitness Chatbot")
    st.caption("Ask anything regarding workouts, nutrition, recovery, hydration, sleep, or fitness motivation.")

    # Medical Disclaimer banner
    st.caption("⚠️ FitCoach is an educational fitness assistant, not a physician. For emergencies or injuries, seek medical care.")

    # Quick Topic Shortcut Pills
    st.markdown("**Suggested Questions:**")
    q_col1, q_col2, q_col3, q_col4 = st.columns(4)
    selected_quick_prompt = None

    if q_col1.button("🥑 Best pre-workout snacks?", use_container_width=True):
        selected_quick_prompt = "What are the best healthy pre-workout snacks for sustained training energy?"
    if q_col2.button("⚖️ How to break plateaus?", use_container_width=True):
        selected_quick_prompt = "How can I break through a stubborn weight loss plateau?"
    if q_col3.button("💧 Daily hydration rules?", use_container_width=True):
        selected_quick_prompt = "How much water should I drink daily around intense training sessions?"
    if q_col4.button("🩹 Relieving sore muscles?", use_container_width=True):
        selected_quick_prompt = "What is the most effective way to recover from severe muscle soreness (DOMS)?"

    # Controls row
    top_col1, top_col2 = st.columns([5, 1])
    with top_col2:
        if st.button("🧹 Clear Chat", use_container_width=True):
            db.clear_chat_history(user_id)
            st.rerun()

    # Load and render chat history
    history = db.get_chat_history(user_id, limit=60)

    if not history:
        st.info("👋 Hello! I am your AI FitCoach. Ask me any question about your workout routine, diet plans, or recovery habits to get started!")
    else:
        for msg in history:
            role = msg.get("role", "user")
            avatar = "🧑‍💻" if role in ["user", "client"] else "🏋️"
            with st.chat_message(role, avatar=avatar):
                st.markdown(msg.get("message", ""))

    # Chat input handling
    user_input = st.chat_input("Ask your fitness question here...")
    if selected_quick_prompt:
        user_input = selected_quick_prompt

    if user_input:
        custom_key = st.session_state.get("custom_api_key", None)
        with st.chat_message("user", avatar="🧑‍💻"):
            st.markdown(user_input)

        with st.chat_message("assistant", avatar="🏋️"):
            with st.spinner("FitCoach AI is formulating your response..."):
                ok, reply = chat_with_coach(
                    user_id=user_id,
                    user_message=user_input,
                    profile=profile,
                    api_key=custom_key
                )
                st.markdown(reply)
        st.rerun()

