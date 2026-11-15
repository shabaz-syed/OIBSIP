"""Tests for BMI logic and the database layer. Run from the project root:  python -m unittest discover tests"""
import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from bmi import database  # noqa: E402
from bmi.calculator import InvalidInputError, calculate_bmi, classify, clean_username, validate_inputs  # noqa: E402


class CalculationTests(unittest.TestCase):
    def test_bmi_value(self):
        self.assertEqual(calculate_bmi(70, 1.75), 22.86)

    def test_category_boundaries(self):
        self.assertEqual(classify(18.4), "Underweight")
        self.assertEqual(classify(18.5), "Normal")
        self.assertEqual(classify(24.9), "Normal")
        self.assertEqual(classify(25), "Overweight")
        self.assertEqual(classify(29.9), "Overweight")
        self.assertEqual(classify(30), "Obese")


class ValidationTests(unittest.TestCase):
    def test_valid(self):
        self.assertEqual(validate_inputs("70", "1.75"), (70.0, 1.75))

    def test_rejects_bad_input(self):
        for weight, height in [("abc", "1.7"), ("70", "xyz"), ("-5", "1.7"), ("70", "-1.7"),
                               ("0", "1.7"), ("", "1.7"), ("70", ""), ("70", "175"), ("nan", "1.7")]:
            with self.assertRaises(InvalidInputError, msg=f"{weight!r}, {height!r}"):
                validate_inputs(weight, height)

    def test_username(self):
        self.assertEqual(clean_username("  Shabaz   K "), "Shabaz K")
        with self.assertRaises(InvalidInputError):
            clean_username("   ")


class DatabaseTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self._original = database.DB_PATH
        database.DB_PATH = Path(self.tmp.name) / "test.db"
        database.init_db()

    def tearDown(self):
        database.DB_PATH = self._original
        self.tmp.cleanup()

    def test_save_and_read_per_user(self):
        database.add_record("asha", 60, 1.65, 22.04, "Normal")
        database.add_record("asha", 62, 1.65, 22.77, "Normal")
        database.add_record("ravi", 90, 1.70, 31.14, "Obese")
        self.assertEqual(len(database.get_records("asha")), 2)
        self.assertEqual(len(database.get_records("ravi")), 1)
        self.assertEqual(database.list_users(), ["asha", "ravi"])

    def test_failure_raises_database_error(self):
        database.DB_PATH = Path(self.tmp.name)  # a folder, not a file, so SQLite cannot open it
        with self.assertRaises(database.DatabaseError):
            database.add_record("asha", 60, 1.65, 22.04, "Normal")


if __name__ == "__main__":
    unittest.main()
