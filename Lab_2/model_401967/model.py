import pickle 
import os 

def run_model_v2(input):
    path= "./model_401967/model.pkl"
    with open(path,"rb")as f:
        model= pickle.load(f)    
        result=model.predict(input)
        result=float(result[0])
    return result
