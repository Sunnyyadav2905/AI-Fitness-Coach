"""
ai/chatbot.py - Conversational Fitness Assistant for AI-FitCoach
Provides interactive fitness coaching, form tips, and nutrition advice using OpenAI GPT.
Maintains chat history and safely redirects medical queries.
"""

from typing import List, Dict, Any, Optional, Tuple
from ai.openai_client import generate_completion, CHATBOT_SYSTEM_PROMPT
from database import db


# Keywords indicating acute medical emergencies
EMERGENCY_KEYWORDS = [
    "chest pain", "heart attack", "can't breathe", "shortness of breath",
    "stroke", "fracture", "broken bone", "fainted", "loss of consciousness",
    "coughing blood", "suicide", "overdose"
]

EMERGENCY_RESPONSE = (
    "🚨 **IMPORTANT MEDICAL ALERT**: If you or someone around you is experiencing acute symptoms "
    "such as severe chest pain, extreme shortness of breath, fainting, or signs of an emergency, "
    "please call your local emergency medical services (such as 911, 112, or local paramedics) or proceed "
    "to the nearest emergency department immediately. As an AI fitness assistant, I cannot diagnose "
    "or manage medical emergencies."
)


def is_medical_emergency(query: str) -> bool:
    """Checks for acute medical emergency indicators."""
    query_lower = (query or "").lower()
    return any(k in query_lower for k in EMERGENCY_KEYWORDS)


def chat_with_coach(
    user_id: int,
    user_message: str,
    profile: Dict[str, Any],
    api_key: Optional[str] = None
) -> Tuple[bool, str]:
    """
    Handles user interaction with the AI fitness chatbot:
    1. Checks for safety/medical emergency keywords.
    2. Retrieves recent conversation history.
    3. Builds message context and queries OpenAI.
    4. Persists the conversation turn to SQLite.
    Returns (success: bool, coach_reply: str).
    """
    clean_message = (user_message or "").strip()
    if not clean_message:
        return False, "Please enter a question or topic for the coach."

    # Immediate emergency safety filter
    if is_medical_emergency(clean_message):
        # Save user message and emergency disclaimer
        try:
            db.save_chat_message(user_id, "user", clean_message)
            db.save_chat_message(user_id, "assistant", EMERGENCY_RESPONSE)
        except Exception:
            pass
        return True, EMERGENCY_RESPONSE

    # Retrieve prior conversation turns
    recent_history = db.get_chat_history(user_id, limit=8)

    # Build context header
    name = profile.get("name") or profile.get("full_name", "User")
    goal = profile.get("fitness_goal", "General Fitness")
    activity = profile.get("activity_level", "Moderately Active")
    weight = profile.get("weight") or profile.get("weight_kg", 70)

    context_prompt = (
        f"[Client Context: Name={name}, Goal={goal}, Weight={weight}kg, Activity={activity}]"
    )

    # Format messages array for OpenAI
    api_messages = [{"role": "system", "content": f"{CHATBOT_SYSTEM_PROMPT}\n\n{context_prompt}"}]

    for msg in recent_history:
        role = "assistant" if msg.get("role") in ["assistant", "coach"] else "user"
        api_messages.append({"role": role, "content": msg.get("message", "")})

    # Add the current user query
    api_messages.append({"role": "user", "content": clean_message})

    # Save user message to database
    try:
        db.save_chat_message(user_id, "user", clean_message)
    except Exception as e:
        print(f"Error saving user chat message: {e}")

    # Generate response
    success, reply = generate_completion(
        prompt="",
        messages=api_messages,
        system_message="",
        api_key=api_key,
        temperature=0.7,
        max_tokens=1200
    )

    if not success:
        # Fallback to smart offline knowledge base
        reply = generate_offline_coach_response(clean_message, profile)

    # Save assistant response to database
    try:
        db.save_chat_message(user_id, "assistant", reply)
    except Exception as e:
        print(f"Error saving assistant chat message: {e}")

    return True, reply


def generate_offline_coach_response(query: str, profile: Dict[str, Any]) -> str:
    """Smart offline response engine for common fitness and nutrition inquiries."""
    q = (query or "").lower()
    name = profile.get("name") or profile.get("full_name", "friend")
    goal = profile.get("fitness_goal", "fitness")
    weight = profile.get("weight") or profile.get("weight_kg", 70.0)

    disclaimer_note = "\n\n> 💡 *Note: Operating in smart offline coaching mode. Add an OpenAI API key in the sidebar for live GPT-4o-mini generation.*"

    if any(w in q for w in ["sore", "soreness", "doms", "stiff", "ache"]):
        return (
            f"Hello {name}! Delayed Onset Muscle Soreness (DOMS) typically peaks 24–48 hours after strenuous or unfamiliar exercise.\n\n"
            "**Recommended Recovery Protocol:**\n"
            "1. **Active Recovery:** 20–30 minutes of low-intensity walking, cycling, or swimming to increase blood flow and flush metabolic waste.\n"
            "2. **Dynamic Mobility:** Light stretching and foam rolling over the affected muscles.\n"
            "3. **Hydration & Sleep:** Aim for at least 3 Liters of water today and 8 hours of quality sleep to optimize muscle protein synthesis.\n"
            "4. **Nutrition:** Ensure you hit your protein target (around 1.6–2.2g per kg of bodyweight) to repair damaged muscle fibers."
            + disclaimer_note
        )
    elif any(w in q for w in ["eat before", "pre-workout", "pre workout", "before workout"]):
        return (
            f"Great question, {name}! For pre-workout fueling:\n\n"
            "**Timing & Food Choices:**\n"
            "* **2–3 Hours Before:** A balanced meal with complex carbs and lean protein (e.g., chicken breast with brown rice or oats with egg whites).\n"
            "* **30–60 Minutes Before:** Easy-to-digest fast carbs with minimal fat and fiber to prevent stomach cramps (e.g., 1 medium banana, 2 rice cakes with honey, or fruit smoothie).\n"
            "* **Hydration:** Drink 400–500ml of water 1 hour prior to ensure proper muscular cellular hydration."
            + disclaimer_note
        )
    elif any(w in q for w in ["eat after", "post-workout", "post workout", "after workout"]):
        return (
            f"Post-workout nutrition is key for your {goal} goal!\n\n"
            "**The Anabolic Recovery Window:**\n"
            "Within 1–2 hours following training, aim to consume:\n"
            "1. **25–40g High-Quality Protein:** Whey isolate, Greek yogurt, chicken breast, or tofu to stimulate Muscle Protein Synthesis (MPS).\n"
            "2. **Carbohydrates:** Re-synthesize depleted glycogen stores with rice, potatoes, oats, or fruit.\n"
            "3. **Rehydration:** Drink 500–750ml of water to replace fluids lost through perspiration."
            + disclaimer_note
        )
    elif any(w in q for w in ["water", "hydration", "drink", "fluid"]):
        target_water = round(float(weight) * 0.035, 1)
        return (
            f"Hydration is fundamental for peak performance and recovery! Based on your bodyweight of {weight} kg, "
            f"your baseline hydration goal is approximately **{target_water} Liters per day**.\n\n"
            "* Tip 1: Drink 500ml of water immediately upon waking to rehydrate after overnight fasting.\n"
            "* Tip 2: Sip water consistently through the day rather than chugging large quantities at once.\n"
            "* Tip 3: If you sweat heavily, add a pinch of electrolyte salts or lemon to your workout bottle."
            + disclaimer_note
        )
    elif any(w in q for w in ["protein", "how much protein"]):
        target_p = int(float(weight) * 2.0)
        return (
            f"For someone with your bodyweight ({weight} kg) aiming for {goal}, certified sports science guidelines "
            f"recommend **1.6 to 2.2 grams of protein per kilogram**.\n\n"
            f"That puts your ideal daily intake around **{target_p} grams of protein per day**.\n"
            "Distribute this across 3–5 meals (~30–40g per meal) to maximize continuous muscle repair."
            + disclaimer_note
        )
    elif any(w in q for w in ["cardio", "running", "treadmill", "steps", "hiit"]):
        return (
            f"Cardiovascular training plays a great role in your {goal} journey, {name}!\n\n"
            "**Recommended Cardio Guidelines:**\n"
            "* **Zone 2 / Low-Intensity Steady State (LISS):** 2–3 sessions of 30–45 minutes per week (e.g., incline walking, jogging) to build mitochondrial density without taxing your nervous system.\n"
            "* **Daily Steps:** Aim for 8,000–10,000 daily steps for steady non-exercise activity thermogenesis (NEAT).\n"
            "* **HIIT:** Limit high-intensity sprint intervals to 1–2 sessions weekly to prevent interference with lifting recovery."
            + disclaimer_note
        )
    else:
        return (
            f"Hello {name}! I'm your AI FitCoach. I'm actively tracking your profile metrics (Goal: {goal}, Weight: {weight} kg).\n\n"
            "I can assist you with:\n"
            "1. **Exercise technique & form cues** (Squats, Bench Press, Deadlifts, Pull-ups)\n"
            "2. **Meal timing & macronutrient targets** for your specific goal\n"
            "3. **Recovery, sleep hygiene, and mobility protocols**\n"
            "4. **Progressive overload and workout split structuring**\n\n"
            "Ask me anything about your training, diet, or recovery!"
            + disclaimer_note
        )


def get_coach_response(
    user_message: str,
    chat_history: List[Dict[str, Any]],
    profile: Dict[str, Any],
    api_key: Optional[str] = None
) -> str:
    """Backwards-compatible wrapper returning reply string directly."""
    if is_medical_emergency(user_message):
        return EMERGENCY_RESPONSE

    # Fallback response generator if called without user_id
    success, reply = generate_completion(
        prompt=user_message,
        system_message=CHATBOT_SYSTEM_PROMPT,
        api_key=api_key
    )
    if success:
        return reply

    return (
        "I'm here to help with your workouts, nutrition, recovery, and fitness habits! "
        "Please check that your OpenAI API key is configured to receive personalized responses."
    )

