import pytest
import requests

BASE_URL = "http://localhost:5000"


# --- /uppercase ---


def test_uppercase_basic():
    r = requests.post(f"{BASE_URL}/uppercase", json={"text": "hello"})
    assert r.status_code == 200
    assert r.json() == {"result": "HELLO"}


def test_uppercase_already_upper():
    r = requests.post(f"{BASE_URL}/uppercase", json={"text": "ABC"})
    assert r.status_code == 200
    assert r.json()["result"] == "ABC"


def test_uppercase_empty_text():
    r = requests.post(f"{BASE_URL}/uppercase", json={"text": ""})
    assert r.status_code == 200
    assert r.json()["result"] == ""


def test_uppercase_with_digits():
    r = requests.post(f"{BASE_URL}/uppercase", json={"text": "abc123"})
    assert r.status_code == 200
    assert r.json()["result"] == "ABC123"


def test_uppercase_missing_field():
    r = requests.post(f"{BASE_URL}/uppercase", json={"foo": "bar"})
    assert r.status_code == 400
    assert r.json()["error"] == "Missing field: text"


def test_uppercase_wrong_type():
    r = requests.post(f"{BASE_URL}/uppercase", json={"text": 123})
    assert r.status_code == 400
    assert r.json()["error"] == "Field text must be a string"


# --- /reverse ---


def test_reverse_basic():
    r = requests.post(f"{BASE_URL}/reverse", json={"text": "hello"})
    assert r.status_code == 200
    assert r.json() == {"result": "olleh"}


def test_reverse_empty_text():
    r = requests.post(f"{BASE_URL}/reverse", json={"text": ""})
    assert r.status_code == 200
    assert r.json()["result"] == ""


def test_reverse_with_digits():
    r = requests.post(f"{BASE_URL}/reverse", json={"text": "abc123"})
    assert r.status_code == 200
    assert r.json()["result"] == "321cba"


def test_reverse_palindrome():
    r = requests.post(f"{BASE_URL}/reverse", json={"text": "level"})
    assert r.status_code == 200
    assert r.json()["result"] == "level"


def test_reverse_missing_field():
    r = requests.post(f"{BASE_URL}/reverse", json={})
    assert r.status_code == 400
    assert r.json()["error"] == "Missing field: text"


def test_reverse_wrong_type():
    r = requests.post(f"{BASE_URL}/reverse", json={"text": ["a", "b"]})
    assert r.status_code == 400
    assert r.json()["error"] == "Field text must be a string"


# --- /word-count ---


def test_word_count_basic():
    r = requests.post(f"{BASE_URL}/word-count", json={"text": "one two three"})
    assert r.status_code == 200
    assert r.json() == {"count": 3}


def test_word_count_single_word():
    r = requests.post(f"{BASE_URL}/word-count", json={"text": "word"})
    assert r.status_code == 200
    assert r.json()["count"] == 1


def test_word_count_empty_text():
    r = requests.post(f"{BASE_URL}/word-count", json={"text": ""})
    assert r.status_code == 200
    assert r.json()["count"] == 0


def test_word_count_only_whitespace():
    r = requests.post(f"{BASE_URL}/word-count", json={"text": "     "})
    assert r.status_code == 200
    assert r.json()["count"] == 0


def test_word_count_multiple_spaces():
    r = requests.post(f"{BASE_URL}/word-count", json={"text": "one   two     three"})
    assert r.status_code == 200
    assert r.json()["count"] == 3


def test_word_count_leading_trailing_spaces():
    r = requests.post(f"{BASE_URL}/word-count", json={"text": "   hello world   "})
    assert r.status_code == 200
    assert r.json()["count"] == 2


def test_word_count_with_digits():
    r = requests.post(f"{BASE_URL}/word-count", json={"text": "abc 123 def"})
    assert r.status_code == 200
    assert r.json()["count"] == 3


def test_word_count_missing_field():
    r = requests.post(f"{BASE_URL}/word-count", json={"other": "value"})
    assert r.status_code == 400
    assert r.json()["error"] == "Missing field: text"


def test_word_count_wrong_type():
    r = requests.post(f"{BASE_URL}/word-count", json={"text": 42})
    assert r.status_code == 400
    assert r.json()["error"] == "Field text must be a string"


# --- /health ---


def test_health():
    r = requests.get(f"{BASE_URL}/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


# --- shared edge case: no JSON body ---


def test_uppercase_no_body():
    r = requests.post(f"{BASE_URL}/uppercase")
    assert r.status_code in (400, 415)
