from flask import Flask, request, jsonify
from model_0000 import model
from model_422385 import model422385

app = Flask(__name__)

<<<<<<< HEAD
@app.route('/api/model_v2', methods=['POST'])
def model_v2_input():
    data = request.get_json()
    input = data["input"]
    result_v2 = model.run_model_v2(input)
    return jsonify({'result': result_v2}), 200

@app.route('/api/model_v2', methods=['POST'])
def model_v2_input():
    data = request.get_json()
    input = data["input"]
    result_v2 = model422385.run_model_v2(input)
    return jsonify({'result': result_v2}), 200

@app.route('/api/model_v1', methods=['POST'])
def model_v1_input():
    data = request.get_json()
    input = data["input"]
    result_v1 = model422385.run_model_v1(input)
    return jsonify({'result': result_v1}), 200
=======
@app.route('/api/model_v3', methods=['POST'])
def model_v3_input():
    data = request.get_json()
    input = data["input"]
    result_v3 = model.run_model_v3(input)
    return jsonify({'result': result_v3}), 200

@app.route('/api/model_v3', methods=['POST'])
def model_v3_input():
    data = request.get_json()
    input = data["input"]
    result_v3 = model422385.run_model_v3(input)
    return jsonify({'result': result_v3}), 200
>>>>>>> lab_2/new_branch_422385_v3

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, port=5000)
