from flask import Flask, request, jsonify
from model_422385 import model as model_422385
app = Flask(__name__)
@app.route('/api/model_422385_v3', methods=['POST'])
def model_422385_v3_input():
    data = request.get_json()
    input = data["input"]
    result_v3 = model_422385.run_model_422385_v3(input)
    return jsonify({'result': result_v3}), 200
if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, port=5000)