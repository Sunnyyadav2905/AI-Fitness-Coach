"""Utils package for AI-FitCoach."""
from utils.constants import (
    ACTIVITY_LEVELS,
    ACTIVITY_MULTIPLIERS,
    FITNESS_GOALS,
    DIETARY_PREFERENCES,
    GENDERS,
    DAILY_TIPS_COLLECTION,
    APP_NAME,
    APP_TAGLINE,
    MEDICAL_DISCLAIMER
)
from utils.validators import (
    validate_email,
    validate_username,
    validate_password,
    validate_numeric_range,
    validate_age,
    validate_height,
    validate_weight,
    validate_target_weight,
    validate_water,
    validate_sleep,
    validate_calories,
    validate_steps
)
from utils.helpers import (
    is_authenticated,
    format_date,
    format_float,
    calculate_adherence_rate,
    clean_markdown,
    safe_api_output,
    format_database_rows,
    export_dataframe_to_csv
)
from utils.bmi import (
    calculate_bmi,
    get_bmi_category,
    calculate_bmi_and_category,
    get_bmi_color,
    get_bmi_explanation,
    calculate_healthy_weight_range,
    calculate_bmr,
    calculate_tdee,
    calculate_macro_targets,
    calculate_water_target
)

