from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from ml_logic import theme_finder

from stress_sense.registry import load_model
from stress_sense.preprocessor import cleaning
import os


app = FastAPI()
app.state.model = load_model(os.environ.get('MODEL_NAME'))

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
    'load a model from local disk or gcp and return the model prediction on the prompt'
    #model = load_model(os.environ.get('MODEL_NAME'))

    if app.state.model is None: #if model is None:
        # TODO
        #what to do here?
        return {'prediction': 'model not found'}

    #Preprocessing
    # TODO : I do not know if that step is necessary when using transformer as classifier. I have that for my ML model
    prompt = cleaning(prompt)

    #Prediction
    # prediction = model.predict([prompt])
    prediction = app.state.model.predict([prompt])
    # prob = model.predict_proba([prompt])
    prob = app.state.model.predict_proba([prompt])


    return {'prediction': prediction[0],  # a string
            'probability': f"{prob[0][0]*100:.2f}"}

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
