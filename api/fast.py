from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from stress_sense.ml_logic import theme_finder

from stress_sense.ml_logic import registry
from stress_sense.ml_logic import preprocessor
import os

app = FastAPI()

app.state.model = registry.load_model(os.environ.get('MODEL_NAME'))
app.state.sbert_model = registry.load_sbert_model("models/sbert")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# HOME
@app.get("/")
def root():
    return {'welcome':'Hello'}

# Prediction
@app.get('/predict_stress') # expects one query -> prompt from user
def predict_stress(prompt:str):

    if (app.state.model and app.state.sbert_model) is None:
        return {'prediction': 'model not found'}

    #Preprocessing
    prompt = preprocessor.strip_urls(prompt)

    prompt_embs = app.state.sbert_model.encode([prompt])
    print(prompt_embs)
    print(type(prompt_embs))

    #Prediction
    prediction = app.state.model.predict(prompt_embs)[0]
    prob = app.state.model.predict_proba(prompt_embs)[0].max()  # get the max probability

    return {'prediction': preprocessor.decode_label(prediction),  # a string
            'probability': float(prob.round(2))}

# Clustering
@app.get('/predict_theme') # expects one query -> prompt from user
def predict_theme(prompt:str):
    #outcome from DL clustering model
    theme_finder_instance = theme_finder.ThemeFinder()
    themes = theme_finder_instance.find_theme(prompt, multi_label=False)
    (theme, confidence) = themes[0]

    return {'theme': theme, 'confidence_level': confidence}

if __name__ == '__main__':
    #just checking if environment variables can be accessed
    import os
    print(os.environ.get('MODEL_TARGET'))
    print(os.environ.get('GCP_PROJECT'))
    print(os.environ.get('GCP_REGION'))
    print(os.environ.get('BUCKET_NAME'))
    print(os.environ.get('GAR_IMAGE'))
