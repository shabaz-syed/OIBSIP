"""Core BMI logic: calculation, classification and input validation (no GUI code here)."""

MIN_WEIGHT_KG, MAX_WEIGHT_KG = 1, 500
MIN_HEIGHT_M, MAX_HEIGHT_M = 0.5, 2.8


class InvalidInputError(ValueError):
    """Raised when the user's weight, height or name is not acceptable."""


def calculate_bmi(weight_kg, height_m):
    """BMI = weight / (height ** 2), rounded to 2 decimal places."""
    return round(weight_kg / (height_m ** 2), 2)


def classify(bmi):
    """Return the standard BMI category for a value."""
    if bmi < 18.5:
        return "Underweight"
    if bmi < 25:
        return "Normal"
    if bmi < 30:
        return "Overweight"
    return "Obese"


def _to_number(text, label):
    text = str(text).strip()
    if not text:
        raise InvalidInputError(f"Please enter your {label}.")
    try:
        value = float(text)
    except ValueError:
        raise InvalidInputError(f"{label.capitalize()} must be a number, for example 70 or 1.75.") from None
    if value != value or value in (float("inf"), float("-inf")):
        raise InvalidInputError(f"{label.capitalize()} must be a real number.")
    if value <= 0:
        raise InvalidInputError(f"{label.capitalize()} must be greater than zero.")
    return value


def validate_inputs(weight_text, height_text):
    """Turn raw text into (weight_kg, height_m) or raise InvalidInputError with a helpful message."""
    weight = _to_number(weight_text, "weight (kg)")
    height = _to_number(height_text, "height (m)")
    if not MIN_WEIGHT_KG <= weight <= MAX_WEIGHT_KG:
        raise InvalidInputError(f"Weight should be between {MIN_WEIGHT_KG} and {MAX_WEIGHT_KG} kg.")
    if height > MAX_HEIGHT_M:
        raise InvalidInputError("Height must be in metres, for example 1.75 (not 175).")
    if height < MIN_HEIGHT_M:
        raise InvalidInputError(f"Height should be at least {MIN_HEIGHT_M} m.")
    return weight, height


def clean_username(name):
    name = " ".join(str(name).split())
    if not name:
        raise InvalidInputError("Please enter a user name so your record can be saved.")
    if len(name) > 40:
        raise InvalidInputError("User name must be 40 characters or fewer.")
    return name
