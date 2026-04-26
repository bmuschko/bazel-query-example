import sys

from data.processor import process_numbers, compute_factorials, load_config
from data.validator import validate_name, analyze_text


def main():
    print("=== Bazel Query Example App ===")

    numbers = [1, 2, 3, 4, 5]
    total = process_numbers(numbers)
    print(f"Sum of {numbers}: {total}")

    factorials = compute_factorials(numbers)
    print(f"Factorials: {factorials}")

    valid, result = validate_name("john doe")
    print(f"Name validation: valid={valid}, result={result}")

    analysis = analyze_text("Hello World from Bazel")
    print(f"Text analysis: {analysis}")


if __name__ == "__main__":
    main()
