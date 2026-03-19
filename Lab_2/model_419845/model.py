import pickle 
import os 

###### Pierwsze rozwiązanie ###########

def run_model_419845(input):
    #Wczytywanie modelu z pliku
    path= "./model_419845/model.pkl"
    with open(path,"rb")as f:
        model= pickle.load(f)    
        result=model.predict(input)
        result=float(result[0])
    return result