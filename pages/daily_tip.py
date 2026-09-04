"""
pages/daily_tip.py - Daily Fitness Tip Generator & Motivation Hub for AI-FitCoach
"""

import streamlit as st
import random
from datetime import date
from utils.constants import DAILY_TIPS_COLLECTION
from components.cards import render_tip_card, render_quote_card
from ai.openai_client import generate_completion, get_effective_api_key

TIP_TOPICS = [
    "Exercise",
    "Hydration",
    "Sleep",
    "Nutrition",
    "Recovery",
    "Motivation",
    "Consistency"
]


@st.cache_data(ttl=43200, show_spinner=False)
def fetch_cached_ai_tip(topic: str, today_str: str, api_key_masked: str) -> str:
    """
    Fetches an AI-generated daily fitness tip with 12-hour caching.
    Prevents repeated API calls on every Streamlit page rerun.
    """
    system_prompt = (
        "You are AI FitCoach. Provide a concise, highly practical, 2-to-3 sentence fitness tip "
        "and a brief motivational quote. Safe, positive, evidence-based."
    )
    prompt = f"Provide an actionable daily fitness tip on the topic of '{topic}' for {today_str}. Include a short quote."
    success, reply = generate_completion(
        prompt=prompt,
        system_message=system_prompt,
        temperature=0.7,
        max_tokens=250
    )
    if success and reply:
        return reply
    return ""


def render_daily_tip_page() -> None:
    """Renders the fitness tips repository and daily inspirational advice."""
    st.title("💡 Daily Fitness Tip")
    st.caption("Evidence-based habits, recovery protocols, and mindset principles to fuel your fitness journey.")

    today_str = str(date.today())

    # Topic selector for tailored daily tips
    col_t1, col_t2 = st.columns([3, 1])
    with col_t1:
        selected_topic = st.selectbox("Select Tip Focus Area", TIP_TOPICS, index=0)
    with col_t2:
        refresh_btn = st.button("🔄 New Tip", use_container_width=True)

    if refresh_btn:
        st.cache_data.clear()

    # Generate or fetch cached AI tip
    custom_key = st.session_state.get("custom_api_key", "")
    key_mask = custom_key[:6] if custom_key else "default"

    ai_tip = ""
    if get_effective_api_key(custom_key):
        with st.spinner("Retrieving today's personalized tip..."):
            ai_tip = fetch_cached_ai_tip(selected_topic, today_str, key_mask)

    st.write("---")
    st.subheader(f"🌟 Today's Featured Tip: {selected_topic}")

    if ai_tip:
        st.markdown(
            f"""
            <div style="background-color: #064e3b; border-left: 5px solid #10b981; padding: 18px 22px; border-radius: 8px; margin-bottom: 20px;">
                <div style="font-weight: 700; color: #6ee7b7; font-size: 0.95rem; text-transform: uppercase;">
                    ⚡ AI Coach Insight • {selected_topic}
                </div>
                <div style="font-size: 1.05rem; color: #ecfdf5; margin-top: 8px; line-height: 1.5;">
                    {ai_tip}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        # Fallback to curated tip
        matching_tips = [t for t in DAILY_TIPS_COLLECTION if t["category"].lower() == selected_topic.lower()]
        featured = matching_tips[0] if matching_tips else DAILY_TIPS_COLLECTION[0]
        c1, c2 = st.columns(2)
        with c1:
            render_tip_card(featured["category"], featured["tip"])
        with c2:
            render_quote_card(featured["quote"])

    st.write("---")

    # Knowledge Catalog covering all 7 areas
    st.subheader("📚 7 Pillars of Fitness Success")
    t_cols = st.columns(len(TIP_TOPICS))
    for idx, topic in enumerate(TIP_TOPICS):
        with t_cols[idx]:
            st.markdown(f"**{topic}**")

    st.markdown("#### Curated Tip Library")
    for item in DAILY_TIPS_COLLECTION:
        with st.expander(f"📌 {item['category']} — \"{item['tip'][:65]}...\""):
            st.markdown(f"**Actionable Advice:**\n{item['tip']}")
            st.markdown(f"**Inspiration:**\n*\"{item['quote']}\"*")

