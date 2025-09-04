from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


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
def classification_model(prompt:str):
    ##TODO
    # from the DL classification find prediction
    return {'prediction': 'whatever the classification model found'}

# Intervention
@app.get('/predict_theme') # expects one query -> prompt from user
def clustering_model(prompt:str):
    #TODO
    #outcome from DL clustering model

    #intervention
    return {'intervention': 'give proper intervention'}
