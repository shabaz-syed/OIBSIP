"""Unit conversion and formatting helpers. The API is always queried in metric."""


def c_to_f(celsius):
    return celsius * 9 / 5 + 32


def ms_to_mph(metres_per_second):
    return metres_per_second * 2.23694


def format_temp(celsius, unit):
    """unit is 'C' or 'F'."""
    value = celsius if unit == "C" else c_to_f(celsius)
    return f"{value:.0f}°{unit}"


def format_wind(metres_per_second, unit):
    if unit == "C":
        return f"{metres_per_second:.1f} m/s"
    return f"{ms_to_mph(metres_per_second):.1f} mph"
