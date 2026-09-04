"""
components/charts.py - Plotly Interactive Analytics & Visualizations for AI-FitCoach
"""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from typing import Optional


def _normalize_progress_df(df: pd.DataFrame) -> pd.DataFrame:
    """Ensures consistent column names across schemas."""
    d = df.copy()
    col_map = {
        "log_date": "date",
        "weight_kg": "weight",
        "calories_consumed": "calories",
        "water_liters": "water",
        "sleep_hours": "sleep"
    }
    for old_col, new_col in col_map.items():
        if old_col in d.columns and new_col not in d.columns:
            d[new_col] = d[old_col]
        elif new_col in d.columns and old_col not in d.columns:
            d[old_col] = d[new_col]
    return d


def create_weight_trend_chart(df: pd.DataFrame, target_weight: float = 65.0) -> go.Figure:
    """Creates an interactive Plotly line chart tracking bodyweight over time against target."""
    df_clean = _normalize_progress_df(df)
    date_col = "date" if "date" in df_clean.columns else "log_date"
    weight_col = "weight" if "weight" in df_clean.columns else "weight_kg"

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df_clean[date_col],
        y=df_clean[weight_col],
        mode="lines+markers",
        name="Logged Weight (kg)",
        line=dict(color="#38bdf8", width=3),
        marker=dict(size=8, color="#0284c7")
    ))

    # Target line
    fig.add_trace(go.Scatter(
        x=df_clean[date_col],
        y=[target_weight] * len(df_clean),
        mode="lines",
        name=f"Target ({target_weight} kg)",
        line=dict(color="#ef4444", width=2, dash="dash")
    ))

    fig.update_layout(
        title="Bodyweight Trend vs. Target",
        xaxis_title="Date",
        yaxis_title="Weight (kg)",
        template="plotly_dark",
        margin=dict(l=40, r=40, t=50, b=40),
        height=360,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    return fig


def create_water_chart(df: pd.DataFrame, target_water: float = 2.5) -> go.Figure:
    """Creates a bar chart tracking daily water intake in Liters."""
    df_clean = _normalize_progress_df(df)
    date_col = "date" if "date" in df_clean.columns else "log_date"
    water_col = "water" if "water" in df_clean.columns else "water_liters"

    fig = px.bar(
        df_clean,
        x=date_col,
        y=water_col,
        title="Daily Water Intake (Liters)",
        labels={date_col: "Date", water_col: "Water (L)"},
        color_discrete_sequence=["#0ea5e9"],
        template="plotly_dark"
    )

    fig.add_hline(
        y=target_water,
        line_dash="dash",
        line_color="#38bdf8",
        annotation_text=f"Goal: {target_water}L",
        annotation_position="top left"
    )

    fig.update_layout(height=320, margin=dict(l=40, r=40, t=50, b=40))
    return fig


def create_sleep_chart(df: pd.DataFrame) -> go.Figure:
    """Creates a bar chart tracking sleep duration."""
    df_clean = _normalize_progress_df(df)
    date_col = "date" if "date" in df_clean.columns else "log_date"
    sleep_col = "sleep" if "sleep" in df_clean.columns else "sleep_hours"

    if sleep_col not in df_clean.columns:
        df_clean[sleep_col] = 7.5

    fig = px.bar(
        df_clean,
        x=date_col,
        y=sleep_col,
        title="Sleep Duration (Hours/Night)",
        labels={date_col: "Date", sleep_col: "Sleep (Hours)"},
        color_discrete_sequence=["#8b5cf6"],
        template="plotly_dark"
    )

    fig.add_hline(
        y=7.0,
        line_dash="dot",
        line_color="#a78bfa",
        annotation_text="Optimal Min: 7h",
        annotation_position="top right"
    )

    fig.update_layout(height=320, margin=dict(l=40, r=40, t=50, b=40))
    return fig


def create_steps_chart(df: pd.DataFrame, target_steps: int = 10000) -> go.Figure:
    """Creates a bar chart tracking daily steps."""
    df_clean = _normalize_progress_df(df)
    date_col = "date" if "date" in df_clean.columns else "log_date"
    if "steps" not in df_clean.columns:
        df_clean["steps"] = 0

    fig = px.bar(
        df_clean,
        x=date_col,
        y="steps",
        title="Daily Steps Count",
        labels={date_col: "Date", "steps": "Steps"},
        color_discrete_sequence=["#06b6d4"],
        template="plotly_dark"
    )

    fig.add_hline(
        y=target_steps,
        line_dash="dash",
        line_color="#22d3ee",
        annotation_text=f"Target: {target_steps} steps",
        annotation_position="top left"
    )

    fig.update_layout(height=320, margin=dict(l=40, r=40, t=50, b=40))
    return fig


def create_calorie_chart(df: pd.DataFrame, target_calories: Optional[int] = None) -> go.Figure:
    """Creates a bar chart tracking daily calorie consumption."""
    df_clean = _normalize_progress_df(df)
    date_col = "date" if "date" in df_clean.columns else "log_date"
    cal_col = "calories" if "calories" in df_clean.columns else "calories_consumed"

    fig = px.bar(
        df_clean,
        x=date_col,
        y=cal_col,
        title="Daily Caloric Intake (kcal)",
        labels={date_col: "Date", cal_col: "Calories (kcal)"},
        color_discrete_sequence=["#10b981"],
        template="plotly_dark"
    )

    if target_calories:
        fig.add_hline(
            y=target_calories,
            line_dash="dash",
            line_color="#f59e0b",
            annotation_text=f"Target: {target_calories} kcal",
            annotation_position="top left"
        )

    fig.update_layout(height=320, margin=dict(l=40, r=40, t=50, b=40))
    return fig


def create_workout_completion_chart(df: pd.DataFrame) -> go.Figure:
    """Creates a discrete timeline/bar chart showing workout completion status."""
    df_clean = _normalize_progress_df(df)
    date_col = "date" if "date" in df_clean.columns else "log_date"

    completion_status = df_clean["workout_completed"].apply(
        lambda x: "Completed" if int(x) == 1 else "Rest / Missed"
    )

    color_map = {"Completed": "#22c55e", "Rest / Missed": "#64748b"}

    fig = px.bar(
        df_clean,
        x=date_col,
        y=[1] * len(df_clean),
        color=completion_status,
        color_discrete_map=color_map,
        title="Workout Completion History",
        labels={date_col: "Date", "y": "Session", "color": "Status"},
        template="plotly_dark"
    )
    fig.update_layout(height=260, yaxis_showticklabels=False, margin=dict(l=40, r=40, t=50, b=40))
    return fig


def create_adherence_gauge(adherence_pct: float) -> go.Figure:
    """Creates a circular gauge chart for workout adherence."""
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=adherence_pct,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Workout Adherence Rate (%)", 'font': {'size': 18, 'color': '#f8fafc'}},
        gauge={
            'axis': {'range': [0, 100], 'tickcolor': '#94a3b8'},
            'bar': {'color': '#10b981'},
            'steps': [
                {'range': [0, 50], 'color': '#ef4444'},
                {'range': [50, 75], 'color': '#f59e0b'},
                {'range': [75, 100], 'color': '#064e3b'}
            ],
            'threshold': {
                'line': {'color': '#38bdf8', 'width': 4},
                'thickness': 0.75,
                'value': 80
            }
        }
    ))
    fig.update_layout(template="plotly_dark", height=240, margin=dict(l=30, r=30, t=40, b=20))
    return fig

