from flask import Flask, request, jsonify
from model_401967 import model as model

app = Flask(__name__)

@app.route('/api/model_v2', methods=['POST'])
def model_v2_input():
    data = request.get_json()
    input = data["input"]
    result_v2 = model.run_model_v2(input)
    return jsonify({'result': result_v2}), 200

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, port=5000)
