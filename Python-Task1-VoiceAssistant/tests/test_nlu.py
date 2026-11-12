"""Quick tests for the intent parser. Run from the project root:  python -m unittest discover tests"""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from assistant.nlu import parse_duration, parse_intent  # noqa: E402


class IntentTests(unittest.TestCase):
    def test_time(self):
        self.assertEqual(parse_intent("what time is it"), "time")

    def test_date(self):
        self.assertEqual(parse_intent("what is today's date"), "date")

    def test_weather(self):
        self.assertEqual(parse_intent("how is the weather in mumbai"), "weather")

    def test_reminder(self):
        self.assertEqual(parse_intent("remind me in 5 minutes to drink water"), "reminder")

    def test_greeting(self):
        self.assertEqual(parse_intent("hello"), "greeting")

    def test_unknown(self):
        self.assertIsNone(parse_intent("blah blah"))


class DurationTests(unittest.TestCase):
    def test_minutes(self):
        self.assertEqual(parse_duration("in 5 minutes"), (5, "minute"))

    def test_none(self):
        self.assertIsNone(parse_duration("soon"))


if __name__ == "__main__":
    unittest.main()
