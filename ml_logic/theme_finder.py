
from transformers import pipeline
import json
from typing import List, Tuple

class ThemeFinder:
    def __init__(self, labels_path: str = "configs/theme_labels.json",
                    model_name: str = "facebook/bart-large-mnli",
                    device: int = -1):
            # Load canonical labels
            with open(labels_path, "r") as f:
                self.labels: List[str] = json.load(f)
            # Load HF pipeline once (CPU by default; set device=0 for GPU)
            self.pipe = pipeline("zero-shot-classification", model=model_name, device=device)

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
