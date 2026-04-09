import os
import pickle


def run_model_401967(input):
    path = os.path.dirname(__file__)
    with open(path + "/model.pkl", "rb") as f:
        model = pickle.load(f)
    result = model.predict(input)
    result = float(result[0])
    return result
