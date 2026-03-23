import pickle 
import os 


def run_model_v1(input):

def run_model_v2(input):
 lab_2/new_branch_422367_v2
    #Wczytywanie modelu z pliku
    path= os.path.dirname(__file__)
    
    with open(path+"/model.pkl","rb")as f:
        model= pickle.load(f)
    #Wykonywanie predykcji    
    result=model.predict(input)
    result=float(result[0])
    return result
