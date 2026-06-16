"""
Testy pytest dla aplikacji Flask (app.py).
Wymagania: pip install pytest requests flask

Uruchomienie:
  1. Uruchom serwer:  python app.py
  2. Uruchom testy:   pytest test_app.py -v
"""

import pytest
import requests

BASE_URL = "http://localhost:5000"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def post(endpoint: str, payload) -> requests.Response:
    """Wysyła żądanie POST z nagłówkiem Content-Type: application/json."""
    return requests.post(
        f"{BASE_URL}{endpoint}",
        json=payload,
        timeout=5,
    )


def post_raw(endpoint: str, data: str) -> requests.Response:
    """Wysyła żądanie POST bez Content-Type (brak nagłówka JSON)."""
    return requests.post(
        f"{BASE_URL}{endpoint}",
        data=data,
        timeout=5,
    )


# ---------------------------------------------------------------------------
# /health
# ---------------------------------------------------------------------------

class TestHealth:
    def test_health_returns_200(self):
        r = requests.get(f"{BASE_URL}/health", timeout=5)
        assert r.status_code == 200

    def test_health_body(self):
        r = requests.get(f"{BASE_URL}/health", timeout=5)
        assert r.json() == {"status": "ok"}


# ---------------------------------------------------------------------------
# /uppercase
# ---------------------------------------------------------------------------

class TestUppercase:
    def test_basic_lowercase(self):
        r = post("/uppercase", {"text": "hello"})
        assert r.status_code == 200
        assert r.json()["result"] == "HELLO"

    def test_already_uppercase(self):
        r = post("/uppercase", {"text": "WORLD"})
        assert r.status_code == 200
        assert r.json()["result"] == "WORLD"

    def test_mixed_case(self):
        r = post("/uppercase", {"text": "Hello World"})
        assert r.status_code == 200
        assert r.json()["result"] == "HELLO WORLD"

    def test_empty_string(self):
        r = post("/uppercase", {"text": ""})
        assert r.status_code == 200
        assert r.json()["result"] == ""

    def test_whitespace_only(self):
        r = post("/uppercase", {"text": "   "})
        assert r.status_code == 200
        assert r.json()["result"] == "   "

    def test_digits_and_symbols(self):
        r = post("/uppercase", {"text": "abc 123 !@#"})
        assert r.status_code == 200
        assert r.json()["result"] == "ABC 123 !@#"

    def test_unicode_letters(self):
        r = post("/uppercase", {"text": "zażółć gęślą jaźń"})
        assert r.status_code == 200
        assert r.json()["result"] == "ZAŻÓŁĆ GĘŚLĄ JAŹŃ"

    def test_missing_text_field(self):
        r = post("/uppercase", {"data": "hello"})
        assert r.status_code == 400
        assert "error" in r.json()

    def test_text_is_integer(self):
        r = post("/uppercase", {"text": 42})
        assert r.status_code == 400
        assert "error" in r.json()

    def test_text_is_list(self):
        r = post("/uppercase", {"text": ["a", "b"]})
        assert r.status_code == 400
        assert "error" in r.json()

    def test_text_is_none(self):
        r = post("/uppercase", {"text": None})
        assert r.status_code == 400
        assert "error" in r.json()

    def test_empty_payload(self):
        r = post("/uppercase", {})
        assert r.status_code == 400
        assert "error" in r.json()

    def test_missing_content_type(self):
        r = post_raw("/uppercase", "hello")
        assert r.status_code in (400, 415)


# ---------------------------------------------------------------------------
# /reverse
# ---------------------------------------------------------------------------

class TestReverse:
    def test_basic_reverse(self):
        r = post("/reverse", {"text": "hello"})
        assert r.status_code == 200
        assert r.json()["result"] == "olleh"

    def test_palindrome(self):
        r = post("/reverse", {"text": "racecar"})
        assert r.status_code == 200
        assert r.json()["result"] == "racecar"

    def test_empty_string(self):
        r = post("/reverse", {"text": ""})
        assert r.status_code == 200
        assert r.json()["result"] == ""

    def test_single_character(self):
        r = post("/reverse", {"text": "x"})
        assert r.status_code == 200
        assert r.json()["result"] == "x"

    def test_whitespace_preserved(self):
        r = post("/reverse", {"text": "ab cd"})
        assert r.status_code == 200
        assert r.json()["result"] == "dc ba"

    def test_digits(self):
        r = post("/reverse", {"text": "12345"})
        assert r.status_code == 200
        assert r.json()["result"] == "54321"

    def test_multiple_spaces(self):
        r = post("/reverse", {"text": "a  b"})
        assert r.status_code == 200
        assert r.json()["result"] == "b  a"

    def test_missing_text_field(self):
        r = post("/reverse", {"value": "hello"})
        assert r.status_code == 400
        assert "error" in r.json()

    def test_text_is_boolean(self):
        r = post("/reverse", {"text": True})
        assert r.status_code == 400
        assert "error" in r.json()

    def test_text_is_dict(self):
        r = post("/reverse", {"text": {"nested": "object"}})
        assert r.status_code == 400
        assert "error" in r.json()

    def test_missing_content_type(self):
        r = post_raw("/reverse", "hello")
        assert r.status_code in (400, 415)


# ---------------------------------------------------------------------------
# /word-count
# ---------------------------------------------------------------------------

class TestWordCount:
    def test_single_word(self):
        r = post("/word-count", {"text": "hello"})
        assert r.status_code == 200
        assert r.json()["count"] == 1

    def test_multiple_words(self):
        r = post("/word-count", {"text": "hello world foo"})
        assert r.status_code == 200
        assert r.json()["count"] == 3

    def test_empty_string(self):
        r = post("/word-count", {"text": ""})
        assert r.status_code == 200
        assert r.json()["count"] == 0

    def test_whitespace_only(self):
        r = post("/word-count", {"text": "   "})
        assert r.status_code == 200
        assert r.json()["count"] == 0

    def test_multiple_spaces_between_words(self):
        r = post("/word-count", {"text": "one  two   three"})
        assert r.status_code == 200
        assert r.json()["count"] == 3

    def test_leading_trailing_spaces(self):
        r = post("/word-count", {"text": "  hello world  "})
        assert r.status_code == 200
        assert r.json()["count"] == 2

    def test_digits_count_as_words(self):
        r = post("/word-count", {"text": "abc 123 456"})
        assert r.status_code == 200
        assert r.json()["count"] == 3

    def test_newline_as_separator(self):
        r = post("/word-count", {"text": "one\ntwo\nthree"})
        assert r.status_code == 200
        assert r.json()["count"] == 3

    def test_tab_as_separator(self):
        r = post("/word-count", {"text": "one\ttwo"})
        assert r.status_code == 200
        assert r.json()["count"] == 2

    def test_missing_text_field(self):
        r = post("/word-count", {"words": "hello"})
        assert r.status_code == 400
        assert "error" in r.json()

    def test_text_is_float(self):
        r = post("/word-count", {"text": 3.14})
        assert r.status_code == 400
        assert "error" in r.json()

    def test_text_is_list(self):
        r = post("/word-count", {"text": ["one", "two"]})
        assert r.status_code == 400
        assert "error" in r.json()

    def test_missing_content_type(self):
        r = post_raw("/word-count", "hello world")
        assert r.status_code in (400, 415)
