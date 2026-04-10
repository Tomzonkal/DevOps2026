import os
import pickle


def run_model_v2(input):
    path = "./model_422378/model.pkl"
    with open(path, "rb") as f:
        model = pickle.load(f)
        result = model.predict(input)
        result = float(result[0])
    return result
