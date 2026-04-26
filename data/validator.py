import requests

from utils.string_utils import capitalize_words, count_vowels


def validate_name(name):
    if not name or not name.strip():
        return False, "Name cannot be empty"
    formatted = capitalize_words(name)
    return True, formatted


def validate_url(url):
    try:
        response = requests.head(url, timeout=5)
        return response.status_code < 400
    except requests.RequestException:
        return False


def analyze_text(text):
    vowel_count = count_vowels(text)
    return {
        "text": text,
        "vowel_count": vowel_count,
        "length": len(text),
    }
