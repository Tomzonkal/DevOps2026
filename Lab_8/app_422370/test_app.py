import pytest
import requests
import subprocess
import time
import sys


BASE_URL = "http://localhost:5000"


@pytest.fixture(scope="session")
def flask_server():
    """Start Flask server before tests and stop it after completion."""
    # Start Flask server in a separate process
    # Use different flags depending on the operating system
    if sys.platform == "win32":
        # Windows - use CREATE_NEW_PROCESS_GROUP
        process = subprocess.Popen(
            ["python", "app.py"],
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
    else:
        # Linux/Mac - use preexec_fn
        import os
        process = subprocess.Popen(
            ["python", "app.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            preexec_fn=os.setsid
        )
    
    # Wait for the server to start
    max_retries = 30
    for _ in range(max_retries):
        try:
            response = requests.get(f"{BASE_URL}/health", timeout=1)
            if response.status_code == 200:
                break
        except requests.exceptions.RequestException:
            time.sleep(0.1)
    else:
        process.kill()
        pytest.fail("Failed to start Flask server")
    
    yield process
    
    # Terminate the server process
    process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait()


class TestHealthEndpoint:
    """Tests for /health endpoint"""
    
    def test_health_check(self, flask_server):
        """Test basic health check"""
        response = requests.get(f"{BASE_URL}/health")
        assert response.status_code == 200
        assert response.json() == {'status': 'ok'}


class TestUppercaseEndpoint:
    """Tests for /uppercase endpoint"""
    
    def test_uppercase_normal_text(self, flask_server):
        """Test converting normal text to uppercase"""
        response = requests.post(
            f"{BASE_URL}/uppercase",
            json={'text': 'hello world'}
        )
        assert response.status_code == 200
        assert response.json() == {'result': 'HELLO WORLD'}
    
    def test_uppercase_empty_string(self, flask_server):
        """Test with empty string"""
        response = requests.post(
            f"{BASE_URL}/uppercase",
            json={'text': ''}
        )
        assert response.status_code == 200
        assert response.json() == {'result': ''}
    
    def test_uppercase_with_numbers(self, flask_server):
        """Test text with numbers"""
        response = requests.post(
            f"{BASE_URL}/uppercase",
            json={'text': 'test123 abc456'}
        )
        assert response.status_code == 200
        assert response.json() == {'result': 'TEST123 ABC456'}
    
    def test_uppercase_with_multiple_spaces(self, flask_server):
        """Test text with multiple spaces"""
        response = requests.post(
            f"{BASE_URL}/uppercase",
            json={'text': 'hello    world   test'}
        )
        assert response.status_code == 200
        assert response.json() == {'result': 'HELLO    WORLD   TEST'}
    
    def test_uppercase_already_uppercase(self, flask_server):
        """Test text already in uppercase"""
        response = requests.post(
            f"{BASE_URL}/uppercase",
            json={'text': 'ALREADY UPPERCASE'}
        )
        assert response.status_code == 200
        assert response.json() == {'result': 'ALREADY UPPERCASE'}
    
    def test_uppercase_special_characters(self, flask_server):
        """Test with special characters"""
        response = requests.post(
            f"{BASE_URL}/uppercase",
            json={'text': 'hello! @world# $test%'}
        )
        assert response.status_code == 200
        assert response.json() == {'result': 'HELLO! @WORLD# $TEST%'}
    
    def test_uppercase_polish_characters(self, flask_server):
        """Test with Polish characters"""
        response = requests.post(
            f"{BASE_URL}/uppercase",
            json={'text': 'ąćęłńóśźż'}
        )
        assert response.status_code == 200
        assert response.json() == {'result': 'ĄĆĘŁŃÓŚŹŻ'}
    
    def test_uppercase_missing_text_field(self, flask_server):
        """Test without 'text' field"""
        response = requests.post(
            f"{BASE_URL}/uppercase",
            json={'wrong_field': 'value'}
        )
        assert response.status_code == 400
        assert response.json() == {'error': 'Missing field: text'}
    
    def test_uppercase_none_json(self, flask_server):
        """Test with empty body (None)"""
        response = requests.post(
            f"{BASE_URL}/uppercase",
            json=None
        )
        assert response.status_code == 415  # Unsupported Media Type
    
    def test_uppercase_text_not_string(self, flask_server):
        """Test when 'text' field is not a string"""
        response = requests.post(
            f"{BASE_URL}/uppercase",
            json={'text': 123}
        )
        assert response.status_code == 400
        assert response.json() == {'error': 'Field text must be a string'}
    
    def test_uppercase_text_is_list(self, flask_server):
        """Test when 'text' field is a list"""
        response = requests.post(
            f"{BASE_URL}/uppercase",
            json={'text': ['hello', 'world']}
        )
        assert response.status_code == 400
        assert response.json() == {'error': 'Field text must be a string'}
    
    def test_uppercase_text_is_dict(self, flask_server):
        """Test when 'text' field is a dictionary"""
        response = requests.post(
            f"{BASE_URL}/uppercase",
            json={'text': {'nested': 'value'}}
        )
        assert response.status_code == 400
        assert response.json() == {'error': 'Field text must be a string'}


class TestReverseEndpoint:
    """Tests for /reverse endpoint"""
    
    def test_reverse_normal_text(self, flask_server):
        """Test reversing normal text"""
        response = requests.post(
            f"{BASE_URL}/reverse",
            json={'text': 'hello'}
        )
        assert response.status_code == 200
        assert response.json() == {'result': 'olleh'}
    
    def test_reverse_empty_string(self, flask_server):
        """Test with empty string"""
        response = requests.post(
            f"{BASE_URL}/reverse",
            json={'text': ''}
        )
        assert response.status_code == 200
        assert response.json() == {'result': ''}
    
    def test_reverse_with_spaces(self, flask_server):
        """Test text with spaces"""
        response = requests.post(
            f"{BASE_URL}/reverse",
            json={'text': 'hello world'}
        )
        assert response.status_code == 200
        assert response.json() == {'result': 'dlrow olleh'}
    
    def test_reverse_with_multiple_spaces(self, flask_server):
        """Test text with multiple spaces"""
        response = requests.post(
            f"{BASE_URL}/reverse",
            json={'text': 'a  b   c'}
        )
        assert response.status_code == 200
        assert response.json() == {'result': 'c   b  a'}
    
    def test_reverse_with_numbers(self, flask_server):
        """Test with numbers"""
        response = requests.post(
            f"{BASE_URL}/reverse",
            json={'text': '12345'}
        )
        assert response.status_code == 200
        assert response.json() == {'result': '54321'}
    
    def test_reverse_palindrome(self, flask_server):
        """Test with palindrome"""
        response = requests.post(
            f"{BASE_URL}/reverse",
            json={'text': 'racecar'}
        )
        assert response.status_code == 200
        assert response.json() == {'result': 'racecar'}
    
    def test_reverse_special_characters(self, flask_server):
        """Test with special characters"""
        response = requests.post(
            f"{BASE_URL}/reverse",
            json={'text': 'hello!@#'}
        )
        assert response.status_code == 200
        assert response.json() == {'result': '#@!olleh'}
    
    def test_reverse_missing_text_field(self, flask_server):
        """Test without 'text' field"""
        response = requests.post(
            f"{BASE_URL}/reverse",
            json={}
        )
        assert response.status_code == 400
        assert response.json() == {'error': 'Missing field: text'}
    
    def test_reverse_text_not_string(self, flask_server):
        """Test when 'text' field is not a string"""
        response = requests.post(
            f"{BASE_URL}/reverse",
            json={'text': 123}
        )
        assert response.status_code == 400
        assert response.json() == {'error': 'Field text must be a string'}
    
    def test_reverse_text_is_boolean(self, flask_server):
        """Test when 'text' field is a boolean"""
        response = requests.post(
            f"{BASE_URL}/reverse",
            json={'text': True}
        )
        assert response.status_code == 400
        assert response.json() == {'error': 'Field text must be a string'}


class TestWordCountEndpoint:
    """Tests for /word-count endpoint"""
    
    def test_word_count_single_word(self, flask_server):
        """Test counting a single word"""
        response = requests.post(
            f"{BASE_URL}/word-count",
            json={'text': 'hello'}
        )
        assert response.status_code == 200
        assert response.json() == {'count': 1}
    
    def test_word_count_multiple_words(self, flask_server):
        """Test counting multiple words"""
        response = requests.post(
            f"{BASE_URL}/word-count",
            json={'text': 'hello world test'}
        )
        assert response.status_code == 200
        assert response.json() == {'count': 3}
    
    def test_word_count_empty_string(self, flask_server):
        """Test with empty string"""
        response = requests.post(
            f"{BASE_URL}/word-count",
            json={'text': ''}
        )
        assert response.status_code == 200
        assert response.json() == {'count': 0}
    
    def test_word_count_only_spaces(self, flask_server):
        """Test with only spaces"""
        response = requests.post(
            f"{BASE_URL}/word-count",
            json={'text': '     '}
        )
        assert response.status_code == 200
        assert response.json() == {'count': 0}
    
    def test_word_count_multiple_spaces_between_words(self, flask_server):
        """Test with multiple spaces between words"""
        response = requests.post(
            f"{BASE_URL}/word-count",
            json={'text': 'hello    world   test'}
        )
        assert response.status_code == 200
        assert response.json() == {'count': 3}
    
    def test_word_count_leading_trailing_spaces(self, flask_server):
        """Test with leading and trailing spaces"""
        response = requests.post(
            f"{BASE_URL}/word-count",
            json={'text': '  hello world  '}
        )
        assert response.status_code == 200
        assert response.json() == {'count': 2}
    
    def test_word_count_with_numbers(self, flask_server):
        """Test with numbers (numbers are also words)"""
        response = requests.post(
            f"{BASE_URL}/word-count",
            json={'text': 'test 123 abc 456'}
        )
        assert response.status_code == 200
        assert response.json() == {'count': 4}
    
    def test_word_count_with_special_characters(self, flask_server):
        """Test with special characters"""
        response = requests.post(
            f"{BASE_URL}/word-count",
            json={'text': 'hello! world@ test#'}
        )
        assert response.status_code == 200
        assert response.json() == {'count': 3}
    
    def test_word_count_newlines_and_tabs(self, flask_server):
        """Test with newlines and tabs"""
        response = requests.post(
            f"{BASE_URL}/word-count",
            json={'text': 'hello\nworld\ttest'}
        )
        assert response.status_code == 200
        assert response.json() == {'count': 3}
    
    def test_word_count_missing_text_field(self, flask_server):
        """Test without 'text' field"""
        response = requests.post(
            f"{BASE_URL}/word-count",
            json={'data': 'hello world'}
        )
        assert response.status_code == 400
        assert response.json() == {'error': 'Missing field: text'}
    
    def test_word_count_text_not_string(self, flask_server):
        """Test when 'text' field is not a string"""
        response = requests.post(
            f"{BASE_URL}/word-count",
            json={'text': 12345}
        )
        assert response.status_code == 400
        assert response.json() == {'error': 'Field text must be a string'}
    
    def test_word_count_text_is_null(self, flask_server):
        """Test when 'text' field is null"""
        response = requests.post(
            f"{BASE_URL}/word-count",
            json={'text': None}
        )
        assert response.status_code == 400
        assert response.json() == {'error': 'Field text must be a string'}
    
    def test_word_count_text_is_array(self, flask_server):
        """Test when 'text' field is an array"""
        response = requests.post(
            f"{BASE_URL}/word-count",
            json={'text': []}
        )
        assert response.status_code == 400
        assert response.json() == {'error': 'Field text must be a string'}


class TestInvalidRequests:
    """Tests for invalid requests"""
    
    def test_empty_json_body(self, flask_server):
        """Test with empty JSON body"""
        response = requests.post(
            f"{BASE_URL}/uppercase",
            json={}
        )
        assert response.status_code == 400
        assert response.json() == {'error': 'Missing field: text'}
    
    def test_no_content_type(self, flask_server):
        """Test without Content-Type header"""
        response = requests.post(
            f"{BASE_URL}/uppercase",
            data='{"text": "hello"}'
        )
        # Flask returns 415 (Unsupported Media Type) when Content-Type is missing
        assert response.status_code == 415
    
    def test_malformed_json(self, flask_server):
        """Test with malformed JSON"""
        response = requests.post(
            f"{BASE_URL}/uppercase",
            data='{"text": "hello"',  # missing closing bracket
            headers={'Content-Type': 'application/json'}
        )
        assert response.status_code in [400, 500]  # Depends on Flask version
    
    def test_wrong_http_method_get(self, flask_server):
        """Test with wrong HTTP method (GET instead of POST)"""
        response = requests.get(f"{BASE_URL}/uppercase")
        assert response.status_code == 405  # Method Not Allowed
    
    def test_nonexistent_endpoint(self, flask_server):
        """Test non-existent endpoint"""
        response = requests.post(
            f"{BASE_URL}/nonexistent",
            json={'text': 'hello'}
        )
        assert response.status_code == 404


class TestEdgeCases:
    """Tests for edge cases"""
    
    def test_very_long_text(self, flask_server):
        """Test with very long text"""
        long_text = 'a' * 10000
        response = requests.post(
            f"{BASE_URL}/uppercase",
            json={'text': long_text}
        )
        assert response.status_code == 200
        assert response.json() == {'result': 'A' * 10000}
    
    def test_unicode_emoji(self, flask_server):
        """Test with emoji"""
        response = requests.post(
            f"{BASE_URL}/reverse",
            json={'text': 'hello 😀 world'}
        )
        assert response.status_code == 200
        assert 'result' in response.json()
    
    def test_single_space(self, flask_server):
        """Test with single space"""
        response = requests.post(
            f"{BASE_URL}/word-count",
            json={'text': ' '}
        )
        assert response.status_code == 200
        assert response.json() == {'count': 0}
    
    def test_zero_as_text(self, flask_server):
        """Test with zero as value (not string)"""
        response = requests.post(
            f"{BASE_URL}/uppercase",
            json={'text': 0}
        )
        assert response.status_code == 400
        assert response.json() == {'error': 'Field text must be a string'}
