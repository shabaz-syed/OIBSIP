"""Speech input (microphone -> text) and output (text -> speech)."""
import threading

import pyttsx3
import speech_recognition as sr

_recognizer = sr.Recognizer()
_engine = pyttsx3.init()
_lock = threading.Lock()  # reminders speak from a timer thread


def speak(text):
    print(f"Assistant: {text}")
    with _lock:
        _engine.say(text)
        _engine.runAndWait()


def listen(prompt=None):
    """Return the recognised phrase in lowercase, or None if nothing usable was heard."""
    if prompt:
        speak(prompt)
    with sr.Microphone() as source:
        _recognizer.adjust_for_ambient_noise(source, duration=0.5)
        print("Listening...")
        try:
            audio = _recognizer.listen(source, timeout=8, phrase_time_limit=10)
        except sr.WaitTimeoutError:
            return None
    try:
        text = _recognizer.recognize_google(audio).lower()
        print(f"You: {text}")
        return text
    except sr.UnknownValueError:
        return None
    except sr.RequestError:
        speak("I can't reach the speech service. Please check your internet connection.")
        return None
