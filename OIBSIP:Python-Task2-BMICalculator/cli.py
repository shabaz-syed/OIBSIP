"""Command-line BMI calculator (Beginner tier).  Run with:  python cli.py"""
from bmi.calculator import InvalidInputError, calculate_bmi, classify, validate_inputs


def main():
    print("=== BMI Calculator ===")
    while True:
        try:
            weight, height = validate_inputs(input("Weight in kg: "), input("Height in metres (e.g. 1.75): "))
        except InvalidInputError as exc:
            print(f"Error: {exc}\n")
            continue
        bmi = calculate_bmi(weight, height)
        print(f"\nYour BMI is {bmi:.2f} - {classify(bmi)}\n")
        if input("Calculate again? (y/n): ").strip().lower() != "y":
            print("Goodbye!")
            break
        print()


if __name__ == "__main__":
    main()
