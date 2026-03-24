from flask import Flask, request, jsonify
from model_0000 import model
from model_422973 import model as model_422973
app = Flask(__name__)

@app.route('/api/model_v1', methods=['POST'])
def model_v1_input():
    data = request.get_json()
    input = data["input"]
    result_v1 = model.run_model_v1(input)
    return jsonify({'result': result_v1}), 200

@app.route('/api/model_422973', methods=['POST'])
def model_422973_input():
    data = request.get_json()
    input = data["input"]
    result_v1 = model_422973.run_model_422973(input)
    return jsonify({'result': result_v1}), 200

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, port=5000)
