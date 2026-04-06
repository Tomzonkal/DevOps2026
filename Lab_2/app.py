from flask import Flask, request, jsonify
from model_0000 import model
from model_418247 import model as model_418247

app = Flask(__name__)

@app.route('/api/model_v1', methods=['POST'])
def model_v1_input():
    data = request.get_json()
    input = data["input"]
    result_v1 = model.run_model_v1(input)
    return jsonify({'result': result_v1}), 200

@app.route('/api/model_418247', methods=['POST'])
def model_418247_input():
    data = request.get_json()
    input = data["input"]
    result_v1 = model_418247.run_model_v1(input)
    result_v2 = model_418247.run_model_v2(input)
    return jsonify({'result': [result_v1, result_v2]}), 200

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, port=5000)