from flask import Flask, request, jsonify
from model_421068 import model

app = Flask(__name__)

@app.route('/api/model_421068_v1', methods=['POST'])
def model_421068_v1_input():
    data = request.get_json()
    input = data["input"]
    result_v1 = model.run_model_421068_v1(input)

@app.route('/api/model_v2', methods=['POST'])
def model_421068_v2_input():
    data = request.get_json()
    input = data["input"]
    result_v2 = model.run_model_v1(input)
    return jsonify({'result': result_v1}), 200

@app.route('/api/model_421068_v3', methods=['POST'])
def model_421068_v3_input():
    data = request.get_json()
    input = data["input"]
    result_v3 = model.run_model_421068_v3(input)
    return jsonify({'result': result_v3}), 200

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, port=5000)
