# Voice Assistant

A Python voice assistant I built for **Task 1 of the Python Programming track** at Oasis Infobyte (OIBSIP). You speak a command, it understands the intent, does the job, and answers out loud.

I implemented both tiers (Beginner and Advanced) in one project.

## What it can do

| Feature | Example phrase |
|---|---|
| Greeting | "Hello" |
| Time and date | "What time is it?", "What's today's date?" |
| Web search | "Search for Python tutorials" |
| Weather (OpenWeatherMap) | "What's the weather in Bangalore?" |
| Timed reminders | "Remind me in 2 minutes to stretch" |
| Send email (SMTP) | "Send an email" |
| Questions (local knowledge base + Wikipedia) | "Who is Alan Turing?" |
| Custom commands | "Add a command", or edit `assistant/config.json` |
| Exit | "Goodbye" |

If the microphone picks up nothing or the speech isn't understood, the assistant asks you to repeat. After 5 misses in a row it stops listening.

## How it works

1. `speech.py` records from the microphone and converts speech to text (`speech_recognition`). Replies are spoken with `pyttsx3`.
2. `nlu.py` splits the sentence into words, stems them with NLTK's Porter stemmer, and scores them against a keyword set for each intent. The highest score wins, so "what's the weather like in Mumbai" and "how hot is it in Mumbai" both reach the weather handler without needing an exact phrase.
3. `actions.py` holds one function per intent (weather, email, reminders and so on).
4. `main.py` runs the listen, understand, act loop.

## Project structure

```
Python-Task1-VoiceAssistant/
├── main.py                 # entry point
├── assistant/
│   ├── __init__.py
│   ├── speech.py           # speech-to-text and text-to-speech
│   ├── nlu.py              # intent detection
│   ├── actions.py          # feature handlers
│   ├── config.py           # loads and saves config, reads env variables
│   └── config.json         # custom commands, contacts, knowledge base
├── tests/
│   └── test_nlu.py         # unit tests for the intent parser
├── screenshots/            # output screenshots
├── requirements.txt
├── .env.example            # names of the environment variables needed
└── .gitignore
```

## Setup

Python 3.9 or newer is recommended.

```bash
git clone https://github.com/<your-username>/OIBSIP.git
cd OIBSIP/Python-Task1-VoiceAssistant
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS / Linux
pip install -r requirements.txt
```

**PyAudio troubleshooting**
- Windows: `pip install pipwin` then `pipwin install pyaudio`
- Ubuntu: `sudo apt install portaudio19-dev espeak` then reinstall requirements
- macOS: `brew install portaudio` then reinstall requirements

### API keys (environment variables)

Never put keys or passwords in the code. Set these before running (see `.env.example`):

```powershell
# Windows PowerShell
$env:OPENWEATHER_API_KEY="your_key"
$env:ASSISTANT_EMAIL="test.account@gmail.com"
$env:ASSISTANT_EMAIL_PASSWORD="your_app_password"
```

```bash
# macOS / Linux
export OPENWEATHER_API_KEY="your_key"
export ASSISTANT_EMAIL="test.account@gmail.com"
export ASSISTANT_EMAIL_PASSWORD="your_app_password"
```

- Weather key: free at [openweathermap.org](https://openweathermap.org/api).
- Email: use a dummy Gmail account with an app password, not your main account.

## Run

```bash
python main.py
```

## Tests

```bash
python -m unittest discover tests
```

## Privacy

| Data | Where it goes | Stored? |
|---|---|---|
| Microphone audio | Sent to Google's Web Speech API for transcription | No |
| City name | Sent to OpenWeatherMap | No |
| Question topic | Sent to the Wikipedia REST API | No |
| Email recipient, subject, body | Sent through the SMTP server (Gmail) | No |
| Custom commands | Saved in `assistant/config.json` on your machine | Yes, locally |
| Email password, API key | Read from environment variables | Never saved in code or files |

Reminders exist only in memory and disappear when the program closes.

## Limitations

- Speech recognition needs an internet connection.
- Intent detection is keyword-and-stem based, so very unusual phrasing may not be understood.
- Spoken email addresses can be misheard, which is why saved contacts in `config.json` are more reliable.

## Screenshots

Add screenshots of the assistant running in the `screenshots/` folder.

## Author

Shabaz, BCA final year, SDC Degree College, Kolar.
Built during the Oasis Infobyte Internship Programme (#oasisinfobyte).
