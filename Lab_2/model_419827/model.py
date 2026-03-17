import pickle 
import os 

###### Drugie rozwiązanie ###########

def run_model_419827_v2(input):
    #Wczytywanie modelu z pliku
    path= "./model_419827/model.pkl"
    with open(path,"rb")as f:
        model= pickle.load(f)    
        result=model.predict(input)
        result=float(result[0])
    return result

