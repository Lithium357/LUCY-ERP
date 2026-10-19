"""Download the selected base model to an explicit local directory."""

import argparse
from pathlib import Path

from huggingface_hub import snapshot_download

DEFAULT_MODEL_ID = "Qwen/Qwen3-4B-Base"

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--destination", type=Path, required=True, help="Local model directory; do not commit it.")
    parser.add_argument("--model-id", default=DEFAULT_MODEL_ID)
    args = parser.parse_args()
    print(f"Downloading {args.model_id} to {args.destination}", flush=True)
    snapshot_download(repo_id=args.model_id, local_dir=args.destination)
