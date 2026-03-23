import pickle 
import os 
<<<<<<< HEAD

###### Pierwsze rozwiązanie ###########

def run_model_v1(input):
    #Wczytywanie modelu z pliku
    path= os.path.dirname(__file__)
    
    with open(path+"/model.pkl","rb")as f:
        model= pickle.load(f)
    #Wykonywanie predykcji    
    result=model.predict(input)
    result=float(result[0])
    return result


###### Drugie rozwiązanie ###########

=======
>>>>>>> lab_2/new_branch_420067_v2
def run_model_v2(input):
    #Wczytywanie modelu z pliku
    path= "./model_0000/model.pkl"
    with open(path,"rb")as f:
        model= pickle.load(f)    
        result=model.predict(input)
        result=float(result[0])
<<<<<<< HEAD
    return result


####### Trzecie rozwiązanie ###########

def run_model_v3(input):
    #Wczytywanie modelu z pliku
    path= os.path.dirname(__file__)
    
    f=open(path+"/model.pkl","rb")
    model= pickle.load(f)
    f.close()
    #Wykonywanie predykcji    
    result=model.predict(input)
    result=float(result[0])
=======
>>>>>>> lab_2/new_branch_420067_v2
    return result