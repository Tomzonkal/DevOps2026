import os 
import pickle 

def run_model_v1(input):
    path = os.path.dirname(__file__)
    with open(path + "/model.pkl", "rb") as f:
        model = pickle.load(f)  
    result = model.predict(input)
    result = float(result[0])
    return result


def run_model_v2(input):
    path = "./model_0000/model.pkl"
    with open(path, "rb") as f:
        model = pickle.load(f)    
        result = model.predict(input)
        result = float(result[0])
    return result


def run_model_v3(input):
    path = os.path.dirname(__file__)
    f = open(path + "/model.pkl", "rb")
    model = pickle.load(f)
    f.close()  
    result = model.predict(input)
    result = float(result[0])
    return result
