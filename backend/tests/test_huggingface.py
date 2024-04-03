from django.test import TestCase
from backend.huggingface import censorbot


class HuggingFaceTest(TestCase):
    def test_censorbot(self):
        self.assertEqual(
            censorbot.detect_hate_speech("Love you")[0]["label"], "nothate"
        )  # nothate
        self.assertEqual(
            censorbot.detect_hate_speech("White are superior than black")[0]["label"],
            "hate",
        )  # hate
        self.assertEqual(
            censorbot.detect_hate_speech("You idiot")[0]["label"], "nothate"
        )  # controversial, but nothate
