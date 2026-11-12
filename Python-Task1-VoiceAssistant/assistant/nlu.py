"""Intent detection: stem the words in a sentence and score them against each intent."""
import re

from nltk.stem import PorterStemmer

_stemmer = PorterStemmer()


def _stems(words):
    return {_stemmer.stem(w) for w in words}


# Order matters: on a tie, the intent listed first wins ("what time is it" -> time, not question).
INTENTS = {
    "greeting": _stems(["hello", "hi", "hey", "morning", "evening"]),
    "time": _stems(["time", "clock", "hour"]),
    "date": _stems(["date", "day", "today", "month", "year"]),
    "search": _stems(["search", "google", "look", "browse", "find"]),
    "email": _stems(["email", "mail", "send"]),
    "reminder": _stems(["remind", "reminder", "timer", "alarm"]),
    "weather": _stems(["weather", "temperature", "forecast", "rain", "hot", "cold"]),
    "add_command": _stems(["add", "teach", "custom", "new"]),
    "exit": _stems(["exit", "quit", "bye", "goodbye", "stop"]),
    "question": _stems(["what", "who", "where", "when", "why", "how", "tell", "explain"]),
}


def parse_intent(text):
    """Return the best matching intent name, or None if nothing matches."""
    tokens = _stems(re.findall(r"[a-z0-9']+", text.lower()))
    best, best_score = None, 0
    for name, keys in INTENTS.items():
        score = len(tokens & keys)
        if score > best_score:
            best, best_score = name, score
    return best


def parse_duration(text):
    """Pull '5 minutes' style durations out of a sentence. Returns (amount, unit) or None."""
    match = re.search(r"(\d+)\s*(second|minute|hour)", text)
    return (int(match.group(1)), match.group(2)) if match else None
