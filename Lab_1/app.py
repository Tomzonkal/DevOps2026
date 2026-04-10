from flask import Flask, jsonify, request
from model_0000 import model as model_0000
from model_401967 import model as model_401967

app = Flask(__name__)


@app.route("/api/model_0000", methods=["POST"])
def model_00000_input():
    data = request.get_json()
    input = data["input"]
    result = model_0000.run_model_0000(input=input)
    return jsonify({"result": result}), 200


@app.route("/api/model_401967", methods=["POST"])
def model_401967_input():
    data = request.get_json()
    input = data["input"]
    result = model_401967.run_model_401967(input=input)
    return jsonify({"result": result}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, port=5000)
