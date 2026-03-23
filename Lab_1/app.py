
# W tej sekcji dodajemy nasz nowy model 
from flask import Flask, request, jsonify
from model_0000 import model as model_0000
#from model_123456 import model as model_123456
from model_421307 import model as model_421307


###########################################


app = Flask(__name__)

##### Ta funkcja powinna być skopiowana do utowrzenia nowego endpointa####################3
@app.route('/api/model_0000', methods=['POST'])
def model_00000_input():
    # Pobieranie treści zapytania w naszym przypadku array[4]
    data = request.get_json()
    input=data["input"]
    #Wykonywanie predykcji
    result=model_0000.run_model_0000(input=input)
    return jsonify({'result': result}), 200


@app.route('/api/model_421307', methods=['POST'])
def model_421307_input():
    # Pobieranie treści zapytania w naszym przypadku array[4]
    data = request.get_json()
    input=data["input"]
    #Wykonywanie predykcji
    result=model_421307.run_model_421307(input=input)
    return jsonify({'result': result}), 200

#######################################################################





if __name__ == '__main__':
    app.run(host="0.0.0.0",debug=True,port=5000)

