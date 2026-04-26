import unittest

from data.validator import validate_name, analyze_text


class TestValidator(unittest.TestCase):
    def test_validate_name_valid(self):
        valid, result = validate_name("john doe")
        self.assertTrue(valid)
        self.assertEqual(result, "John Doe")

    def test_validate_name_empty(self):
        valid, _ = validate_name("")
        self.assertFalse(valid)

    def test_validate_name_whitespace(self):
        valid, _ = validate_name("   ")
        self.assertFalse(valid)

    def test_analyze_text(self):
        result = analyze_text("hello")
        self.assertEqual(result["vowel_count"], 2)
        self.assertEqual(result["length"], 5)

    def test_analyze_text_no_vowels(self):
        result = analyze_text("xyz")
        self.assertEqual(result["vowel_count"], 0)


if __name__ == "__main__":
    unittest.main()
