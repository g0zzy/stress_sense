from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from stress_sense.ml_logic import theme_finder

from stress_sense.ml_logic import registry
from stress_sense.ml_logic import preprocessor
import os
import torch

app = FastAPI()

#app.state.model = registry.load_model(os.environ.get('MODEL_NAME'))
#app.state.sbert_model = registry.load_sbert_model("models/sbert")

##Load the dlbert model and the registry
app.state.dlbert_model = registry.load_dl_model("models/dlbertfinal")
app.state.dlbert_tokenizer = registry.load_dl_tokenizer("models/dlbertfinal")

# Load the theme finder instance
app.state.theme_finder_instance = theme_finder.ThemeFinder()

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


def get_prediction(text, model, tokenizer, device):
    inputs = tokenizer(text, return_tensors='pt', truncation=True, padding=True)
    inputs = {k: v.to(device) for k, v in inputs.items()}
    outputs = model(**inputs)
    _, predicted = torch.max(outputs.logits, dim=1)
    predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)
    print(f"probabilities: \n\t{predictions}")
    print(f"id2label: \n\t{model.config.id2label}")
    print(f"predictions:")
    for _id, label in model.config.id2label.items():
        print(f"\t{label:<7}:\t{round(float(predictions[0][_id]), 3)}")
    return predicted.item(), predictions




@app.get('/predict_stress_dl') # expects one query -> prompt from user
def predict_stress_dl(prompt:str):

    if (app.state.dlbert_model) is None:
        return {'prediction': 'model not found'}

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    app.state.dlbert_model.to(device)
    class_labels = {
    0: 'Anxiety',
    1: 'Normal',
    2: 'Stress',
    }

    predicted_class, predictions = get_prediction(prompt, app.state.dlbert_model, app.state.dlbert_tokenizer, device)
    print(f'Text: {prompt}')
    print(f'Predicted Class: {class_labels[predicted_class]}')
    predictions_list = predictions.tolist()
    max_index = predictions_list[0].index(max(predictions_list[0]))
    predicted_probability = predictions_list[0][max_index]
    print(f'Predicted Probability: {predicted_probability}')
    print('---')

    confidence = {}
    for _id, label in app.state.dlbert_model.config.id2label.items():
        label_number = label.lower()[-1]
        label_class = class_labels.get(int(label_number))
        confidence[label_class] = round(float(predictions[0][_id]), 3)

    sorted_classes_probabilities = dict(sorted(confidence.items(), key=lambda item: item[1], reverse=True))
    print(sorted_classes_probabilities)

    return {'prediction': class_labels[predicted_class], 'confidence': sorted_classes_probabilities}


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
def predict_theme(prompt:str, multi_label: bool = False):
    #outcome from DL clustering model
    themes = app.state.theme_finder_instance.find_theme(prompt, multi_label=multi_label)
    # (theme, confidence) = themes[0]

    return {'themes': themes}

if __name__ == '__main__':
    #just checking if environment variables can be accessed
    import os
    print(os.environ.get('MODEL_TARGET'))
    print(os.environ.get('GCP_PROJECT'))
    print(os.environ.get('GCP_REGION'))
    print(os.environ.get('BUCKET_NAME'))
    print(os.environ.get('GAR_IMAGE'))
