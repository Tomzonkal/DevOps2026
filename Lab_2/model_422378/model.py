import pickle 
import os 

def run_model_v3(input):
    path= os.path.dirname(__file__)
    f=open(path+"/model.pkl","rb")
    model= pickle.load(f)
    f.close()
    result=model.predict(input)
    result=float(result[0])
    return result