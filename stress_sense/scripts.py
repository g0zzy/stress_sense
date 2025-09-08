from huggingface_hub import snapshot_download

print(snapshot_download(repo_id="facebook/bart-large-mnli", repo_type="model", cache_dir="./models"))
