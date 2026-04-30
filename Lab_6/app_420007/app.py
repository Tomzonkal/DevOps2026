from flask import Flask, jsonify, request

app = Flask(__name__)


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


@app.route("/calculate", methods=["POST"])
def calculate():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Brak danych JSON"}), 400

    a = data.get("a")
    b = data.get("b")
    op = data.get("op")

    if a is None or b is None or op is None:
        return jsonify({"error": "Wymagane pola: a, b, op"}), 400

    if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
        return jsonify({"error": "Pola a i b muszą być liczbami"}), 400

    if op == "+":
        result = a + b
    elif op == "-":
        result = a - b
    elif op == "*":
        result = a * b
    elif op == "/":
        if b == 0:
            return jsonify({"error": "Dzielenie przez zero"}), 400
        result = a / b
    else:
        return jsonify({"error": f"Nieznany operator: {op}"}), 400

    return jsonify({"result": result})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
