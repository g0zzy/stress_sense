from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from ml_logic import theme_finder

app = FastAPI()

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
    ##TODO
    # from the DL classification find prediction
    return {'prediction': 'whatever the classification model found'}

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
