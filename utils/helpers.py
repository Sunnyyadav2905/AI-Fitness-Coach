"""
utils/helpers.py - General Helper Utilities for AI-FitCoach
"""

from datetime import datetime, date
from typing import Union, Any, List, Dict
import pandas as pd


def is_authenticated(session_state: Any) -> bool:
    """Checks if a user session is active and valid."""
    if not session_state:
        return False
    return bool(session_state.get("logged_in") or session_state.get("user"))


def format_date(d: Union[str, date, datetime], out_fmt: str = "%b %d, %Y") -> str:
    """Formats dates consistently for UI display."""
    if not d:
        return "N/A"
    if isinstance(d, str):
        try:
            d = datetime.strptime(d[:10], "%Y-%m-%d").date()
        except ValueError:
            return d
    if isinstance(d, (date, datetime)):
        return d.strftime(out_fmt)
    return str(d)


def format_float(val: Any, decimals: int = 2) -> str:
    """Safely formats a floating point number."""
    try:
        if val is None:
            return "N/A"
        f = float(val)
        return f"{f:.{decimals}f}"
    except (ValueError, TypeError):
        return "N/A"


def calculate_adherence_rate(completed_sessions: int, total_logged_days: int) -> float:
    """Calculates workout adherence percentage."""
    if total_logged_days <= 0:
        return 0.0
    return round((completed_sessions / total_logged_days) * 100.0, 1)


def clean_markdown(text: str) -> str:
    """Strips unwanted surrounding markdown code fences if model output is wrapped."""
    if not text:
        return ""
    clean = text.strip()
    if clean.startswith("```markdown"):
        clean = clean[11:]
    elif clean.startswith("```"):
        clean = clean[3:]
    if clean.endswith("```"):
        clean = clean[:-3]
    return clean.strip()


def safe_api_output(raw_output: Any) -> str:
    """Safely handles OpenAI API response outputs and returns clean markdown or fallback message."""
    if not raw_output:
        return "No response generated. Please check your prompt and try again."
    cleaned = clean_markdown(str(raw_output))
    return cleaned


def format_database_rows(rows: List[Any]) -> List[Dict[str, Any]]:
    """Converts a list of sqlite3.Row objects into a list of standard python dictionaries."""
    if not rows:
        return []
    result = []
    for r in rows:
        if isinstance(r, dict):
            result.append(r)
        else:
            try:
                result.append(dict(r))
            except Exception:
                result.append(r)
    return result


def export_dataframe_to_csv(df: pd.DataFrame) -> bytes:
    """Encodes a pandas DataFrame as CSV UTF-8 bytes for download."""
    return df.to_csv(index=False).encode("utf-8")

