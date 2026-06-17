import pytest
import requests

BASE_URL = "http://localhost:5000"


# ---------------------------------------------------------------------------
# /health
# ---------------------------------------------------------------------------

class TestHealth:
    def test_health_returns_ok(self):
        response = requests.get(f"{BASE_URL}/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}

    def test_health_content_type_is_json(self):
        response = requests.get(f"{BASE_URL}/health")
        assert "application/json" in response.headers.get("Content-Type", "")


# ---------------------------------------------------------------------------
# /uppercase
# ---------------------------------------------------------------------------

class TestUppercase:
    def test_uppercase_basic(self):
        response = requests.post(f"{BASE_URL}/uppercase", json={"text": "hello world"})
        assert response.status_code == 200
        assert response.json() == {"result": "HELLO WORLD"}

    def test_uppercase_already_uppercase(self):
        response = requests.post(f"{BASE_URL}/uppercase", json={"text": "ALREADY"})
        assert response.status_code == 200
        assert response.json()["result"] == "ALREADY"

    def test_uppercase_mixed_case(self):
        response = requests.post(f"{BASE_URL}/uppercase", json={"text": "HeLLo WoRLd"})
        assert response.status_code == 200
        assert response.json()["result"] == "HELLO WORLD"

    def test_uppercase_empty_string(self):
        response = requests.post(f"{BASE_URL}/uppercase", json={"text": ""})
        assert response.status_code == 200
        assert response.json()["result"] == ""

    def test_uppercase_with_digits(self):
        response = requests.post(f"{BASE_URL}/uppercase", json={"text": "abc 123 def"})
        assert response.status_code == 200
        assert response.json()["result"] == "ABC 123 DEF"

    def test_uppercase_multiple_spaces(self):
        response = requests.post(f"{BASE_URL}/uppercase", json={"text": "hello   world"})
        assert response.status_code == 200
        assert response.json()["result"] == "HELLO   WORLD"

    def test_uppercase_missing_text_field(self):
        response = requests.post(f"{BASE_URL}/uppercase", json={"other": "value"})
        assert response.status_code == 400
        assert "error" in response.json()

    def test_uppercase_invalid_type_integer(self):
        response = requests.post(f"{BASE_URL}/uppercase", json={"text": 123})
        assert response.status_code == 400
        assert "error" in response.json()

    def test_uppercase_invalid_type_list(self):
        response = requests.post(f"{BASE_URL}/uppercase", json={"text": ["hello"]})
        assert response.status_code == 400
        assert "error" in response.json()

    def test_uppercase_invalid_type_null(self):
        response = requests.post(f"{BASE_URL}/uppercase", json={"text": None})
        assert response.status_code == 400
        assert "error" in response.json()

    def test_uppercase_no_body(self):
        response = requests.post(f"{BASE_URL}/uppercase", json={})
        assert response.status_code == 400
        assert "error" in response.json()


# ---------------------------------------------------------------------------
# /reverse
# ---------------------------------------------------------------------------

class TestReverse:
    def test_reverse_basic(self):
        response = requests.post(f"{BASE_URL}/reverse", json={"text": "abcde"})
        assert response.status_code == 200
        assert response.json() == {"result": "edcba"}

    def test_reverse_single_character(self):
        response = requests.post(f"{BASE_URL}/reverse", json={"text": "a"})
        assert response.status_code == 200
        assert response.json()["result"] == "a"

    def test_reverse_empty_string(self):
        response = requests.post(f"{BASE_URL}/reverse", json={"text": ""})
        assert response.status_code == 200
        assert response.json()["result"] == ""

    def test_reverse_with_digits(self):
        response = requests.post(f"{BASE_URL}/reverse", json={"text": "abc123"})
        assert response.status_code == 200
        assert response.json()["result"] == "321cba"

    def test_reverse_with_spaces(self):
        response = requests.post(f"{BASE_URL}/reverse", json={"text": "hello world"})
        assert response.status_code == 200
        assert response.json()["result"] == "dlrow olleh"

    def test_reverse_multiple_spaces(self):
        response = requests.post(f"{BASE_URL}/reverse", json={"text": "a   b"})
        assert response.status_code == 200
        assert response.json()["result"] == "b   a"

    def test_reverse_palindrome(self):
        response = requests.post(f"{BASE_URL}/reverse", json={"text": "racecar"})
        assert response.status_code == 200
        assert response.json()["result"] == "racecar"

    def test_reverse_missing_text_field(self):
        response = requests.post(f"{BASE_URL}/reverse", json={"other": "value"})
        assert response.status_code == 400
        assert "error" in response.json()

    def test_reverse_invalid_type_integer(self):
        response = requests.post(f"{BASE_URL}/reverse", json={"text": 42})
        assert response.status_code == 400
        assert "error" in response.json()

    def test_reverse_invalid_type_boolean(self):
        response = requests.post(f"{BASE_URL}/reverse", json={"text": True})
        assert response.status_code == 400
        assert "error" in response.json()

    def test_reverse_no_body(self):
        response = requests.post(f"{BASE_URL}/reverse", json={})
        assert response.status_code == 400
        assert "error" in response.json()


# ---------------------------------------------------------------------------
# /word-count
# ---------------------------------------------------------------------------

class TestWordCount:
    def test_word_count_basic(self):
        response = requests.post(f"{BASE_URL}/word-count", json={"text": "raz dwa trzy"})
        assert response.status_code == 200
        assert response.json() == {"count": 3}

    def test_word_count_single_word(self):
        response = requests.post(f"{BASE_URL}/word-count", json={"text": "hello"})
        assert response.status_code == 200
        assert response.json()["count"] == 1

    def test_word_count_empty_string(self):
        response = requests.post(f"{BASE_URL}/word-count", json={"text": ""})
        assert response.status_code == 200
        assert response.json()["count"] == 0

    def test_word_count_only_spaces(self):
        response = requests.post(f"{BASE_URL}/word-count", json={"text": "   "})
        assert response.status_code == 200
        assert response.json()["count"] == 0

    def test_word_count_multiple_spaces_between_words(self):
        response = requests.post(f"{BASE_URL}/word-count", json={"text": "hello   world"})
        assert response.status_code == 200
        assert response.json()["count"] == 2

    def test_word_count_leading_and_trailing_spaces(self):
        response = requests.post(f"{BASE_URL}/word-count", json={"text": "  hello world  "})
        assert response.status_code == 200
        assert response.json()["count"] == 2

    def test_word_count_with_digits(self):
        response = requests.post(f"{BASE_URL}/word-count", json={"text": "abc 123 def 456"})
        assert response.status_code == 200
        assert response.json()["count"] == 4

    def test_word_count_digits_only(self):
        response = requests.post(f"{BASE_URL}/word-count", json={"text": "1 2 3"})
        assert response.status_code == 200
        assert response.json()["count"] == 3

    def test_word_count_missing_text_field(self):
        response = requests.post(f"{BASE_URL}/word-count", json={"other": "value"})
        assert response.status_code == 400
        assert "error" in response.json()

    def test_word_count_invalid_type_integer(self):
        response = requests.post(f"{BASE_URL}/word-count", json={"text": 99})
        assert response.status_code == 400
        assert "error" in response.json()

    def test_word_count_invalid_type_dict(self):
        response = requests.post(f"{BASE_URL}/word-count", json={"text": {"nested": "value"}})
        assert response.status_code == 400
        assert "error" in response.json()

    def test_word_count_no_body(self):
        response = requests.post(f"{BASE_URL}/word-count", json={})
        assert response.status_code == 400
        assert "error" in response.json()