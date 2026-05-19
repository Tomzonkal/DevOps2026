import requests

BASE_URL = "http://localhost:5000"


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
    assert r.json()["result"] == "54321"


def test_missing_field():
    r = requests.post(f"{BASE_URL}/uppercase", json={})
    assert r.status_code == 400


def test_invalid_type():
    r = requests.post(f"{BASE_URL}/uppercase", json={"text": 123})
    assert r.status_code == 400
