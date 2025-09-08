## all functions related to load / save model

import os # to get the env variables
from sklearn.pipeline import Pipeline
import pickle
from transformers import AutoModelForSequenceClassification, AutoTokenizer
from sentence_transformers import SentenceTransformer

def load_model(model_name="Production") -> Pipeline:
    """
    Return a saved model:
    - locally (given by MODEL_NAME environment variable)

    Return None (but do not Raise) if no model is found

    """
    # print(model_name)
    # return
    path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))),'models')
    # local_model_paths
    print(f"\nLoad model from local registry...\n{path}\n")
    print(f"Model name : {model_name}")
    file = os.path.join(path,model_name)

    print(file)
    if not os.path.isfile(file):
        print(f"\n❌ No model found in {path} with the name {model_name}")
        return None

    with open(file,'rb') as f:
        model = pickle.load(f)

    print("✅ Model loaded from local disk")
    return model


def load_dl_model(model_path="models/dlbert"):
    '''Load the DLBERT model from a given path
    '''
    if not os.path.isdir(model_path):
        print(f"\n❌ No DLBERT model found in {model_path}")
        return None
    model = AutoModelForSequenceClassification.from_pretrained(model_path)
    print("✅ DLBERT Model loaded from local disk")
    return model


def load_dl_tokenizer(tokenizer_path="models/dlbert"):
    '''
    Load the tokenizer from a given path
    '''
    if not os.path.isdir(tokenizer_path):
        print(f"\n❌ No DLBERT model found in {tokenizer_path}")
        return None
    tokenizer = AutoTokenizer.from_pretrained(tokenizer_path)
    print("✅ DLBERT Tokenizer loaded from local disk")
    return tokenizer


def load_sbert_model(model_path="models/sbert") -> SentenceTransformer:
    """
    Load a SBERT model from a given path
    """
    if not os.path.isdir(model_path):
        print(f"\n❌ No SBERT model found in {model_path}")
        return None
    model = SentenceTransformer(model_path)
    print("✅ SBERT Model loaded from local disk")
    return model
