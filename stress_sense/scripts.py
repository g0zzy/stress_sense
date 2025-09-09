import os
# from huggingface_hub import snapshot_download

# snapshot_download(repo_id=os.environ.get('CLUSTERING_MODEL_NAME'), repo_type="model", cache_dir="./models")

from transformers import pipeline

pipe = pipeline("zero-shot-classification", model=os.environ.get('CLUSTERING_MODEL_NAME'), device=-1)
pipe.save_pretrained("./models/clustering-valhalla-distilbart-mnli-12-1")
