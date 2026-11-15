"""Weather App package (OIBSIP Python Task 4)."""
from .config import load_env

load_env()  # reads the API key from a local .env file if one exists
