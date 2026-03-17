from flask import Flask, request, jsonify
from model_0000 import model
from model_422377 import model as model_422377

app = Flask(__name__)

@app.route('/api/model_422377', methods=['POST'])
def model_422377_input():
    data = request.get_json()
    input = data["input"]
    result = model_422377.run_model_v3(input)
    return jsonify({'result': result}), 200

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, port=5000)
