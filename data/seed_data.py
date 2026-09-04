"""
data/seed_data.py - Seeds realistic sample data into fitcoach.db for demonstrations.
Creates demo accounts, biometric profiles, 3 weeks of daily progress logs,
custom workout and diet plans, and AI coach chat dialogue.
"""

import os
import sys
from datetime import datetime, timedelta

# Ensure project root is in path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from database import db
from auth.auth import hash_password


def seed_database(db_path: str = None):
    print("Initializing database tables...")
    db.init_db(db_path=db_path)

    # 1. Check if demo_user already exists
    existing_user = db.get_user_by_username("demo_user", db_path=db_path)
    if existing_user:
        print(f"User 'demo_user' already exists (ID: {existing_user['id']}). Skipping user creation or clearing prior demo data.")
        user_id = existing_user["id"]
    else:
        # Create demo user
        pwd_hash = hash_password("Password123!")
        user_id = db.create_user(
            username="demo_user",
            email="demo@fitcoach.ai",
            password_hash=pwd_hash,
            db_path=db_path
        )
        print(f"Created demo user 'demo_user' (ID: {user_id}) with password 'Password123!'")

    # 2. Seed / Update Profile for Alex Johnson
    profile_data = {
        "full_name": "Alex Johnson",
        "age": 28,
        "gender": "Male",
        "height_cm": 178.0,
        "weight_kg": 76.5,
        "target_weight_kg": 72.0,
        "activity_level": "Moderately Active",
        "fitness_goal": "Weight Loss",
        "diet_preference": "Non-Vegetarian",
        "medical_notes": "Mild lower back stiffness on heavy deadlifts; otherwise healthy."
    }
    db.upsert_profile(user_id, profile_data, db_path=db_path)
    print("Seeded user profile for Alex Johnson (178cm, 76.5kg -> 72kg target).")

    # 3. Seed 21 Days of Realistic Progress Logs
    today = datetime(2026, 9, 4).date()
    progress_days = [
        # (day_offset, weight, water, sleep, calories, workout_done, steps, notes)
        (20, 79.2, 2.7, 7.2, 2350, 1, 9400, "Push Day: Chest, shoulders, triceps. Benchmark bench press 70kg 4x8."),
        (19, 79.0, 3.0, 7.8, 2280, 1, 10200, "Pull Day: Lat pulldowns, barbell bent-over rows, hammer curls."),
        (18, 78.9, 3.2, 8.0, 2150, 1, 11500, "Leg Day: Back squats 90kg, lunges, calf raises. Great pump!"),
        (17, 78.8, 2.8, 7.5, 2200, 0, 8100, "Active Rest: 30 min morning mobility & core stretches."),
        (16, 78.6, 3.1, 8.2, 2100, 1, 12300, "Upper Body Hypertrophy: Incline DB press, cable crossovers."),
        (15, 78.5, 3.0, 7.4, 2180, 1, 10800, "Lower Body & Abs: Romanian deadlifts, leg press, hanging knee raises."),
        (14, 78.5, 2.5, 6.8, 2400, 0, 7200, "Rest day: Attended family dinner. Hydration was a bit low."),
        (13, 78.2, 3.4, 7.9, 2120, 1, 11900, "Push Day: Incline dumbbell press, military press, lateral raises."),
        (12, 78.1, 3.2, 8.1, 2100, 1, 10500, "Pull Day: Weighted pull-ups, seated cable row, face pulls."),
        (11, 77.9, 3.5, 8.0, 2050, 1, 12600, "Leg Day: Front squats, walking lunges with dumbbells. Felt energetic."),
        (10, 77.8, 3.0, 7.6, 2140, 0, 8900, "Rest & foam rolling. Hamstrings feel recovered."),
        (9, 77.6, 3.3, 7.8, 2090, 1, 11400, "Cardio & Full Body HIIT: 25 min kettlebell intervals + rowing."),
        (8, 77.5, 3.2, 8.3, 2080, 1, 10700, "Shoulders & Arms focus: Overhead press, dips, barbell curls."),
        (7, 77.4, 2.9, 7.2, 2300, 0, 7800, "Rest day: Relaxing weekend walk."),
        (6, 77.2, 3.5, 8.0, 2050, 1, 12800, "Heavy Push: Flat bench press increased to 75kg! Tricep pushdowns."),
        (5, 77.0, 3.4, 8.1, 2040, 1, 11200, "Heavy Pull: Deadlifts 110kg 3x5, single-arm DB rows, shrugs."),
        (4, 76.9, 3.2, 7.9, 2080, 1, 11800, "Legs & Core: Leg extensions, hamstring curls, plank circuits."),
        (3, 76.8, 3.0, 7.5, 2150, 0, 8500, "Active recovery: 40 min steady-state brisk outdoor walk."),
        (2, 76.6, 3.6, 8.2, 2020, 1, 13100, "Upper Body Power: Overhead press 50kg, weighted chin-ups."),
        (1, 76.5, 3.5, 8.4, 2000, 1, 12400, "Lower Body Volume: Hack squats, split squats, calf burns."),
        (0, 76.5, 3.4, 8.0, 2050, 1, 10500, "Check-in morning: Great energy, feeling leaner, waist down 2cm.")
    ]

    # Delete existing progress for clean demo state
    conn = db.get_connection(db_path)
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM progress WHERE user_id = ?", (user_id,))
        cur.execute("DELETE FROM workout_plans WHERE user_id = ?", (user_id,))
        cur.execute("DELETE FROM diet_plans WHERE user_id = ?", (user_id,))
        cur.execute("DELETE FROM chat_history WHERE user_id = ?", (user_id,))
        conn.commit()
    finally:
        conn.close()

    for offset, weight, water, sleep, calories, workout, steps, notes in progress_days:
        log_dt = today - timedelta(days=offset)
        db.save_progress(
            user_id=user_id,
            date=log_dt.strftime("%Y-%m-%d"),
            weight=weight,
            water=water,
            sleep=sleep,
            calories=calories,
            workout_completed=workout,
            steps=steps,
            notes=notes,
            db_path=db_path
        )
    print(f"Seeded {len(progress_days)} consecutive daily progress logs.")

    # 4. Seed Saved Workout Plan
    sample_workout = """# 4-Day Push-Pull-Legs & Upper Hypertrophy Routine

**Target Goal:** Weight Loss & Muscle Preservation  
**Experience Level:** Intermediate  
**Weekly Frequency:** 4 Days/Week  
**Session Duration:** 50–60 Minutes

---

### Day 1: Push (Chest, Shoulders, Triceps)
* **Warm-up:** 5 min arm swings, band pull-aparts, rotator cuff rotations.
* **Barbell Flat Bench Press:** 4 sets × 6–8 reps (Rest: 120s)
* **Incline Dumbbell Press:** 3 sets × 8–10 reps (Rest: 90s)
* **Dumbbell Lateral Raises:** 4 sets × 12–15 reps (Rest: 60s)
* **Overhead Cable Tricep Extension:** 3 sets × 12 reps (Rest: 60s)
* **Push-ups (Burnout set):** 1 set to technical failure
* **Cool-down:** 5 min chest and shoulder static stretching.

---

### Day 2: Pull (Back, Rear Delts, Biceps)
* **Warm-up:** 5 min row ergometer + cat-cow stretches.
* **Conventional Barbell Deadlift:** 3 sets × 5 reps (Rest: 150s)
* **Lat Pulldown (Wide Grip):** 4 sets × 8–10 reps (Rest: 90s)
* **Chest-Supported Dumbbell Rows:** 3 sets × 10–12 reps (Rest: 75s)
* **Face Pulls with Cable Rope:** 4 sets × 15 reps (Rest: 60s)
* **Incline Dumbbell Bicep Curls:** 3 sets × 10–12 reps (Rest: 60s)
* **Cool-down:** Lat stretches and child's pose.

---

### Day 3: Legs & Core Focus
* **Warm-up:** 5 min bodyweight squats, hip openers, glute bridges.
* **Barbell Back Squats:** 4 sets × 6–8 reps (Rest: 120s)
* **Romanian Dumbbell Deadlifts:** 3 sets × 8–10 reps (Rest: 90s)
* **Walking Dumbbell Lunges:** 3 sets × 12 steps per leg (Rest: 75s)
* **Standing Calf Raises:** 4 sets × 15 reps (Rest: 45s)
* **Hanging Knee Raises:** 3 sets × 12–15 reps (Rest: 60s)
* **Plank Hold:** 3 sets × 45–60 seconds
* **Cool-down:** Quad, hamstring, and hip flexor stretches.

---

### Day 4: Upper Body Hypertrophy & Arms
* **Seated Overhead Dumbbell Press:** 4 sets × 8–10 reps (Rest: 90s)
* **Neutral-Grip Pull-ups or Lat Pulldowns:** 3 sets × 8–10 reps (Rest: 90s)
* **Dumbbell Flat Flyes:** 3 sets × 12 reps (Rest: 60s)
* **Hammer Curls Supersetted with Tricep Dips:** 3 sets × 12 reps each (Rest: 60s)
* **Farmer's Walk:** 3 sets × 40 meters (Grip and core strength)

---
*Progressive Overload Rule: When you can complete all prescribed sets with the maximum reps in the range, increase weight by 2.5kg next week.*
"""
    db.save_workout_plan(user_id, plan=sample_workout, db_path=db_path)
    print("Seeded sample 4-Day Push-Pull-Legs workout routine.")

    # 5. Seed Saved Diet Plan
    sample_diet = """# High-Protein Fat Loss Meal Plan (2,100 kcal)

**Target Goal:** Gradual Fat Loss with Muscle Retention  
**Caloric Target:** ~2,100 kcal / day  
**Macronutrient Split:** ~165g Protein (31%) | ~210g Carbs (40%) | ~65g Healthy Fats (28%)

---

### 🍳 Meal 1: High-Energy Power Breakfast (8:00 AM)
* **Ingredients:**
  * 3 whole large eggs + 2 egg whites (scrambled with baby spinach)
  * 60g rolled oats cooked in water or unsweetened almond milk
  * 1/2 cup blueberries or fresh berries
  * 1 cup black coffee or green tea
* **Macros:** ~460 kcal | 36g Protein | 42g Carbs | 16g Fat

---

### 🍏 Meal 2: Mid-Morning Micronutrient Snack (11:00 AM)
* **Ingredients:**
  * 170g low-fat Plain Greek Yogurt
  * 15g raw almonds or walnuts
  * 1 medium crisp apple (sliced with cinnamon)
* **Macros:** ~280 kcal | 20g Protein | 30g Carbs | 9g Fat

---

### 🥗 Meal 3: Balanced Hypertrophy Lunch (1:30 PM)
* **Ingredients:**
  * 180g grilled skinless chicken breast or extra-firm tofu
  * 150g cooked brown rice or quinoa
  * 150g steamed broccoli florets and zucchini with 1 tsp extra virgin olive oil
* **Macros:** ~560 kcal | 48g Protein | 55g Carbs | 14g Fat

---

### ⚡ Meal 4: Pre-Workout Primer (4:30 PM)
* **Ingredients:**
  * 1 medium banana
  * 1 scoop (30g) Whey Protein Isolate mixed in 300ml cold water
* **Macros:** ~230 kcal | 26g Protein | 28g Carbs | 2g Fat

---

### 🐟 Meal 5: Lean Recovery Dinner (7:30 PM)
* **Ingredients:**
  * 180g oven-baked Atlantic salmon or grilled white fish
  * 200g baked sweet potato
  * Mixed garden green salad (spinach, cucumber, tomatoes) with lemon juice
* **Macros:** ~570 kcal | 38g Protein | 52g Carbs | 20g Fat

---

### 💧 Hydration & Recovery Protocol
* Drink minimum **3.2 to 3.5 Liters** of filtered water daily.
* Add a pinch of Himalayan pink salt to pre-workout water for optimal muscle pump and electrolyte balance.
"""
    db.save_diet_plan(user_id, plan=sample_diet, db_path=db_path)
    print("Seeded sample 2,100 kcal High-Protein Diet Plan.")

    # 6. Seed AI Coach Conversation History
    chat_turns = [
        ("user", "Hey Coach! What's the optimal time to consume my pre-workout meal?"),
        ("assistant", "Hello Alex! For optimal energy and digestion, aim to eat your pre-workout meal approximately **60 to 90 minutes** before your workout.\n\n"
                      "Focus on easily digestible carbohydrates with moderate lean protein (like your oatmeal with a scoop of protein or a banana with Greek yogurt), "
                      "and keep dietary fat and fiber modest so blood flow remains directed toward your working muscles rather than digestion."),
        ("user", "My hamstrings are feeling super tight and sore after yesterday's Romanian deadlifts. Should I skip legs next time?"),
        ("assistant", "Delayed Onset Muscle Soreness (DOMS) after Romanian Deadlifts is completely normal, especially when eccentric loading is emphasized!\n\n"
                      "You do **not** need to skip your next leg session unless you experience acute, sharp, or asymmetrical pain. Here is the recommended recovery protocol:\n"
                      "1. **Active Recovery:** Do a brisk 20-minute walk or light stationary cycling today to flush lactic acid and enhance blood circulation.\n"
                      "2. **Dynamic Mobility:** Perform gentle hamstring scoops and deep bodyweight lunges.\n"
                      "3. **Hydration & Electrolytes:** Ensure you hit your 3.4L water goal with adequate potassium and sodium."),
        ("user", "Awesome advice! How is my overall weight trend looking based on my recent check-ins?"),
        ("assistant", "You're doing fantastic, Alex! Over the last 3 weeks, you have progressed from **79.2 kg down to 76.5 kg** (a sustainable, healthy loss of 2.7 kg), "
                      "while maintaining your daily step count above 10,000 steps and logging an 85%+ workout adherence rate. Keep prioritizing your protein and 8 hours of sleep!")
    ]

    for role, msg in chat_turns:
        db.save_chat_message(user_id=user_id, role=role, message=msg, db_path=db_path)
    print("Seeded realistic conversational coaching history.")

    # 7. Seed Sarah Miller as a secondary profile
    if not db.get_user_by_username("sarah_fit", db_path=db_path):
        sarah_id = db.create_user(
            username="sarah_fit",
            email="sarah@fitcoach.ai",
            password_hash=hash_password("Password123!"),
            db_path=db_path
        )
        sarah_profile = {
            "full_name": "Sarah Miller",
            "age": 26,
            "gender": "Female",
            "height_cm": 165.0,
            "weight_kg": 59.0,
            "target_weight_kg": 56.0,
            "activity_level": "Very Active",
            "fitness_goal": "Endurance & Toning",
            "diet_preference": "Vegetarian",
            "medical_notes": "None"
        }
        db.upsert_profile(sarah_id, sarah_profile, db_path=db_path)
        print(f"Created secondary demo user 'sarah_fit' (ID: {sarah_id}).")

    print("\n[SUCCESS] Successfully seeded rich sample data into fitcoach.db!")
    print("\nDemo Credentials:")
    print("-----------------------------------------")
    print("Username: demo_user")
    print("Email:    demo@fitcoach.ai")
    print("Password: Password123!")
    print("-----------------------------------------")
    print("Secondary User:")
    print("Username: sarah_fit")
    print("Password: Password123!")
    print("-----------------------------------------")


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else None
    seed_database(target)
