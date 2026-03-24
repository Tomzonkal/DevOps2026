
# W tej sekcji dodajemy nasz nowy model 
from flask import Flask, request, jsonify

###########################################


app = Flask(__name__)

##### Ta funkcja powinna być skopiowana do utowrzenia nowego endpointa####################3
@app.route('/api/model_0000', methods=['POST'])
def model_00000_input():
    # Pobieranie treści zapytania w naszym przypadku array[4]
    data = request.get_json()
    input=data["input"]
    #Wykonywanie predykcji
    result=[]
    result.append(model_0000.run_model_v1(input=input))
    return jsonify({'result': result}), 200

#######################################################################





if __name__ == '__main__':
    app.run(host="0.0.0.0",debug=True,port=5000)

