
# W tej sekcji dodajemy nasz nowy model 
from flask import Flask, request, jsonify
from model_0000 import model as model_0000
from model_401967 import model as model_401967


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

#######################################################################

@app.route('/api/model_401967', methods=['POST'])
def model_401967_input():
    # Pobieranie treści zapytania w naszym przypadku array[4]
    data = request.get_json()
    input=data["input"]
    #Wykonywanie predykcji
    result=model_401967.run_model_401967(input=input)
    return jsonify({'result': result}), 200




if __name__ == '__main__':
    app.run(host="0.0.0.0",debug=True,port=5000)

