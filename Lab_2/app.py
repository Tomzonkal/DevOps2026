from flask import Flask, request, jsonify
#from model_0000 import model
from model_422375 import model

app = Flask(name)

@app.route('/api/model_422375', methods=['POST'])
def model_422374_input():
    data = request.get_json()
    input = data["input"]

    result_v1 = model.run_model_v1(input)
    result_v2 = model.run_model_v2(input)

    return jsonify({
        'result_v1': result_v1,
        'result_v2': result_v2
    }), 200

if name == 'main':
    app.run(host="0.0.0.0", debug=True, port=5000)
