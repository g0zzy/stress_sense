
import os
from transformers import pipeline
import json
from typing import List, Tuple

class ThemeFinder:
    def __init__(self, labels_path: str = "stress_sense/configs/theme_labels.json",
                    model_name = os.environ.get('CLUSTERING_MODEL_NAME'), #"facebook/bart-large-mnli",
                    device: int = -1):
            # Load canonical labels
            with open(labels_path, "r") as f:
                self.labels: List[str] = json.load(f)
            # Load HF pipeline once (CPU by default; set device=0 for GPU)

            path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))),'models')
            model_path = os.path.join(path, "clustering-valhalla-distilbart-mnli-12-1")
            self.pipe = pipeline("zero-shot-classification", model=model_path, device=device)#, local_files_only=True, cache_dir="./models")

    def find_theme(self, text: str, multi_label: bool = False, threshold: float = 0.35) -> List[Tuple[str, float]]:
        res = self.pipe(text, candidate_labels=self.labels, multi_label=multi_label)
        labels = res["labels"]
        scores = res["scores"]
        if multi_label:
            picked = [(l, s) for l, s in zip(labels, scores) if s >= threshold]
            # ensure deterministic order
            picked.sort(key=lambda x: x[1], reverse=True)
            return picked or [("general stress", 1.0)]
        else:
            return [(labels[0], scores[0])]
