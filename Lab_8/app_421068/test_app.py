import pytest
import requests

BASE_URL = "http://localhost:5000"

# --- /uppercase ---


def test_uppercase_basic():
    r = requests.post(f"{BASE_URL}/uppercase", json={"text": "hello world"})
    assert r.status_code == 200
    assert r.json()["result"] == "HELLO WORLD"


def test_uppercase_already_upper():
    r = requests.post(f"{BASE_URL}/uppercase", json={"text": "ALREADY"})
    assert r.json()["result"] == "ALREADY"


def test_uppercase_empty_string():
    r = requests.post(f"{BASE_URL}/uppercase", json={"text": ""})
    assert r.status_code == 200
    assert r.json()["result"] == ""


def test_uppercase_with_digits():
    r = requests.post(f"{BASE_URL}/uppercase", json={"text": "hello 123"})
    assert r.json()["result"] == "HELLO 123"


def test_uppercase_missing_field():
    r = requests.post(f"{BASE_URL}/uppercase", json={"wrong": "field"})
    assert r.status_code == 400


def test_uppercase_invalid_type():
    r = requests.post(f"{BASE_URL}/uppercase", json={"text": 123})
    assert r.status_code == 400


# --- /reverse ---


def test_reverse_basic():
    r = requests.post(f"{BASE_URL}/reverse", json={"text": "abcde"})
    assert r.status_code == 200
    assert r.json()["result"] == "edcba"


def test_reverse_empty_string():
    r = requests.post(f"{BASE_URL}/reverse", json={"text": ""})
    assert r.json()["result"] == ""


def test_reverse_with_digits():
    r = requests.post(f"{BASE_URL}/reverse", json={"text": "abc123"})
    assert r.json()["result"] == "321cba"


def test_reverse_missing_field():
    r = requests.post(f"{BASE_URL}/reverse", json={})
    assert r.status_code == 400


def test_reverse_invalid_type():
    r = requests.post(f"{BASE_URL}/reverse", json={"text": ["a", "b"]})
    assert r.status_code == 400


# --- /word-count ---


def test_word_count_basic():
    r = requests.post(f"{BASE_URL}/word-count", json={"text": "raz dwa trzy"})
    assert r.status_code == 200
    assert r.json()["count"] == 3


def test_word_count_empty_string():
    r = requests.post(f"{BASE_URL}/word-count", json={"text": ""})
    assert r.json()["count"] == 0


def test_word_count_multiple_spaces():
    r = requests.post(f"{BASE_URL}/word-count", json={"text": "raz   dwa   trzy"})
    assert r.json()["count"] == 3


def test_word_count_only_spaces():
    r = requests.post(f"{BASE_URL}/word-count", json={"text": "   "})
    assert r.json()["count"] == 0


def test_word_count_with_digits():
    r = requests.post(f"{BASE_URL}/word-count", json={"text": "abc 123 xyz"})
    assert r.json()["count"] == 3


def test_word_count_missing_field():
    r = requests.post(f"{BASE_URL}/word-count", json={})
    assert r.status_code == 400


def test_word_count_invalid_type():
    r = requests.post(f"{BASE_URL}/word-count", json={"text": 42})
    assert r.status_code == 400


# --- /health ---


def test_health():
    r = requests.get(f"{BASE_URL}/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"
