import threading
import time

import pytest
import requests

BASE_URL = "http://localhost:5000"


def start_server():
    import app

    app.app.run(host="0.0.0.0", port=5000)


@pytest.fixture(scope="session", autouse=True)
def server():
    t = threading.Thread(target=start_server, daemon=True)
    t.start()
    time.sleep(1)


def test_health():
    r = requests.get(f"{BASE_URL}/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_uppercase():
    r = requests.post(f"{BASE_URL}/uppercase", json={"text": "hello world"})
    assert r.status_code == 200
    assert r.json()["result"] == "HELLO WORLD"


def test_reverse():
    r = requests.post(f"{BASE_URL}/reverse", json={"text": "abcde"})
    assert r.status_code == 200
    assert r.json()["result"] == "edcba"


def test_word_count():
    r = requests.post(f"{BASE_URL}/word-count", json={"text": "raz dwa trzy"})
    assert r.status_code == 200
    assert r.json()["count"] == 3


def test_uppercase_empty():
    r = requests.post(f"{BASE_URL}/uppercase", json={"text": ""})
    assert r.status_code == 200
    assert r.json()["result"] == ""


def test_word_count_empty():
    r = requests.post(f"{BASE_URL}/word-count", json={"text": ""})
    assert r.status_code == 200
    assert r.json()["count"] == 0


def test_word_count_multiple_spaces():
    r = requests.post(f"{BASE_URL}/word-count", json={"text": "raz  dwa"})
    assert r.status_code == 200
    assert r.json()["count"] == 2


def test_reverse_numbers():
    r = requests.post(f"{BASE_URL}/reverse", json={"text": "12345"})
    assert r.status_code == 200
    ass