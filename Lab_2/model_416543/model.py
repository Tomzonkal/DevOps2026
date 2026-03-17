import pickle 
import os 
def run_model_v2(input):
    #Wczytywanie modelu z pliku
    path= "./model_0000/model.pkl"
    with open(path,"rb")as f:
        model= pickle.load(f)    
        result=model.predict(input)
        result=float(result[0])
    return result
