from flask import Flask, request, jsonify

app = Flask(__name__)


def _parse_text(data):
    if data is None or 'text' not in data:
        return None, ('Missing field: text', 400)
    if not isinstance(data['text'], str):
        return None, ('Field text must be a string', 400)
    return data['text'], None


@app.route('/uppercase', methods=['POST'])
def uppercase():
    text, err = _parse_text(request.get_json())
    if err:
        return jsonify({'error': err[0]}), err[1]
    return jsonify({'result': text.upper()})


@app.route('/reverse', methods=['POST'])
def reverse():
    text, err = _parse_text(request.get_json())
    if err:
        return jsonify({'error': err[0]}), err[1]
    return jsonify({'result': text[::-1]})


@app.route('/word-count', methods=['POST'])
def word_count():
    text, err = _parse_text(request.get_json())
    if err:
        return jsonify({'error': err[0]}), err[1]
    count = len(text.split()) if text.strip() else 0
    return jsonify({'count': count})


@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
