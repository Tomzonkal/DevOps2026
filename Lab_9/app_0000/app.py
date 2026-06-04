from flask import Flask, request, jsonify

app = Flask(__name__)


@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"})


@app.route('/fibonacci', methods=['POST'])
def fibonacci():
    data = request.get_json()
    if not data or 'n' not in data:
        return jsonify({"error": "Missing field 'n'"}), 400
    n = data['n']
    if not isinstance(n, int) or isinstance(n, bool) or n < 0:
        return jsonify({"error": "'n' must be a non-negative integer"}), 400
    if n == 0:
        return jsonify({"result": 0})
    a, b = 0, 1
    for _ in range(n - 1):
        a, b = b, a + b
    return jsonify({"result": b})


@app.route('/is-prime', methods=['POST'])
def is_prime():
    data = request.get_json()
    if not data or 'n' not in data:
        return jsonify({"error": "Missing field 'n'"}), 400
    n = data['n']
    if not isinstance(n, int) or isinstance(n, bool):
        return jsonify({"error": "'n' must be an integer"}), 400
    if n < 2:
        return jsonify({"is_prime": False})
    for i in range(2, int(n ** 0.5) + 1):
        if n % i == 0:
            return jsonify({"is_prime": False})
    return jsonify({"is_prime": True})


@app.route('/sum-digits', methods=['POST'])
def sum_digits():
    data = request.get_json()
    if not data or 'number' not in data:
        return jsonify({"error": "Missing field 'number'"}), 400
    number = data['number']
    if not isinstance(number, int) or isinstance(number, bool):
        return jsonify({"error": "'number' must be an integer"}), 400
    result = sum(int(d) for d in str(abs(number)))
    return jsonify({"result": result})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
