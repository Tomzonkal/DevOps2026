"""
Testy pytest dla REST API kalkulatora (calculator.py).

Testy używają biblioteki `requests` do wykonywania prawdziwych żądań HTTP
do działającego serwera Flask. Fixture `server` startuje aplikację
automatycznie, jeśli nie jest jeszcze uruchomiona — dzięki temu testy
przechodzą zarówno lokalnie (serwer w tle wg README), jak i w CI,
gdzie nikt nie uruchamia serwera osobnym krokiem.
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
    """
    Uruchamia calculator.py, jeśli serwer nie jest już dostępny.
    Po zakończeniu testów zamyka proces, który sama wystartowała.
    """
    proc = None
    if not _server_up():
        proc = subprocess.Popen(
            [sys.executable, "calculator.py"],
            cwd=Path(__file__).parent,
        )
        # Czekamy maksymalnie ~15 s aż serwer wstanie
        for _ in range(30):
            if _server_up():
                break
            time.sleep(0.5)
        else:
            if proc:
                proc.terminate()
            raise RuntimeError("Serwer kalkulatora nie wystartował w wyznaczonym czasie")

    yield

    if proc:
        proc.terminate()
        proc.wait()


# --------------------------------------------------------------------------
# /add
# --------------------------------------------------------------------------

def test_add_positive():
    r = requests.post(f"{BASE_URL}/add", json={"a": 10, "b": 5})
    assert r.status_code == 200
    assert r.json() == {"result": 15}


def test_add_negative():
    r = requests.post(f"{BASE_URL}/add", json={"a": -7, "b": -3})
    assert r.status_code == 200
    assert r.json() == {"result": -10}


def test_add_floats():
    r = requests.post(f"{BASE_URL}/add", json={"a": 2.5, "b": 0.5})
    assert r.status_code == 200
    assert r.json() == {"result": 3.0}


# --------------------------------------------------------------------------
# /subtract
# --------------------------------------------------------------------------

def test_subtract_positive():
    r = requests.post(f"{BASE_URL}/subtract", json={"a": 10, "b": 3})
    assert r.status_code == 200
    assert r.json() == {"result": 7}


def test_subtract_result_negative():
    r = requests.post(f"{BASE_URL}/subtract", json={"a": 3, "b": 10})
    assert r.status_code == 200
    assert r.json() == {"result": -7}


def test_subtract_floats():
    r = requests.post(f"{BASE_URL}/subtract", json={"a": 5.5, "b": 2.0})
    assert r.status_code == 200
    assert r.json() == {"result": 3.5}


# --------------------------------------------------------------------------
# /multiply
# --------------------------------------------------------------------------

def test_multiply_positive():
    r = requests.post(f"{BASE_URL}/multiply", json={"a": 4, "b": 5})
    assert r.status_code == 200
    assert r.json() == {"result": 20}


def test_multiply_by_zero():
    r = requests.post(f"{BASE_URL}/multiply", json={"a": 99, "b": 0})
    assert r.status_code == 200
    assert r.json() == {"result": 0}


def test_multiply_negative():
    r = requests.post(f"{BASE_URL}/multiply", json={"a": -4, "b": 5})
    assert r.status_code == 200
    assert r.json() == {"result": -20}


# --------------------------------------------------------------------------
# /divide
# --------------------------------------------------------------------------

def test_divide_positive():
    r = requests.post(f"{BASE_URL}/divide", json={"a": 10, "b": 2})
    assert r.status_code == 200
    assert r.json() == {"result": 5}


def test_divide_floats():
    r = requests.post(f"{BASE_URL}/divide", json={"a": 7, "b": 2})
    assert r.status_code == 200
    assert r.json() == {"result": 3.5}


def test_divide_by_zero():
    r = requests.post(f"{BASE_URL}/divide", json={"a": 10, "b": 0})
    assert r.status_code == 400
    assert "error" in r.json()


# --------------------------------------------------------------------------
# Przypadki błędów — brakujące / niepoprawne pola
# --------------------------------------------------------------------------

def test_missing_field_b():
    r = requests.post(f"{BASE_URL}/add", json={"a": 10})
    assert r.status_code == 400
    assert "error" in r.json()


def test_missing_both_fields():
    r = requests.post(f"{BASE_URL}/add", json={})
    assert r.status_code == 400
    assert "error" in r.json()


def test_non_numeric_field():
    r = requests.post(f"{BASE_URL}/multiply", json={"a": "abc", "b": 2})
    assert r.status_code == 400
    assert "error" in r.json()


# --------------------------------------------------------------------------
# /health
# --------------------------------------------------------------------------

def test_health():
    r = requests.get(f"{BASE_URL}/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}
