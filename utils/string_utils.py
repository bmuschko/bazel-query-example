def capitalize_words(text):
    return " ".join(word.capitalize() for word in text.split())


def reverse_string(text):
    return text[::-1]


def count_vowels(text):
    return sum(1 for c in text.lower() if c in "aeiou")
