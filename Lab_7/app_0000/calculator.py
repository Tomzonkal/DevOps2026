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
