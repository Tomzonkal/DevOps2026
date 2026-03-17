import pickle 
import os 

###### Pierwsze rozwiązanie ###########

def run_model_421068_v1(input):
    #Wczytywanie modelu z pliku
    path= os.path.dirname(__file__)
 
    with open(path+"/model.pkl","rb")as f:
        model= pickle.load(f)

####### Trzecie rozwiązanie ###########

def run_model_421068_v3(input):
    #Wczytywanie modelu z pliku
    path= os.path.dirname(__file__)
    
    f=open(path+"/model.pkl","rb")
    model= pickle.load(f)
    f.close()

    #Wykonywanie predykcji    
    result=model.predict(input)
    result=float(result[0])
    return result

import pickle
import os

###### Drugie rozwiązanie ###########

def run_model_421068_v2(input):
    #Wczytywanie modelu z pliku
    path= "./model_421068/model.pkl"
    with open(path,"rb")as f:
        model= pickle.load(f)
        result=model.predict(input)
        result=float(result[0])
    return result


