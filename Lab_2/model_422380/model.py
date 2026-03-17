import pickle
import os

def run_model_422380_v1(input):
    path= os.path.dirname(__file__)
    with open(path+"/model.pkl","rb")as f:
        model= pickle.load(f)
    result=model.predict(input)
    result=float(result[0])
    return result

def run_model_422380_v2(input):
    path= os.path.dirname(__file__)
    with open(path+"/model.pkl","rb")as f:
        model= pickle.load(f)
    result=model.predict(input)
    result=float(result[0])
    return result

def run_model_422380_v3(input):
    path= os.path.dirname(__file__)
    with open(path+"/model.pkl","rb")as f:
        model= pickle.load(f)
    result=model.predict(input)
    result=float(result[0])
    return result
