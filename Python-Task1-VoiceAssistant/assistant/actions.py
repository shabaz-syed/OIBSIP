"""What the assistant actually does once it knows the intent."""
import datetime as dt
import re
import smtplib
import threading
import webbrowser
from email.message import EmailMessage

import requests

from . import config
from .nlu import parse_duration
from .speech import listen, speak

HEADERS = {"User-Agent": "OIBSIP-VoiceAssistant/1.0"}


def greet():
    hour = dt.datetime.now().hour
    part = "morning" if hour < 12 else "afternoon" if hour < 18 else "evening"
    speak(f"Hello! Good {part}. How can I help you?")


def tell_time():
    speak("It's " + dt.datetime.now().strftime("%I:%M %p"))


def tell_date():
    speak("Today is " + dt.datetime.now().strftime("%A, %d %B %Y"))


def web_search(text):
    topic = re.sub(r"\b(search|google|look up|look|find|for|about|on the web|please)\b", "", text).strip()
    if not topic:
        topic = listen("What should I search for?")
        if not topic:
            return speak("I didn't catch the topic.")
    speak(f"Searching the web for {topic}")
    webbrowser.open("https://www.google.com/search?q=" + requests.utils.quote(topic))


def send_email(cfg):
    if not (config.EMAIL_ADDR and config.EMAIL_PASS):
        return speak("Email isn't set up yet. Please set the email environment variables first.")
    who = listen("Who should I send it to? Say a saved contact name or the address.")
    if not who:
        return speak("I didn't catch the recipient.")
    to = cfg["contacts"].get(who) or who.replace(" at ", "@").replace(" dot ", ".").replace(" ", "")
    subject = listen("What's the subject?") or "Message from my voice assistant"
    body = listen("What should the message say?")
    if not body:
        return speak("I didn't catch the message, so I cancelled it.")
    msg = EmailMessage()
    msg["From"], msg["To"], msg["Subject"] = config.EMAIL_ADDR, to, subject
    msg.set_content(body)
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(config.EMAIL_ADDR, config.EMAIL_PASS)
            server.send_message(msg)
        speak("Email sent.")
    except Exception as exc:  # smtplib raises several different errors
        speak("Sorry, I couldn't send the email.")
        print("SMTP error:", exc)


def set_reminder(text):
    duration = parse_duration(text)
    if not duration:
        duration = parse_duration(listen("For how long? For example, 5 minutes.") or "")
        if not duration:
            return speak("I couldn't understand the duration.")
    amount, unit = duration
    seconds = amount * {"second": 1, "minute": 60, "hour": 3600}[unit]
    task = re.search(r"\bto (.+)$", text)
    label = task.group(1) if task else "your timer is up"
    threading.Timer(seconds, lambda: speak(f"Reminder: {label}")).start()
    speak(f"Okay, I'll remind you in {amount} {unit}{'s' if amount != 1 else ''}.")


def get_weather(text):
    if not config.WEATHER_KEY:
        return speak("Weather isn't set up yet. Please set the OpenWeatherMap API key first.")
    match = re.search(r"\bin ([a-z ]+)$", text)
    city = match.group(1).strip() if match else listen("Which city?")
    if not city:
        return speak("I didn't catch the city.")
    try:
        r = requests.get(
            "https://api.openweathermap.org/data/2.5/weather",
            params={"q": city, "appid": config.WEATHER_KEY, "units": "metric"},
            timeout=8,
        )
        if r.status_code != 200:
            return speak(f"I couldn't find weather for {city}.")
        data = r.json()
        desc = data["weather"][0]["description"]
        temp = data["main"]["temp"]
        humidity = data["main"]["humidity"]
        speak(f"In {city} it's {temp:.0f} degrees Celsius with {desc}. Humidity is {humidity} percent.")
    except requests.RequestException:
        speak("I couldn't reach the weather service.")


def answer_question(text, cfg):
    for key, answer in cfg["knowledge_base"].items():
        if key in text:
            return speak(answer)
    topic = re.sub(
        r"\b(what|who|is|are|was|were|the|a|an|tell me about|explain|where|when|why|how|about|of)\b", "", text
    ).strip().replace(" ", "_")
    if not topic:
        return speak("What would you like to know?")
    try:
        r = requests.get(
            "https://en.wikipedia.org/api/rest_v1/page/summary/" + requests.utils.quote(topic),
            headers=HEADERS,
            timeout=8,
        )
        if r.status_code == 200 and r.json().get("extract"):
            sentences = re.split(r"(?<=[.!?]) ", r.json()["extract"])
            return speak(" ".join(sentences[:2]))
    except requests.RequestException:
        pass
    speak("I couldn't find an answer. Try asking me to search the web.")


def add_custom_command(cfg):
    phrase = listen("What phrase should trigger the command?")
    if not phrase:
        return speak("I didn't catch the phrase.")
    kind = listen("Should I say something or open a website? Say 'say' or 'open'.")
    if kind and "open" in kind:
        site = listen("Say the website, for example youtube dot com.")
        if not site:
            return speak("I didn't catch the website.")
        cfg["custom_commands"][phrase] = "open:https://" + site.replace(" dot ", ".").replace(" ", "")
    else:
        reply = listen("What should I say back?")
        if not reply:
            return speak("I didn't catch that.")
        cfg["custom_commands"][phrase] = "say:" + reply
    config.save_config(cfg)
    speak(f"Done. Say '{phrase}' to use it.")


def run_custom(text, cfg):
    """Run a user-defined command if the sentence contains its trigger phrase."""
    for phrase, action in cfg["custom_commands"].items():
        if phrase in text:
            kind, _, value = action.partition(":")
            if kind == "open":
                webbrowser.open(value)
                speak("Opening it now.")
            else:
                speak(value)
            return True
    return False
