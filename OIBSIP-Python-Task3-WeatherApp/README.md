# Weather App

A Python weather app I built for **Task 4 of the Python Programming track** at Oasis Infobyte (OIBSIP). It fetches live data from the OpenWeatherMap API and comes in two versions that share the same API code:

- **Command-line app** (`cli.py`), the Beginner tier
- **Desktop app with a GUI** (`main.py`), the Advanced tier, with icons, forecasts and a unit toggle

## Features

**Beginner (command line)**
- Enter a city name or a ZIP code
- Calls the OpenWeatherMap API and parses the JSON response
- Shows temperature in °C and °F, humidity, a weather description and wind speed
- Handles errors: city not found, network timeout, no connection, invalid API key, too many requests
- Rejects empty input

**Advanced (GUI)**
- `tkinter` window with a city/ZIP field, a **Get Weather** button and a results panel
- Weather icons from the OpenWeatherMap icon URLs (loaded with Pillow)
- Hourly forecast for the next 6 hours
- Daily forecast for the next 5 days (high / low)
- **°C / °F** switch button (changes the display instantly without another API call; wind switches between m/s and mph)
- **Use My Location** button (bonus) that detects your city from your IP address through `ipinfo.io`
- Errors appear inside the window, not in the terminal
- Requests run in a background thread so the window never freezes while loading

## Project structure

```
Python-Task4-WeatherApp/
├── main.py              # GUI entry point
├── cli.py               # command-line version
├── weather/
│   ├── __init__.py
│   ├── api.py           # OpenWeatherMap + ipinfo requests, parsing, error handling
│   ├── units.py         # °C/°F and m/s/mph conversion
│   ├── config.py        # loads the API key from .env
│   └── gui.py           # tkinter interface
├── tests/
│   └── test_weather.py  # unit tests (network mocked)
├── screenshots/
├── requirements.txt
├── .env.example
└── .gitignore
```

## Setup

Python 3.9 or newer.

1. Get a free API key at [openweathermap.org](https://openweathermap.org/api). New keys can take a while to activate, so if you get "Invalid API key" right after signing up, wait and try again. The free tier allows 60 calls per minute.
2. Install and configure:

```bash
cd OIBSIP/Python-Task4-WeatherApp
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
python -m pip install -r requirements.txt
cp .env.example .env              # Windows: copy .env.example .env
```

3. Open `.env` and replace `your_openweathermap_api_key` with your key. (You can also set `OPENWEATHER_API_KEY` as a normal environment variable instead.)

`tkinter` ships with the python.org installer. With Homebrew Python on macOS run `brew install python-tk`. On Ubuntu: `sudo apt install python3-tk`.

## Run

```bash
python main.py     # GUI
python cli.py      # command line
```

You can search by city (`Bengaluru`, `London`) or by ZIP/postal code. US ZIP codes work as typed (`94040`). For other countries add the country code, for example `560001,IN`.

## Tests

```bash
python -m unittest discover tests
```

## Notes and limitations

- The free forecast API returns data in 3-hour steps, so "next 6 hours" shows the 3-hour slots that fall inside the next 6 hours.
- The daily forecast shows the next 5 calendar days (not today). The last day may be partial because the free API covers about 5 days.
- "Use My Location" is based on your IP address, so it is approximate and can be wrong on a VPN or mobile network.
- Wind speed is shown in m/s with °C and in mph with °F.

## Privacy

The city or ZIP you type (or the city detected from your IP) is sent to OpenWeatherMap. "Use My Location" also contacts `ipinfo.io`, which sees your IP address. Nothing is stored on disk apart from your own `.env` file, which is excluded from git.

## Screenshots

Add screenshots of the CLI and GUI to the `screenshots/` folder.

## Author

Shabaz, BCA final year, SDC Degree College, Kolar.
Built during the Oasis Infobyte Internship Programme (#oasisinfobyte).
