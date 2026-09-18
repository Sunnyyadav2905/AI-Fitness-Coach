"""
ai/workout_generator.py - AI Workout Plan Generator for AI-FitCoach
Produces personalized, safe, and progressive weekly workout routines using Google Gemini API.
"""

from typing import Dict, Any, Optional, Tuple
from ai.gemini_client import generate_completion, WORKOUT_SYSTEM_PROMPT
from database import db
from utils.constants import MEDICAL_DISCLAIMER


def generate_workout_plan(
    profile: Dict[str, Any],
    preferences: Dict[str, Any],
    api_key: Optional[str] = None,
    user_id: Optional[int] = None
) -> Tuple[bool, str]:
    """
    Generates a personalized weekly workout plan using Google Gemini API based on user profile & preferences.
    Saves the plan to the SQLite database if user_id is provided.
    Returns (success: bool, plan_markdown: str).
    """
    name = profile.get("name") or profile.get("full_name", "Athlete")
    age = profile.get("age", 25)
    gender = profile.get("gender", "Male")
    height = profile.get("height") or profile.get("height_cm", 170.0)
    weight = profile.get("weight") or profile.get("weight_kg", 70.0)
    target_weight = profile.get("target_weight") or profile.get("target_weight_kg", 65.0)
    activity_level = profile.get("activity_level", "Moderately Active")
    fitness_goal = profile.get("fitness_goal", "Weight Loss")

    days_per_week = preferences.get("days_per_week", 4)
    duration = preferences.get("duration", preferences.get("duration_min", 45))
    equipment = preferences.get("equipment", "Full Commercial Gym")
    experience = preferences.get("experience", preferences.get("experience_level", "Intermediate"))
    split_type = preferences.get("split_type", "Push - Pull - Legs")

    user_prompt = f"""
Please generate a comprehensive, highly personalized weekly workout plan based on the following user details:

**User Metrics & Profile:**
- Name: {name}
- Age: {age} years old
- Gender: {gender}
- Height: {height} cm
- Weight: {weight} kg
- Target Weight: {target_weight} kg
- Current Activity Level: {activity_level}
- Primary Fitness Goal: {fitness_goal}

**Workout Preferences:**
- Days Available Per Week: {days_per_week} days
- Workout Duration: {duration} minutes per session
- Available Equipment: {equipment}
- Fitness Experience: {experience}
- Preferred Split/Routine Style: {split_type}

**Required Output Structure (in clean, formatted Markdown):**
1. **Overview & Goal Alignment**: Brief rationale on how this plan achieves {fitness_goal} within {duration} minutes.
2. **Weekly Schedule Overview**: Clear day-by-day split layout (e.g. Day 1, Day 2, Rest, etc.).
3. **Daily Workout Breakdowns** (for each active day):
   - **Target Muscle Groups**
   - **Warm-up Routine** (with duration & specific dynamic movements)
   - **Main Exercises Table / List**: Exercise name, Sets, Repetitions, Rest periods between sets, and key form cues
   - **Cool-down & Mobility**: Specific static stretches and recovery cues
4. **Beginner Modifications & Progressions**: Easy adjustments if an exercise feels too hard or too easy.
5. **Safety Guidance & Form Cues**: Practical tips to prevent strain and injury.
"""

    success, content = generate_completion(
        prompt=user_prompt,
        system_message=WORKOUT_SYSTEM_PROMPT,
        api_key=api_key,
        temperature=0.7,
        max_tokens=2500
    )

    if not success:
        # If API key is missing or quota exhausted, generate via smart offline engine
        offline_plan = generate_fallback_workout_plan(profile, preferences)
        final_plan = (
            f"> 💡 **Offline Template Engine Active**: Generated using sports-science guidelines because an active Gemini API key was not detected. "
            f"Add your Gemini API key in the sidebar anytime for real-time Gemini generation.\n\n"
            f"{offline_plan}\n\n---\n\n{MEDICAL_DISCLAIMER}"
        )
    else:
        # Append mandatory medical disclaimer
        final_plan = f"{content.strip()}\n\n---\n\n{MEDICAL_DISCLAIMER}"

    # Persist into database if user_id is provided
    if user_id:
        try:
            db.save_workout_plan(user_id=user_id, plan=final_plan)
        except Exception as e:
            print(f"Error saving workout plan to DB: {e}")

    return True, final_plan


def generate_fallback_workout_plan(profile: Dict[str, Any], preferences: Dict[str, Any]) -> str:
    """Generates an evidence-based, customized workout routine without external API calls."""
    name = profile.get("name") or profile.get("full_name", "Athlete")
    goal = profile.get("fitness_goal", "Weight Loss")
    split = preferences.get("split_type", "Push - Pull - Legs (PPL)")
    days = preferences.get("days_per_week", 4)
    duration = preferences.get("duration", 45)
    equipment = preferences.get("equipment", "Full Commercial Gym")
    exp = preferences.get("experience", "Intermediate")

    reps_guidance = "6–10 reps (hypertrophy & strength focus)" if "Muscle" in goal or "Strength" in goal else "10–15 reps (endurance & metabolic fat-burn focus)"
    rest_guidance = "60–90 seconds between sets"

    md = f"""# 🏋️ Personalized {split} Routine

**Client:** {name} | **Goal:** {goal} | **Level:** {exp}  
**Frequency:** {days} Days/Week | **Duration:** {duration} Minutes/Session | **Gear:** {equipment}

---

## 🎯 Plan Overview & Strategy
This plan utilizes **progressive overload** combined with compound multi-joint movements to maximize metabolic conditioning and lean muscle preservation. With {days} weekly sessions lasting {duration} minutes, rest periods are standardized at {rest_guidance} to optimize cardiovascular recovery and work capacity.

---

## 📅 Weekly Schedule Overview
"""

    if "Upper" in split or "Lower" in split:
        md += """* **Day 1:** Upper Body Strength (Horizontal Push & Pull)
* **Day 2:** Lower Body Power (Squat pattern & Posterior chain)
* **Day 3:** Active Recovery / Light Cardio & Core
* **Day 4:** Upper Body Hypertrophy (Vertical Push & Pull + Arms)
* **Day 5:** Lower Body & Calves / Abs
* **Day 6 & 7:** Rest & Restoration
"""
    elif "Full Body" in split:
        md += """* **Day 1:** Full Body A (Quad dominant + Chest + Row)
* **Day 2:** Rest & Mobility Walk
* **Day 3:** Full Body B (Hinge dominant + Overhead Press + Pull-up)
* **Day 4:** Rest
* **Day 5:** Full Body C (Lunge / Unilateral + Upper Hypertrophy)
* **Day 6 & 7:** Active Recovery & Weekend Stretch
"""
    else: # Default PPL
        md += """* **Day 1:** Push Focus (Chest, Front/Side Delts, Triceps)
* **Day 2:** Pull Focus (Lats, Upper Back, Rear Delts, Biceps)
* **Day 3:** Legs & Core (Quads, Hamstrings, Glutes, Calves)
* **Day 4:** Rest or Cardio Conditioning
* **Day 5:** Upper Body Hybrid & Conditioning
* **Day 6 & 7:** Rest & Active Mobility
"""

    md += f"""
---

## 📋 Detailed Exercise Breakdowns

### Session 1: Primary Compound Focus
* **Warm-up (8–10 Mins):** 5 min light cardiovascular warmup, 10 arm circles, 15 bodyweight squats, cat-cow spine mobilizations.
* **Exercise 1 (Main Compound):** Barbell or Dumbbell Bench Press — 4 sets × {reps_guidance} (Rest: 90s)
* **Exercise 2 (Upper Secondary):** Bent-Over Row or Lat Pulldown — 4 sets × 8–12 reps (Rest: 75s)
* **Exercise 3 (Accessory Movement):** Dumbbell Lateral Raises — 3 sets × 12–15 reps (Rest: 60s)
* **Exercise 4 (Core / Finishing):** Plank Holds — 3 sets × 45–60 seconds (Rest: 45s)
* **Cool-down (5 Mins):** Chest doorway stretch, lat stretches, child's pose.

### Session 2: Lower Body & Posterior Chain Focus
* **Warm-up (8–10 Mins):** 5 min stationary bike, leg swings, glute bridges, dynamic hip openers.
* **Exercise 1 (Primary Hinge/Squat):** Goblet Squats or Barbell Back Squats — 4 sets × {reps_guidance} (Rest: 90s)
* **Exercise 2 (Posterior Chain):** Romanian Deadlifts (RDLs) — 3 sets × 10–12 reps (Rest: 75s)
* **Exercise 3 (Unilateral Leg Work):** Walking Lunges — 3 sets × 12 steps per leg (Rest: 60s)
* **Exercise 4 (Calves):** Standing Calf Raises — 4 sets × 15 reps (Rest: 45s)
* **Cool-down (5 Mins):** Standing quad stretch, seated hamstring reach, pigeon pose.

### Session 3: Accessory & Conditioning
* **Warm-up (6–8 Mins):** Jumping jacks, dynamic arm swings, torso twists.
* **Exercise 1 (Shoulder Press):** Seated Dumbbell Shoulder Press — 3 sets × 10–12 reps (Rest: 75s)
* **Exercise 2 (Biceps & Triceps):** Incline Dumbbell Curls supersetted with Tricep Rope Pushdowns — 3 sets × 12 reps each (Rest: 60s)
* **Exercise 3 (Core):** Hanging Knee Raises or Reverse Crunches — 3 sets × 15 reps (Rest: 45s)
* **Conditioning Finisher:** 10 minutes of steady-state incline treadmill walk or rowing intervals.

---

## 🔄 Beginner Modifications & Safe Progressions
* **Too Intense?** Decrease total sets from 4 to 2–3, or substitute barbell movements with machine/dumbbell variants.
* **Ready for Progression?** When you hit the top of the recommended rep range on all sets with solid form, increase the load by 2.5–5% next week.
"""
    return md


def generate_workout_routine(
    profile: Dict[str, Any],
    preferences: Dict[str, Any],
    api_key: Optional[str] = None
) -> str:
    """Backwards-compatible wrapper returning markdown string directly."""
    success, result = generate_workout_plan(profile, preferences, api_key=api_key)
    return result

