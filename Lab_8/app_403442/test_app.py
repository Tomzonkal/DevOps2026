import pytest
import requests

BASE_URL = "http://localhost:5000"


# ---------- /health ----------

def test_health():
    r = requests.get(f"{BASE_URL}/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


# ---------- /uppercase ----------

@pytest.mark.parametrize("payload, expected", [
    ({"text": "hello"}, "HELLO"),
    ({"text": ""}, ""),
    ({"text": "   abc   "}, "   ABC   "),
    ({"text": "abc123"}, "ABC123"),
])
def test_uppercase_valid(payload, expected):
    r = requests.post(f"{BASE_URL}/uppercase", json=payload)
    assert r.status_code == 200
    assert r.json()["result"] == expected


@pytest.mark.parametrize("payload, error_msg", [
    ({}, "Missing field: text"),
    ({"text": 123}, "Field text must be a string"),
])
def test_uppercase_errors(payload, error_msg):
    r = requests.post(f"{BASE_URL}/uppercase", json=payload)
    assert r.status_code == 400
    assert r.json()["error"] == error_msg


# ---------- /reverse ----------

@pytest.mark.parametrize("payload, expected", [
    ({"text": "hello"}, "olleh"),
    ({"text": ""}, ""),
    ({"text": "abc 123"}, "321 cba"),
    ({"text": "  a b  "}, "  b a  "),
])
def test_reverse_valid(payload, expected):
    r = requests.post(f"{BASE_URL}/reverse", json=payload)
    assert r.status_code == 200
    assert r.json()["result"] == expected


@pytest.mark.parametrize("payload, error_msg", [
    ({}, "Missing field: text"),
    ({"text": []}, "Field text must be a string"),
])
def test_reverse_errors(payload, error_msg):
    r = requests.post(f"{BASE_URL}/reverse", json=payload)
    assert r.status_code == 400
    assert r.json()["error"] == error_msg


# ---------- /word-count ----------

@pytest.mark.parametrize("payload, expected", [
    ({"text": "hello world"}, 2),
    ({"text": ""}, 0),
    ({"text": "   "}, 0),
    ({"text": "one   two   three"}, 3),
    ({"text": "abc 123 def"}, 3),
])
def test_word_count_valid(payload, expected):
    r = requests.post(f"{BASE_URL}/word-count", json=payload)
    assert r.status_code == 200
    assert r.json()["count"] == expected


@pytest.mark.parametrize("payload, error_msg", [
    ({}, "Missing field: text"),
    ({"text": 999}, "Field text must be a string"),
])
def test_word_count_errors(payload, error_msg):
    r = requests.post(f"{BASE_URL}/word-count", json=payload)
    assert r.status_code == 400
    assert r.json()["error"] == error_msg