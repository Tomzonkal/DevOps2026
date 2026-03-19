import pickle 
import os 

###### Pierwsze rozwiązanie ###########

def run_model_419845(input):
    #Wczytywanie modelu z pliku
    path= os.path.dirname(__file__)
    
    f=open(path+"/model.pkl","rb")
    model= pickle.load(f)
    f.close()
    #Wykonywanie predykcji    
    result=model.predict(input)
    result=float(result[0])
    return result
