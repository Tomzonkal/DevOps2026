import pickle 
import os 

###### Pierwsze rozwiązanie ###########

def run_model_421068_v1(input):
    #Wczytywanie modelu z pliku
    path= os.path.dirname(__file__)
 
    with open(path+"/model.pkl","rb")as f:
        model= pickle.load(f)
    #Wykonywanie predykcji    
    result=model.predict(input)
    result=float(result[0])
    return result
