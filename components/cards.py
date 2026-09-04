"""
components/cards.py - Reusable Styled UI Card Components for Streamlit
"""

import streamlit as st
from typing import Optional


def render_metric_card(
    title: str,
    value: str,
    subtitle: str = "",
    color: Optional[str] = None
) -> None:
    """Renders a modern metric card with customizable accent color."""
    val_style = f"color: {color};" if color else "color: #f8fafc;"
    html = f"""
    <div style="
        background: linear-gradient(135deg, #1e293b, #0f172a);
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 18px 20px;
        margin-bottom: 12px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.15);
    ">
        <div style="font-size: 0.8rem; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.05em; font-weight: 600;">
            {title}
        </div>
        <div style="font-size: 1.8rem; font-weight: 700; margin: 4px 0; {val_style}">
            {value}
        </div>
        <div style="font-size: 0.85rem; color: #38bdf8;">
            {subtitle}
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def render_tip_card(category: str, tip_text: str) -> None:
    """Renders an engaging daily tip box."""
    html = f"""
    <div style="
        background: linear-gradient(135deg, #064e3b, #022c22);
        border-left: 5px solid #10b981;
        padding: 16px 20px;
        border-radius: 8px;
        margin-bottom: 16px;
        color: #ecfdf5;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    ">
        <div style="font-size: 0.85rem; font-weight: 700; color: #6ee7b7; text-transform: uppercase;">
            💡 Daily Fitness Tip ({category})
        </div>
        <div style="font-size: 0.95rem; margin-top: 6px; line-height: 1.4;">
            {tip_text}
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def render_quote_card(quote_text: str) -> None:
    """Renders a stylish motivational quote card."""
    html = f"""
    <div style="
        background: linear-gradient(135deg, #1e1b4b, #0f172a);
        border-left: 5px solid #818cf8;
        padding: 16px 20px;
        border-radius: 8px;
        margin-bottom: 16px;
        color: #e0e7ff;
        font-style: italic;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    ">
        <div style="font-size: 0.85rem; font-weight: 700; color: #a5b4fc; text-transform: uppercase; font-style: normal;">
            💬 Daily Inspiration
        </div>
        <div style="font-size: 0.95rem; margin-top: 6px; line-height: 1.4;">
            "{quote_text}"
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def render_info_badge(label: str, bg_color: str = "#3b82f6") -> str:
    """Returns an inline HTML pill badge."""
    return f"""<span style="
        background-color: {bg_color};
        color: #ffffff;
        padding: 4px 10px;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
        display: inline-block;
    ">{label}</span>"""
