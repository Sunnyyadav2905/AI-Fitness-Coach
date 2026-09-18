"""
components/navbar.py - Top Navigation Header Component for Streamlit
"""

import streamlit as st
from typing import Dict, Any


def render_navbar(user: Dict[str, Any], ai_active: bool = False) -> None:
    """Renders the top application header bar with branding and user status."""
    col1, col2, col3 = st.columns([3, 2, 1])

    with col1:
        st.markdown(
            "<h3 style='margin:0; color:#38bdf8;'>🏋️ AI FitCoach</h3>"
            "<span style='font-size:0.8rem; color:#94a3b8;'>Generative AI Based Personal Fitness Assistant</span>",
            unsafe_allow_html=True
        )

    with col2:
        badge_text = "🟢 Gemini Connected" if ai_active else "🟡 Smart Offline Mode"
        badge_color = "#059669" if ai_active else "#d97706"
        st.markdown(
            f"<div style='text-align:right; margin-top:6px;'>"
            f"<span style='background-color:{badge_color}; color:#fff; padding:3px 10px; border-radius:12px; font-size:0.75rem; font-weight:600;'>{badge_text}</span>"
            f"<br><span style='font-size:0.8rem; color:#cbd5e1;'>User: <strong>{user.get('username', '')}</strong></span>"
            f"</div>",
            unsafe_allow_html=True
        )

    with col3:
        if st.button("🚪 Logout", key="nav_logout_btn", use_container_width=True):
            st.session_state.user = None
            st.session_state.current_page = "Dashboard"
            st.rerun()

    st.markdown("<hr style='margin: 10px 0 20px 0; border-color: #334155;'>", unsafe_allow_html=True)
