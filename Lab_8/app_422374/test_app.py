"""
Testy pytest dla REST API operacji na tekście (app.py).

Testy używają biblioteki `requests` do wykonywania żądań HTTP do działającego
serwera Flask na localhost:5000. Fixture `server` startuje aplikację sam,
jeśli nie jest jeszcze uruchomiona — dzięki temu testy przechodzą zarówno
lokalnie, jak i w CI (gdzie aplikacja jest podnoszona w tle przez workflow).
"""

import subprocess
import sys
import time
from pathlib import Path

import pytest
import requests

BASE_URL = "http://localhost:5000"


def _server_up():
    """Zwraca True, jeśli serwer odpowiada na /health."""
    try:
        r = requests.get(f"{BASE_URL}/health", timeout=0.5)
        return r.status_code == 200
    except requests.exceptions.RequestException:
        return False


@pytest.fixture(scope="session", autouse=True)
def server():
    """Uruchamia app.py, jeśli serwer nie jest już dostępny; zamyka po testach."""
    proc = None
    if not _server_up():
        proc = subprocess.Popen(
            [sys.executable, "app.py"],
            cwd=Path(__file__).parent,
        )
        for _ in range(30):
            if _server_up():
                break
            time.sleep(0.5)
        else:
            if proc:
                proc.terminate()
            raise RuntimeError("Serwer nie wystartował w wyznaczonym czasie")

    yield

    if proc:
        proc.terminate()
        proc.wait()


# --------------------------------------------------------------------------
# /uppercase
# --------------------------------------------------------------------------

def test_uppercase_basic():
    r = requests.post(f"{BASE_URL}/uppercase", json={"text": "hello world"})
    assert r.status_code == 200
    assert r.json() == {"result": "HELLO WORLD"}


def test_uppercase_with_digits():
    r = requests.post(f"{BASE_URL}/uppercase", json={"text": "abc123"})
    assert r.status_code == 200
    assert r.json() == {"result": "ABC123"}


def test_uppercase_empty():
    r = requests.post(f"{BASE_URL}/uppercase", json={"text": ""})
    assert r.status_code == 200
    assert r.json() == {"result": ""}


# --------------------------------------------------------------------------
# /reverse
# --------------------------------------------------------------------------

def test_reverse_basic():
    r = requests.post(f"{BASE_URL}/reverse", json={"text": "abcde"})
    assert r.status_code == 200
    assert r.json() == {"result": "edcba"}


def test_reverse_with_spaces():
    r = requests.post(f"{BASE_URL}/reverse", json={"text": "ab cd"})
    assert r.status_code == 200
    assert r.json() == {"result": "dc ba"}


def test_reverse_empty():
    r = requests.post(f"{BASE_URL}/reverse", json={"text": ""})
    assert r.status_code == 200
    assert r.json() == {"result": ""}


# --------------------------------------------------------------------------
# /word-count
# --------------------------------------------------------------------------

def test_word_count_basic():
    r = requests.post(f"{BASE_URL}/word-count", json={"text": "raz dwa trzy"})
    assert r.status_code == 200
    assert r.json() == {"count": 3}


def test_word_count_multiple_spaces():
    r = requests.post(f"{BASE_URL}/word-count", json={"text": "raz    dwa"})
    assert r.status_code == 200
    assert r.json() == {"count": 2}


def test_word_count_empty():
    r = requests.post(f"{BASE_URL}/word-count", json={"text": ""})
    assert r.status_code == 200
    assert r.json() == {"count": 0}


def test_word_count_only_spaces():
    r = requests.post(f"{BASE_URL}/word-count", json={"text": "     "})
    assert r.status_code == 200
    assert r.json() == {"count": 0}


# --------------------------------------------------------------------------
# Przypadki błędów
# --------------------------------------------------------------------------

def test_missing_text_field():
    r = requests.post(f"{BASE_URL}/uppercase", json={})
    assert r.status_code == 400
    assert "error" in r.json()


def test_wrong_type_instead_of_string():
    r = requests.post(f"{BASE_URL}/reverse", json={"text": 12345})
    assert r.status_code == 400
    assert "error" in r.json()


def test_word_count_missing_field():
    r = requests.post(f"{BASE_URL}/word-count", json={})
    assert r.status_code == 400
    assert "error" in r.json()


# --------------------------------------------------------------------------
# /health
# --------------------------------------------------------------------------

def test_health():
    r = requests.get(f"{BASE_URL}/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}
