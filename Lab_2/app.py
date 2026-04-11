from flask import Flask, request, jsonify
from model_422364 import model

app = Flask(__name__)

@app.route('/api/model_v3', methods=['POST'])
def model_v3_input():
    data = request.get_json()
    user_input = data["input"]

    result_v1 = model.run_model_v1(user_input)
    result_v2 = model.run_model_v2(user_input)
    result_v3 = model.run_model_v3(user_input)

    return jsonify({
        'result_v1': result_v1,
        'result_v2': result_v2,
        'result_v3': result_v3
    }), 200

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, port=5000)