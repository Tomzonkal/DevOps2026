import subprocess
import time

import pytest
import requests

BASE_URL = "http://localhost:5000"


@pytest.fixture(scope="session", autouse=True)
def start_server():
    proc = subprocess.Popen(["python3", "app.py"])
    time.sleep(2)
    yield
    proc.terminate()
    proc.wait()


# --- /uppercase ---


def test_uppercase_basic():
    r = requests.post(f"{BASE_URL}/uppercase", json={"text": "hello world"})
    assert r.status_code == 200
    assert r.json()["result"] == "HELLO WORLD"


def test_uppercase_already_upper():
    r = requests.post(f"{BASE_URL}/uppercase", json={"text": "HELLO"})
    assert r.status_code == 200
    assert r.json()["result"] == "HELLO"


def test_uppercase_with_digits():
    r = requests.post(f"{BASE_URL}/uppercase", json={"text": "hello123"})
    assert r.status_code == 200
    assert r.json()["result"] == "HELLO123"


def test_uppercase_empty():
    r = requests.post(f"{BASE_URL}/uppercase", json={"text": ""})
    assert r.status_code == 200
    assert r.json()["result"] == ""


def test_uppercase_missing_field():
    r = requests.post(f"{BASE_URL}/uppercase", json={"foo": "bar"})
    assert r.status_code == 400
    assert "error" in r.json()


def test_uppercase_invalid_type():
    r = requests.post(f"{BASE_URL}/uppercase", json={"text": 123})
    assert r.status_code == 400


# --- /reverse ---


def test_reverse_basic():
    r = requests.post(f"{BASE_URL}/reverse", json={"text": "abcde"})
    assert r.status_code == 200
    assert r.json()["result"] == "edcba"


def test_reverse_empty():
    r = requests.post(f"{BASE_URL}/reverse", json={"text": ""})
    assert r.status_code == 200
    assert r.json()["result"] == ""


def test_reverse_single_char():
    r = requests.post(f"{BASE_URL}/reverse", json={"text": "a"})
    assert r.status_code == 200
    assert r.json()["result"] == "a"


def test_reverse_with_spaces():
    r = requests.post(f"{BASE_URL}/reverse", json={"text": "hello world"})
    assert r.status_code == 200
    assert r.json()["result"] == "dlrow olleh"


def test_reverse_missing_field():
    r = requests.post(f"{BASE_URL}/reverse", json={})
    assert r.status_code == 400


def test_reverse_invalid_type():
    r = requests.post(f"{BASE_URL}/reverse", json={"text": 99.9})
    assert r.status_code == 400


# --- /word-count ---


def test_word_count_basic():
    r = requests.post(f"{BASE_URL}/word-count", json={"text": "raz dwa trzy"})
    assert r.status_code == 200
    assert r.json()["count"] == 3


def test_word_count_single_word():
    r = requests.post(f"{BASE_URL}/word-count", json={"text": "hello"})
    assert r.status_code == 200
    assert r.json()["count"] == 1


def test_word_count_empty():
    r = requests.post(f"{BASE_URL}/word-count", json={"text": ""})
    assert r.status_code == 200
    assert r.json()["count"] == 0


def test_word_count_multiple_spaces():
    r = requests.post(f"{BASE_URL}/word-count", json={"text": "raz  dwa   trzy"})
    assert r.status_code == 200
    assert r.json()["count"] == 3


def test_word_count_missing_field():
    r = requests.post(f"{BASE_URL}/word-count", json={})
    assert r.status_code == 400


def test_word_count_invalid_type():
    r = requests.post(f"{BASE_URL}/word-count", json={"text": ["a", "b"]})
    assert r.status_code == 400


# --- /health ---


def test_health():
    r = requests.get(f"{BASE_URL}/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"
