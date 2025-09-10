from transformers import pipeline

pipe = pipeline("zero-shot-classification", model=os.environ.get('CLUSTERING_MODEL_NAME'), device=-1)
pipe.save_pretrained("./models/clustering-valhalla-distilbart-mnli-12-1")