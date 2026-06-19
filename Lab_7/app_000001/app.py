from flask import Flask, jsonify, request

app = Flask(__name__)


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


@app.route("/add", methods=["POST"])
def add():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Brak danych JSON"}), 400

    a = data.get("a")
    b = data.get("b" )

    if a is None or b is None:
        return jsonify({"error": "Wymagane pola: a, b"}), 400

    if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
        return jsonify({"error": "Pola a i b muszą być liczbami"}), 400

    return jsonify({"result": a + b})


@app.route("/subtract", methods=["POST"])
def subtract():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Brak danych JSON"}), 400

    a = data.get("a")
    b = data.get("b")

    if a is None or b is None:
        return jsonify({"error": "Wymagane pola: a, b"}), 400

    if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
        return jsonify({"error": "Pola a i b muszą być liczbami"}), 400

    return jsonify({"result": a - b})


@app.route("/multiply", methods=["POST"])
def multiply():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Brak danych JSON"}), 400

    a = data.get("a")
    b = data.get("b")

    if a is None or b is None:
        return jsonify({"error": "Wymagane pola: a, b"}), 400

    if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
        return jsonify({"error": "Pola a i b muszą być liczbami"}), 400

    return jsonify({"result": a * b})


@app.route("/divide", methods=["POST"])
def divide():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Brak danych JSON"}), 400

    a = data.get("a")
    b = data.get("b")

    if a is None or b is None:
        return jsonify({"error": "Wymagane pola: a, b"}), 400

    if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
        return jsonify({"error": "Pola a i b muszą być liczbami"}), 400

    if b == 0:
        return jsonify({"error": "Dzielenie przez zero"}), 400

    return jsonify({"result": a / b})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
