"""Command-line weather app (Beginner tier).  Run with:  python cli.py"""
from weather import api
from weather.units import c_to_f, ms_to_mph


def show(current):
    print(f"\nWeather in {current.city}, {current.country}")
    print(f"  Condition:   {current.description}")
    print(f"  Temperature: {current.temp_c:.1f} °C / {c_to_f(current.temp_c):.1f} °F")
    print(f"  Humidity:    {current.humidity}%")
    print(f"  Wind speed:  {current.wind_ms:.1f} m/s ({ms_to_mph(current.wind_ms):.1f} mph)\n")


def main():
    print("=== Weather App ===")
    while True:
        text = input("Enter a city name or ZIP code (q to quit): ").strip()
        if text.lower() in ("q", "quit", "exit"):
            print("Goodbye!")
            break
        try:
            show(api.get_current(text))
        except api.WeatherError as exc:
            print(f"Error: {exc}\n")


if __name__ == "__main__":
    main()
