from flask import Flask, request, jsonify
from model_0000 import model
from model_419845 import model as model_419845

app = Flask(__name__)

@app.route('/api/model_419845', methods=['POST'])
def model_419845_input():
    data = request.get_json()
    input = data["input"]
    result_v1 = model_419845.run_model_419845(input)
    return jsonify({'result': result_v1}), 200

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, port=5000)
