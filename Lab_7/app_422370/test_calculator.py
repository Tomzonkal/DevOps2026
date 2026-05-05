"""
Testy pytest dla aplikacji Flask Calculator API.
Testy używają biblioteki requests do wykonywania rzeczywistych żądań HTTP.
"""

import pytest
import requests
import subprocess
import time
import os
import signal


# Konfiguracja
BASE_URL = "http://localhost:5000"
STARTUP_TIMEOUT = 5  # sekundy na uruchomienie serwera


@pytest.fixture(scope="session")
def flask_server():
    """
    Fixture uruchamiający serwer Flask w osobnym procesie na czas sesji testowej.
    """
    # Zapisz kod aplikacji do pliku tymczasowego
    app_code = """
from flask import Flask, request, jsonify
app = Flask(__name__)

def _parse_numbers(data):
    if data is None or 'a' not in data or 'b' not in data:
        return None, None, ('Missing fields: a, b', 400)
    a, b = data['a'], data['b']
    if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
        return None, None, ('Fields a and b must be numbers', 400)
    return a, b, None

@app.route('/add', methods=['POST'])
def add():
    a, b, err = _parse_numbers(request.get_json())
    if err:
        return jsonify({'error': err[0]}), err[1]
    return jsonify({'result': a + b})

@app.route('/subtract', methods=['POST'])
def subtract():
    a, b, err = _parse_numbers(request.get_json())
    if err:
        return jsonify({'error': err[0]}), err[1]
    return jsonify({'result': a - b})

@app.route('/multiply', methods=['POST'])
def multiply():
    a, b, err = _parse_numbers(request.get_json())
    if err:
        return jsonify({'error': err[0]}), err[1]
    return jsonify({'result': a * b})

@app.route('/divide', methods=['POST'])
def divide():
    a, b, err = _parse_numbers(request.get_json())
    if err:
        return jsonify({'error': err[0]}), err[1]
    if b == 0:
        return jsonify({'error': 'Division by zero'}), 400
    return jsonify({'result': a / b})

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
"""
    
    with open('temp_app.py', 'w') as f:
        f.write(app_code)
    
    # Uruchom serwer Flask
    process = subprocess.Popen(
        ['python', 'temp_app.py'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Czekaj aż serwer będzie gotowy
    start_time = time.time()
    server_ready = False
    
    while time.time() - start_time < STARTUP_TIMEOUT:
        try:
            response = requests.get(f"{BASE_URL}/health", timeout=1)
            if response.status_code == 200:
                server_ready = True
                break
        except requests.exceptions.RequestException:
            time.sleep(0.1)
    
    if not server_ready:
        process.kill()
        os.remove('temp_app.py')
        raise RuntimeError("Nie udało się uruchomić serwera Flask")
    
    yield process
    
    # Zakończ serwer po testach
    process.send_signal(signal.SIGTERM)
    process.wait(timeout=5)
    os.remove('temp_app.py')


class TestHealthEndpoint:
    """Testy endpointu /health"""
    
    def test_health_check(self, flask_server):
        """Test podstawowy endpoint health"""
        response = requests.get(f"{BASE_URL}/health")
        assert response.status_code == 200
        assert response.json() == {'status': 'ok'}


class TestAddEndpoint:
    """Testy endpointu /add"""
    
    def test_add_positive_integers(self, flask_server):
        """Test dodawania liczb całkowitych dodatnich"""
        response = requests.post(f"{BASE_URL}/add", json={'a': 5, 'b': 3})
        assert response.status_code == 200
        assert response.json() == {'result': 8}
    
    def test_add_negative_integers(self, flask_server):
        """Test dodawania liczb ujemnych"""
        response = requests.post(f"{BASE_URL}/add", json={'a': -5, 'b': -3})
        assert response.status_code == 200
        assert response.json() == {'result': -8}
    
    def test_add_mixed_sign_integers(self, flask_server):
        """Test dodawania liczb o różnych znakach"""
        response = requests.post(f"{BASE_URL}/add", json={'a': 10, 'b': -3})
        assert response.status_code == 200
        assert response.json() == {'result': 7}
    
    def test_add_floats(self, flask_server):
        """Test dodawania liczb zmiennoprzecinkowych"""
        response = requests.post(f"{BASE_URL}/add", json={'a': 2.5, 'b': 3.7})
        assert response.status_code == 200
        assert response.json()['result'] == pytest.approx(6.2)
    
    def test_add_zero(self, flask_server):
        """Test dodawania z zerem"""
        response = requests.post(f"{BASE_URL}/add", json={'a': 0, 'b': 5})
        assert response.status_code == 200
        assert response.json() == {'result': 5}
    
    def test_add_large_numbers(self, flask_server):
        """Test dodawania dużych liczb"""
        response = requests.post(f"{BASE_URL}/add", json={'a': 1000000, 'b': 2000000})
        assert response.status_code == 200
        assert response.json() == {'result': 3000000}


class TestSubtractEndpoint:
    """Testy endpointu /subtract"""
    
    def test_subtract_positive_integers(self, flask_server):
        """Test odejmowania liczb całkowitych dodatnich"""
        response = requests.post(f"{BASE_URL}/subtract", json={'a': 10, 'b': 3})
        assert response.status_code == 200
        assert response.json() == {'result': 7}
    
    def test_subtract_negative_integers(self, flask_server):
        """Test odejmowania liczb ujemnych"""
        response = requests.post(f"{BASE_URL}/subtract", json={'a': -5, 'b': -3})
        assert response.status_code == 200
        assert response.json() == {'result': -2}
    
    def test_subtract_negative_result(self, flask_server):
        """Test odejmowania dającego ujemny wynik"""
        response = requests.post(f"{BASE_URL}/subtract", json={'a': 3, 'b': 10})
        assert response.status_code == 200
        assert response.json() == {'result': -7}
    
    def test_subtract_floats(self, flask_server):
        """Test odejmowania liczb zmiennoprzecinkowych"""
        response = requests.post(f"{BASE_URL}/subtract", json={'a': 5.5, 'b': 2.3})
        assert response.status_code == 200
        assert response.json()['result'] == pytest.approx(3.2)
    
    def test_subtract_from_zero(self, flask_server):
        """Test odejmowania od zera"""
        response = requests.post(f"{BASE_URL}/subtract", json={'a': 0, 'b': 5})
        assert response.status_code == 200
        assert response.json() == {'result': -5}


class TestMultiplyEndpoint:
    """Testy endpointu /multiply"""
    
    def test_multiply_positive_integers(self, flask_server):
        """Test mnożenia liczb całkowitych dodatnich"""
        response = requests.post(f"{BASE_URL}/multiply", json={'a': 4, 'b': 5})
        assert response.status_code == 200
        assert response.json() == {'result': 20}
    
    def test_multiply_negative_integers(self, flask_server):
        """Test mnożenia liczb ujemnych"""
        response = requests.post(f"{BASE_URL}/multiply", json={'a': -4, 'b': -5})
        assert response.status_code == 200
        assert response.json() == {'result': 20}
    
    def test_multiply_mixed_sign(self, flask_server):
        """Test mnożenia liczb o różnych znakach"""
        response = requests.post(f"{BASE_URL}/multiply", json={'a': -4, 'b': 5})
        assert response.status_code == 200
        assert response.json() == {'result': -20}
    
    def test_multiply_by_zero(self, flask_server):
        """Test mnożenia przez zero"""
        response = requests.post(f"{BASE_URL}/multiply", json={'a': 100, 'b': 0})
        assert response.status_code == 200
        assert response.json() == {'result': 0}
    
    def test_multiply_floats(self, flask_server):
        """Test mnożenia liczb zmiennoprzecinkowych"""
        response = requests.post(f"{BASE_URL}/multiply", json={'a': 2.5, 'b': 4.0})
        assert response.status_code == 200
        assert response.json()['result'] == pytest.approx(10.0)
    
    def test_multiply_by_one(self, flask_server):
        """Test mnożenia przez jeden"""
        response = requests.post(f"{BASE_URL}/multiply", json={'a': 42, 'b': 1})
        assert response.status_code == 200
        assert response.json() == {'result': 42}


class TestDivideEndpoint:
    """Testy endpointu /divide"""
    
    def test_divide_positive_integers(self, flask_server):
        """Test dzielenia liczb całkowitych dodatnich"""
        response = requests.post(f"{BASE_URL}/divide", json={'a': 10, 'b': 2})
        assert response.status_code == 200
        assert response.json() == {'result': 5.0}
    
    def test_divide_negative_integers(self, flask_server):
        """Test dzielenia liczb ujemnych"""
        response = requests.post(f"{BASE_URL}/divide", json={'a': -10, 'b': -2})
        assert response.status_code == 200
        assert response.json() == {'result': 5.0}
    
    def test_divide_mixed_sign(self, flask_server):
        """Test dzielenia liczb o różnych znakach"""
        response = requests.post(f"{BASE_URL}/divide", json={'a': 10, 'b': -2})
        assert response.status_code == 200
        assert response.json() == {'result': -5.0}
    
    def test_divide_floats(self, flask_server):
        """Test dzielenia liczb zmiennoprzecinkowych"""
        response = requests.post(f"{BASE_URL}/divide", json={'a': 7.5, 'b': 2.5})
        assert response.status_code == 200
        assert response.json()['result'] == pytest.approx(3.0)
    
    def test_divide_resulting_in_float(self, flask_server):
        """Test dzielenia dającego wynik zmiennoprzecinkowy"""
        response = requests.post(f"{BASE_URL}/divide", json={'a': 7, 'b': 2})
        assert response.status_code == 200
        assert response.json()['result'] == pytest.approx(3.5)
    
    def test_divide_by_zero(self, flask_server):
        """Test dzielenia przez zero - przypadek brzegowy"""
        response = requests.post(f"{BASE_URL}/divide", json={'a': 10, 'b': 0})
        assert response.status_code == 400
        assert 'error' in response.json()
        assert response.json()['error'] == 'Division by zero'
    
    def test_divide_zero_by_number(self, flask_server):
        """Test dzielenia zera przez liczbę"""
        response = requests.post(f"{BASE_URL}/divide", json={'a': 0, 'b': 5})
        assert response.status_code == 200
        assert response.json() == {'result': 0.0}
    
    def test_divide_by_one(self, flask_server):
        """Test dzielenia przez jeden"""
        response = requests.post(f"{BASE_URL}/divide", json={'a': 42, 'b': 1})
        assert response.status_code == 200
        assert response.json() == {'result': 42.0}


class TestErrorHandling:
    """
    Testy obsługi błędów dla wszystkich endpointów
    
    Uwaga: bool nie jest testowany jako błąd, ponieważ w Pythonie bool dziedziczy po int,
    więc isinstance(True, int) zwraca True. True == 1, False == 0 w kontekście numerycznym.
    """
    
    @pytest.mark.parametrize("endpoint", ['/add', '/subtract', '/multiply', '/divide'])
    def test_missing_field_a(self, flask_server, endpoint):
        """Test braku pola 'a' w JSON"""
        response = requests.post(f"{BASE_URL}{endpoint}", json={'b': 5})
        assert response.status_code == 400
        assert 'error' in response.json()
        assert response.json()['error'] == 'Missing fields: a, b'
    
    @pytest.mark.parametrize("endpoint", ['/add', '/subtract', '/multiply', '/divide'])
    def test_missing_field_b(self, flask_server, endpoint):
        """Test braku pola 'b' w JSON"""
        response = requests.post(f"{BASE_URL}{endpoint}", json={'a': 5})
        assert response.status_code == 400
        assert 'error' in response.json()
        assert response.json()['error'] == 'Missing fields: a, b'
    
    @pytest.mark.parametrize("endpoint", ['/add', '/subtract', '/multiply', '/divide'])
    def test_missing_both_fields(self, flask_server, endpoint):
        """Test braku obu pól w JSON"""
        response = requests.post(f"{BASE_URL}{endpoint}", json={})
        assert response.status_code == 400
        assert 'error' in response.json()
        assert response.json()['error'] == 'Missing fields: a, b'
    
    @pytest.mark.parametrize("endpoint", ['/add', '/subtract', '/multiply', '/divide'])
    def test_empty_json(self, flask_server, endpoint):
        """Test pustego JSONa - Flask zwraca 415 i HTML zamiast JSON"""
        response = requests.post(f"{BASE_URL}{endpoint}", json=None)
        # Flask zwraca 415 gdy json=None (brak Content-Type: application/json)
        assert response.status_code == 415
        # Flask zwraca HTML error page, nie JSON, więc sprawdzamy tylko status
        assert 'text/html' in response.headers.get('Content-Type', '')
    
    @pytest.mark.parametrize("endpoint", ['/add', '/subtract', '/multiply', '/divide'])
    def test_string_instead_of_number_a(self, flask_server, endpoint):
        """Test stringa zamiast liczby w polu 'a'"""
        response = requests.post(f"{BASE_URL}{endpoint}", json={'a': 'text', 'b': 5})
        assert response.status_code == 400
        assert 'error' in response.json()
        assert response.json()['error'] == 'Fields a and b must be numbers'
    
    @pytest.mark.parametrize("endpoint", ['/add', '/subtract', '/multiply', '/divide'])
    def test_string_instead_of_number_b(self, flask_server, endpoint):
        """Test stringa zamiast liczby w polu 'b'"""
        response = requests.post(f"{BASE_URL}{endpoint}", json={'a': 5, 'b': 'text'})
        assert response.status_code == 400
        assert 'error' in response.json()
        assert response.json()['error'] == 'Fields a and b must be numbers'
    
    @pytest.mark.parametrize("endpoint", ['/add', '/subtract', '/multiply', '/divide'])
    def test_null_value_a(self, flask_server, endpoint):
        """Test wartości null w polu 'a'"""
        response = requests.post(f"{BASE_URL}{endpoint}", json={'a': None, 'b': 5})
        assert response.status_code == 400
        assert 'error' in response.json()
    
    @pytest.mark.parametrize("endpoint", ['/add', '/subtract', '/multiply', '/divide'])
    def test_array_instead_of_number(self, flask_server, endpoint):
        """Test tablicy zamiast liczby"""
        response = requests.post(f"{BASE_URL}{endpoint}", json={'a': [1, 2], 'b': 5})
        assert response.status_code == 400
        assert 'error' in response.json()
    
    @pytest.mark.parametrize("endpoint", ['/add', '/subtract', '/multiply', '/divide'])
    def test_object_instead_of_number(self, flask_server, endpoint):
        """Test obiektu zamiast liczby"""
        response = requests.post(f"{BASE_URL}{endpoint}", json={'a': {'val': 1}, 'b': 5})
        assert response.status_code == 400
        assert 'error' in response.json()
    
    @pytest.mark.parametrize("endpoint", ['/add', '/subtract', '/multiply', '/divide'])
    def test_extra_fields_ignored(self, flask_server, endpoint):
        """Test że dodatkowe pola są ignorowane"""
        response = requests.post(f"{BASE_URL}{endpoint}", json={'a': 5, 'b': 3, 'extra': 'ignored'})
        assert response.status_code == 200
        assert 'result' in response.json()
    
    @pytest.mark.parametrize("endpoint", ['/add', '/subtract', '/multiply', '/divide'])
    def test_invalid_json_syntax(self, flask_server, endpoint):
        """Test nieprawidłowej składni JSON"""
        response = requests.post(
            f"{BASE_URL}{endpoint}", 
            data="not valid json",
            headers={'Content-Type': 'application/json'}
        )
        assert response.status_code in [400, 500]  # Flask może zwrócić różne kody dla złego JSON


class TestEdgeCases:
    """Testy przypadków brzegowych"""
    
    def test_very_small_float(self, flask_server):
        """Test bardzo małych liczb zmiennoprzecinkowych"""
        response = requests.post(f"{BASE_URL}/add", json={'a': 0.0000001, 'b': 0.0000002})
        assert response.status_code == 200
        assert response.json()['result'] == pytest.approx(0.0000003)
    
    def test_very_large_numbers(self, flask_server):
        """Test bardzo dużych liczb"""
        response = requests.post(f"{BASE_URL}/multiply", json={'a': 10**15, 'b': 10**15})
        assert response.status_code == 200
        assert response.json()['result'] == pytest.approx(10**30)
    
    def test_negative_zero(self, flask_server):
        """Test z ujemnym zerem"""
        response = requests.post(f"{BASE_URL}/add", json={'a': -0, 'b': 5})
        assert response.status_code == 200
        assert response.json() == {'result': 5}
    
    def test_float_precision(self, flask_server):
        """Test precyzji zmiennoprzecinkowej"""
        response = requests.post(f"{BASE_URL}/add", json={'a': 0.1, 'b': 0.2})
        assert response.status_code == 200
        assert response.json()['result'] == pytest.approx(0.3)
    
    def test_divide_by_negative_zero(self, flask_server):
        """Test dzielenia przez ujemne zero"""
        response = requests.post(f"{BASE_URL}/divide", json={'a': 10, 'b': -0.0})
        assert response.status_code == 400
        assert response.json()['error'] == 'Division by zero'
    
    def test_very_large_float_number(self, flask_server):
        """Test bardzo dużych liczb zmiennoprzecinkowych (zamiast infinity)"""
        # Użyj bardzo dużej liczby, ale nie infinity (która nie jest prawidłowym JSONem)
        large_num = 1.7976931348623157e+308  # blisko max float
        response = requests.post(f"{BASE_URL}/add", json={'a': large_num, 'b': 0})
        assert response.status_code == 200
        assert response.json()['result'] == pytest.approx(large_num)
    
    @pytest.mark.parametrize("endpoint", ['/add', '/subtract', '/multiply', '/divide'])
    def test_wrong_http_method_get(self, flask_server, endpoint):
        """Test użycia niewłaściwej metody HTTP (GET zamiast POST)"""
        response = requests.get(f"{BASE_URL}{endpoint}")
        assert response.status_code == 405  # Method Not Allowed


class TestHTTPHeaders:
    """Testy nagłówków HTTP"""
    
    @pytest.mark.parametrize("endpoint", ['/add', '/subtract', '/multiply', '/divide'])
    def test_response_content_type(self, flask_server, endpoint):
        """Test że odpowiedź ma prawidłowy Content-Type"""
        response = requests.post(f"{BASE_URL}{endpoint}", json={'a': 5, 'b': 3})
        assert 'application/json' in response.headers.get('Content-Type', '')
    
    @pytest.mark.parametrize("endpoint", ['/add', '/subtract', '/multiply', '/divide'])
    def test_request_without_content_type(self, flask_server, endpoint):
        """Test żądania bez nagłówka Content-Type"""
        response = requests.post(
            f"{BASE_URL}{endpoint}",
            data='{"a": 5, "b": 3}'
        )
        # Bez Content-Type: application/json Flask może nie sparsować JSONa
        assert response.status_code in [400, 415, 500]


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
