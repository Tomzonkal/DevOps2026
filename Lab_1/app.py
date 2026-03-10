
# W tej sekcji dodajemy nasz nowy model 
from flask import Flask, request, jsonify
from model_0000 import model as model_0000
from model_123456 import model as model_123456
from model_422385 import model as model_422385

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


@app.route('/api/model_422385', methods=['POST'])
def model_422385_input():
    # Pobieranie treści zapytania w naszym przypadku array[4]
    data = request.get_json()
    input=data["input"]
    #Wykonywanie predykcji
    result=model_422385.run_model_422385(input=input)
    return jsonify({'result': result}), 200

#######################################################################

@app.route('/api/model_123456', methods=['POST'])
def model_123456_input():
    # Pobieranie treści zapytania w naszym przypadku array[4]
    data = request.get_json()
    input=data["input"]
    #Wykonywanie predykcji
    result=model_123456.run_model_123456(input=input)
    return jsonify({'result': result}), 200

#######################################################################

def run_model_422385(input):
    #Wczytywanie modelu z pliku
    path= os.path.dirname(__file__)
    
    with open(path+"/model.pkl","rb")as f:
        model= pickle.load(f)
    #Wykonywanie predykcji    
    result=model.predict(input)
    result=float(result[0])
    return result




if __name__ == '__main__':
    app.run(host="0.0.0.0",debug=True,port=5000)

