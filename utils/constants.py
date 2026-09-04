"""
utils/constants.py - Application Constants & Configurations for AI-FitCoach
"""

APP_NAME = "AI FitCoach"
APP_TAGLINE = "Generative AI Based Personal Fitness Assistant"
APP_VERSION = "2.0.0"

# User Profile Options
GENDERS = ["Male", "Female", "Other / Prefer not to say"]

ACTIVITY_LEVELS = [
    "Sedentary",
    "Lightly Active",
    "Moderately Active",
    "Very Active",
    "Extremely Active"
]

FITNESS_GOALS = [
    "Weight Loss",
    "Muscle Gain",
    "General Fitness",
    "Strength",
    "Endurance",
    "Maintenance"
]

DIETARY_PREFERENCES = [
    "Vegetarian",
    "Non-Vegetarian",
    "Vegan",
    "Eggetarian",
    "Indian",
    "Custom"
]

# Activity Level Factors (Harris-Benedict multipliers)
ACTIVITY_MULTIPLIERS = {
    "Sedentary": 1.2,
    "Lightly Active": 1.375,
    "Moderately Active": 1.55,
    "Very Active": 1.725,
    "Extremely Active": 1.9
}

# Workout Splits
WORKOUT_SPLITS = [
    "Push - Pull - Legs (PPL)",
    "Upper / Lower Split",
    "Full Body Routine (3-4 days/week)",
    "Bro Split (Single muscle group/day)",
    "Cardio & Functional Core"
]

# Equipment Availability
EQUIPMENT_OPTIONS = [
    "Full Commercial Gym (Barbell, Dumbbells, Cables, Machines)",
    "Home Gym (Dumbbells & Adjustable Bench)",
    "Resistance Bands & Pull-Up Bar",
    "Bodyweight / Calisthenics Only"
]

# Fitness Experience
EXPERIENCE_LEVELS = [
    "Beginner (0-6 months)",
    "Intermediate (6 months - 2 years)",
    "Advanced (2+ years)"
]

# Default values
DEFAULT_AGE = 25
DEFAULT_HEIGHT = 170.0
DEFAULT_WEIGHT = 70.0
DEFAULT_TARGET_WEIGHT = 65.0
DEFAULT_WATER = 2.5
DEFAULT_SLEEP = 7.5
DEFAULT_CALORIES = 2200
DEFAULT_STEPS = 8000

# Disclaimer Text
MEDICAL_DISCLAIMER = (
    "⚠️ **Disclaimer**: AI FitCoach provides general educational fitness and nutrition suggestions. "
    "This tool is NOT a medical device, diagnosis, or prescription. Consult a certified medical doctor, "
    "dietitian, or fitness professional before undertaking any strenuous diet or exercise regimen."
)

# Curated Daily Tips & Motivational Quotes
DAILY_TIPS_COLLECTION = [
    {
        "id": 1,
        "category": "Nutrition",
        "tip": "Consume 20–35g of high-quality protein per meal to trigger muscle protein synthesis and maintain prolonged satiety.",
        "quote": "Take care of your body. It's the only place you have to live. — Jim Rohn"
    },
    {
        "id": 2,
        "category": "Hydration",
        "tip": "Drink 500ml of water right after waking up. Your body loses fluid overnight through respiration and sweat.",
        "quote": "Small disciplines repeated with consistency every day lead to great achievements. — John C. Maxwell"
    },
    {
        "id": 3,
        "category": "Exercise",
        "tip": "Control the lowering (eccentric) portion of every repetition for 2 to 3 seconds. Eccentric tension triggers maximum mechanical adaptation.",
        "quote": "The clock is ticking. Are you becoming the person you want to be? — Greg Plitt"
    },
    {
        "id": 4,
        "category": "Sleep & Recovery",
        "tip": "Deep sleep (stages 3 & 4) is when your body releases the vast majority of human growth hormone (HGH) for tissue remodeling.",
        "quote": "Rest when you're weary. Refresh and renew yourself, your body, your mind. — Ralph Marston"
    },
    {
        "id": 5,
        "category": "Consistency",
        "tip": "Progress in fitness is built on compounding small habits. Consistency beats perfection every single week.",
        "quote": "You don't have to be extreme, just consistent. — Anonymous"
    },
    {
        "id": 6,
        "category": "Motivation",
        "tip": "Day-to-day scale fluctuations are largely due to sodium intake, glycogen storage, and water balance, not instant fat gain.",
        "quote": "Action is the foundational key to all success. — Pablo Picasso"
    }
]

