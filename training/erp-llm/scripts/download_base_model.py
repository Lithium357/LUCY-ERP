"""Download the selected base model into the D: project volume for reproducible training."""

from pathlib import Path

from huggingface_hub import snapshot_download

MODEL_ID = "Qwen/Qwen3-4B-Base"
DESTINATION = Path(r"D:\ERP-LLM\models\Qwen3-4B-Base")

if __name__ == "__main__":
    print(f"Downloading {MODEL_ID} to {DESTINATION}", flush=True)
    snapshot_download(repo_id=MODEL_ID, local_dir=DESTINATION)
