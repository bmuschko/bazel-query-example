import yaml

from utils.math_utils import add, multiply, factorial


def load_config(config_path):
    with open(config_path, "r") as f:
        return yaml.safe_load(f)


def process_numbers(numbers):
    total = numbers[0]
    for n in numbers[1:]:
        total = add(total, n)
    return total


def compute_factorials(numbers):
    return [factorial(n) for n in numbers]


def multiply_pairs(pairs):
    return [multiply(a, b) for a, b in pairs]
