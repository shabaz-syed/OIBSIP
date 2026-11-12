



"""Entry point for the voice assistant.  Run with:  python main.py"""
from assistant import actions, config
from assistant.nlu import parse_intent
from assistant.speech import listen, speak

MAX_MISSES = 5


def main():
    cfg = config.load_config()
    actions.greet()
    misses = 0
    while True:
        try:
            text = listen()
        except OSError:
            print("No microphone found. Check your audio input and your PyAudio install.")
            return
        if not text:
            misses += 1
            speak("Sorry, I didn't catch that. Could you please repeat?")
            if misses >= MAX_MISSES:
                speak("I'll stop listening now. Goodbye!")
                break
            continue
        misses = 0

        if actions.run_custom(text, cfg):
            continue

        intent = parse_intent(text)
        if intent == "greeting":
            actions.greet()
        elif intent == "time":
            actions.tell_time()
        elif intent == "date":
            actions.tell_date()
        elif intent == "search":
            actions.web_search(text)
        elif intent == "email":
            actions.send_email(cfg)
        elif intent == "reminder":
            actions.set_reminder(text)
        elif intent == "weather":
            actions.get_weather(text)
        elif intent == "add_command":
            actions.add_custom_command(cfg)
            cfg = config.load_config()
        elif intent == "question":
            actions.answer_question(text, cfg)
        elif intent == "exit":
            speak("Goodbye!")
            break
        else:
            speak("I'm not sure how to help with that yet. You can teach me by saying 'add a command'.")


if __name__ == "__main__":
    main()
