import pickle 
import os 

###### Pierwsze rozwiązanie ###########

def run_model_419845(input):
    #Wczytywanie modelu z pliku
<<<<<<< HEAD
    path= os.path.dirname(__file__)
    
    with open(path+"/model.pkl","rb")as f:
        model= pickle.load(f)
    #Wykonywanie predykcji    
    result=model.predict(input)
    result=float(result[0])
    return result


=======
    path= "./model_419845/model.pkl"
    with open(path,"rb")as f:
        model= pickle.load(f)    
        result=model.predict(input)
        result=float(result[0])
    return result
>>>>>>> lab_2/new_branch_419845_v2
