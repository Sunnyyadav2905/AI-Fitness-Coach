"""
ai/recommendations.py - Progress Analysis & Adaptive Recommendations for AI-FitCoach
Evaluates historical progress metrics (weight, water, sleep, steps, calories, workouts)
and provides data-backed, encouraging weekly modifications using Google Gemini API.
"""

from typing import List, Dict, Any, Optional, Tuple
from ai.gemini_client import generate_completion, RECOMMENDATION_SYSTEM_PROMPT
from utils.constants import MEDICAL_DISCLAIMER


def generate_progress_recommendations(
    profile: Dict[str, Any],
    logs: List[Dict[str, Any]],
    api_key: Optional[str] = None
) -> Tuple[bool, str]:
    """
    Analyzes recent progress logs and user goals to generate tailored coaching recommendations.
    Uses: Current weight, Previous weight, Target weight, Workout consistency, Sleep, Water, Steps, Calories, Goal.
    Returns (success: bool, recommendation_markdown: str).
    """
    if not logs:
        return False, "Start tracking your progress to see charts and AI recommendations."

    name = profile.get("name") or profile.get("full_name", "Athlete")
    fitness_goal = profile.get("fitness_goal", "General Fitness")
    target_weight = profile.get("target_weight") or profile.get("target_weight_kg", 65.0)

    # Extract weight history
    weight_entries = [
        float(l["weight"]) for l in logs
        if l.get("weight") is not None or l.get("weight_kg") is not None
    ]
    current_weight = weight_entries[-1] if weight_entries else (profile.get("weight") or 70.0)
    prev_weight = weight_entries[-2] if len(weight_entries) >= 2 else current_weight

    # Extract consistency metrics
    total_days = len(logs)
    workouts_completed = sum(1 for l in logs if int(l.get("workout_completed", 0)) == 1)
    consistency_rate = round((workouts_completed / total_days) * 100, 1) if total_days > 0 else 0.0

    # Extract averages
    waters = [float(l["water"]) for l in logs if l.get("water") is not None]
    avg_water = round(sum(waters) / len(waters), 2) if waters else 0.0

    sleeps = [float(l["sleep"]) for l in logs if l.get("sleep") is not None]
    avg_sleep = round(sum(sleeps) / len(sleeps), 1) if sleeps else 0.0

    calories = [int(l["calories"]) for l in logs if l.get("calories") is not None and int(l["calories"]) > 0]
    avg_calories = round(sum(calories) / len(calories)) if calories else 0

    steps = [int(l["steps"]) for l in logs if l.get("steps") is not None and int(l["steps"]) > 0]
    avg_steps = round(sum(steps) / len(steps)) if steps else 0

    # Format recent entries for AI prompt
    recent_entries_str = []
    for l in logs[-10:]:
        date_str = l.get("date") or l.get("log_date", "Recent")
        w = l.get("weight") or l.get("weight_kg", "N/A")
        h2o = l.get("water") or l.get("water_liters", "N/A")
        slp = l.get("sleep") or l.get("sleep_hours", "N/A")
        cals = l.get("calories") or l.get("calories_consumed", "N/A")
        stps = l.get("steps", "N/A")
        wo = "Yes" if int(l.get("workout_completed", 0)) == 1 else "No"
        recent_entries_str.append(
            f"- Date: {date_str} | Wt: {w}kg | Water: {h2o}L | Sleep: {slp}h | Cals: {cals} | Steps: {stps} | Workout: {wo}"
        )

    user_prompt = f"""
Analyze the recent progress data for {name} and provide actionable, encouraging recommendations:

**Profile & Targets:**
- Fitness Goal: {fitness_goal}
- Current Weight: {current_weight} kg
- Previous Weight: {prev_weight} kg
- Target Weight: {target_weight} kg

**Key Progress Statistics:**
- Total Days Logged: {total_days}
- Workout Consistency: {consistency_rate}% ({workouts_completed}/{total_days} days completed)
- Average Water Intake: {avg_water} Liters / day
- Average Sleep Duration: {avg_sleep} Hours / night
- Average Daily Calories: {avg_calories} kcal
- Average Daily Steps: {avg_steps} steps

**Recent Daily Logs:**
{chr(10).join(recent_entries_str)}

**Please Provide:**
1. **Workout Consistency Suggestions**: Specific guidance based on the {consistency_rate}% completion rate.
2. **Hydration Improvements**: Practical ways to hit optimal daily water targets.
3. **Sleep Improvements**: Specific sleep hygiene tips based on their {avg_sleep}h sleep average.
4. **Realistic Fitness & Caloric Suggestions**: Sustainable tweaks towards the {fitness_goal} goal without extreme restrictions.
5. **Positive Encouragement**: Warm, motivating feedback reinforcing adherence and habit consistency.
"""

    success, content = generate_completion(
        prompt=user_prompt,
        system_message=RECOMMENDATION_SYSTEM_PROMPT,
        api_key=api_key,
        temperature=0.7,
        max_tokens=1500
    )

    if not success:
        offline_rec = generate_fallback_recommendations(
            name=name,
            goal=fitness_goal,
            current_weight=current_weight,
            target_weight=target_weight,
            consistency_rate=consistency_rate,
            avg_water=avg_water,
            avg_sleep=avg_sleep,
            avg_calories=avg_calories,
            avg_steps=avg_steps
        )
        final_rec = (
            f"> 💡 **Offline Progress Intelligence**: Generated via statistical trend analysis. "
            f"Add a Gemini API key in the sidebar for live Gemini generation.\n\n"
            f"{offline_rec}\n\n---\n\n{MEDICAL_DISCLAIMER}"
        )
    else:
        final_rec = f"{content.strip()}\n\n---\n\n{MEDICAL_DISCLAIMER}"

    return True, final_rec


def generate_fallback_recommendations(
    name: str,
    goal: str,
    current_weight: float,
    target_weight: float,
    consistency_rate: float,
    avg_water: float,
    avg_sleep: float,
    avg_calories: int,
    avg_steps: int
) -> str:
    """Calculates data-backed progress observations and recommendations without external API."""
    weight_diff = round(current_weight - target_weight, 1)

    if consistency_rate >= 80:
        consistency_eval = "🌟 **Outstanding Adherence!** You are training consistently on 80%+ of logged days. Your discipline is in the top tier."
    elif consistency_rate >= 50:
        consistency_eval = "👍 **Solid Foundation!** You're hitting over half of your scheduled workouts. Focus on locking in fixed workout times to reach 75%+."
    else:
        consistency_eval = "⚡ **Opportunity to Build Momentum:** Adherence is currently below 50%. Try reducing session length to 30 mins to build consistency before volume."

    water_eval = "💧 **Hydration is on point!**" if avg_water >= 2.8 else f"💧 **Increase Water Intake:** Averaging {avg_water}L. Try drinking a full glass immediately upon waking and between meals to hit 3.0L."

    sleep_eval = "😴 **Rest & Recovery Optimal:** Averaging 7.5+ hours of sleep per night." if avg_sleep >= 7.5 else f"😴 **Prioritize Sleep:** Averaging {avg_sleep} hours. Muscle protein synthesis and hormonal recovery peak in deep sleep (7–8 hours)."

    return f"""### 📊 Data-Driven Progress Analysis for {name}

**Goal Focus:** {goal} | **Current Weight:** {current_weight} kg | **Target Weight:** {target_weight} kg ({abs(weight_diff)} kg remaining)

---

#### 1. 🏋️ Workout Consistency & Execution
{consistency_eval}

#### 2. 💧 Hydration Performance
{water_eval} Proper hydration enhances cellular pump, kidney filtration, and cognitive energy.

#### 3. 🌙 Sleep & Central Nervous System Recovery
{sleep_eval}

#### 4. 👟 Daily Activity (NEAT)
* **Average Steps:** {avg_steps} steps/day. 
* *Coaching Tip:* Steady daily walking burns free fatty acids while keeping cortisol low, perfectly complementing resistance training.

#### 5. 🎯 Next Week's Actionable Focus
1. **Maintain Training Intensity:** Keep applying progressive overload (track sets, reps, and weights in your log notes).
2. **Pre-pack Hydration:** Keep a 1L water bottle on your desk or gym bag.
3. **Consistency over Perfection:** Aim for 3–4 quality sessions this week!
"""


def analyze_progress_and_recommend(
    profile: Dict[str, Any],
    logs: List[Dict[str, Any]],
    api_key: Optional[str] = None
) -> str:
    """Backwards-compatible wrapper returning markdown string directly."""
    success, result = generate_progress_recommendations(profile, logs, api_key=api_key)
    return result

