from flask import Flask, request, jsonify
#from model_0000 import model
from model_0000 import model
from model_420344 import model as model_420344

app = Flask(__name__)

@app.route('/api/model_v1', methods=['POST'])
def model_v1_input():
    data = request.get_json()
    input = data["input"]
    result_v1 = model_420344.run_model_v1(input)
    return jsonify({'result': result_v1}), 200

@app.route('/api/model_420344', methods=['POST'])
def model_420344_input():
    data = request.get_json()
    input = data["input"]

    result_v1 = model_420344.run_model_v1(input)
    result_v2 = model_420344.run_model_v2(input)
    result_v3 = model_420344.run_model_v3(input)

    return jsonify({'result': [result_v1, result_v2, result_v3]}), 200

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, port=5000)
