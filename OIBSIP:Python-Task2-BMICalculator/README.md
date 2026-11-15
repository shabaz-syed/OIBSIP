# BMI Calculator

A Python BMI calculator I built for **Task 2 of the Python Programming track** at Oasis Infobyte (OIBSIP). It comes in two versions that share the same calculation code:

- **Command-line tool** (`cli.py`), the Beginner tier
- **Desktop app with a GUI** (`main.py`), the Advanced tier, with saved history and a trend graph

## Features

**Beginner (command line)**
- Asks for weight (kg) and height (m)
- Calculates BMI with `BMI = weight / (height²)`
- Classifies the result: Underweight (< 18.5), Normal (18.5 to 24.9), Overweight (25 to 29.9), Obese (30 or more)
- Shows the BMI rounded to 2 decimal places with its category
- Rejects empty, non-numeric, zero and negative values with a clear message, and catches height typed in cm (for example `175`)

**Advanced (GUI)**
- Built with `tkinter`: labelled input fields and a Calculate button
- Colour-coded result (blue = underweight, green = normal, orange = overweight, red = obese)
- Multiple named users, each with their own records
- History saved in an SQLite database and shown in a table, newest first
- Line chart of a user's BMI over time using `matplotlib`, with the normal range shaded
- Error handling for database read and write failures: the app still shows the result and warns if it couldn't save

## Project structure

```
Python-Task2-BMICalculator/
├── main.py              # GUI entry point
├── cli.py               # command-line version
├── bmi/
│   ├── __init__.py
│   ├── calculator.py    # BMI formula, categories, input validation
│   ├── database.py      # SQLite storage
│   └── gui.py           # tkinter interface and chart
├── tests/
│   └── test_bmi.py      # unit tests
├── screenshots/
├── requirements.txt
└── .gitignore
```

The database file is created automatically in a `data/` folder the first time you run the GUI. It is ignored by git.

## Setup

Python 3.9 or newer.

```bash
cd OIBSIP/Python-Task2-BMICalculator
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
python -m pip install -r requirements.txt
```

`tkinter` ships with the python.org installer. If you installed Python with Homebrew on macOS, run `brew install python-tk`. On Ubuntu: `sudo apt install python3-tk`.

## Run

```bash
python main.py     # GUI
python cli.py      # command line
```

## Tests

```bash
python -m unittest discover tests
```

## How to use the GUI

1. Type a user name (or pick an existing one from the dropdown).
2. Enter weight in kg and height in metres, for example `70` and `1.75`.
3. Press **Calculate** (or Enter). The result is saved and added to the history table.
4. Press **Show Trend** to see that user's BMI over time. You need at least two saved records.

## Notes and limitations

- BMI is a general screening number. It doesn't account for muscle mass, age or body composition, so it is not a medical diagnosis.
- Categories are checked on the exact value before rounding, so 24.96 displays as `24.96` and counts as Normal.
- Height must be in metres and weight in kilograms.

## Screenshots

Add screenshots of the CLI and GUI to the `screenshots/` folder.

## Author

Shabaz, BCA final year, SDC Degree College, Kolar.
Built during the Oasis Infobyte Internship Programme (#oasisinfobyte).
