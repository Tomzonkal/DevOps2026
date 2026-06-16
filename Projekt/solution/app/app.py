from flask import Flask, request, jsonify

app = Flask(__name__)


@app.route("/")
def index():
    return jsonify({
        "service": "Calculator API",
        "version": "1.0.0",
        "endpoints": {
            "GET  /health":     "Health check",
            "POST /add":        "Add two numbers",
            "POST /subtract":   "Subtract two numbers",
            "POST /multiply":   "Multiply two numbers",
            "POST /divide":     "Divide two numbers",
        }
    })


@app.route("/health")
def health():
    return jsonify({"status": "ok2"}), 200


def _get_operands(req):
    data = req.get_json(force=True)
    if data is None or "a" not in data or "b" not in data:
        raise ValueError("Request body must contain 'a' and 'b' fields")
    return float(data["a"]), float(data["b"])


@app.route("/add", methods=["POST"])
def add():
    try:
        a, b = _get_operands(request)
        return jsonify({"result": a + b})
    except (ValueError, TypeError) as e:
        return jsonify({"error": str(e)}), 400


@app.route("/subtract", methods=["POST"])
def subtract():
    try:
        a, b = _get_operands(request)
        return jsonify({"result": a - b})
    except (ValueError, TypeError) as e:
        return jsonify({"error": str(e)}), 400


@app.route("/multiply", methods=["POST"])
def multiply():
    try:
        a, b = _get_operands(request)
        return jsonify({"result": a * b})
    except (ValueError, TypeError) as e:
        return jsonify({"error": str(e)}), 400


@app.route("/divide", methods=["POST"])
def divide():
    try:
        a, b = _get_operands(request)
        if b == 0:
            return jsonify({"error": "Division by zero"}), 400
        return jsonify({"result": a / b})
    except (ValueError, TypeError) as e:
        return jsonify({"error": str(e)}), 400


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
