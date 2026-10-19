"""Download the approved Hugging Face dataset repositories without transforming them."""

from __future__ import annotations

import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

from huggingface_hub import HfApi, snapshot_download

ROOT = Path(r"D:\ERP-LLM")
RAW_ROOT = ROOT / "data" / "raw"
MANIFEST_PATH = ROOT / "data" / "collection-manifest.json"
MAX_BYTES = 512 * 1024**3

DATASETS = [
    "sdsr/erp-and-erotica",
    "PygmalionAI/PIPPA",
    "chimbiwide/RolePlay-NPCv2",
    "openerotica/erotica-analysis",
    "openerotica/mixed-rp",
    "devesh75/NSFW-Roleplay-Conversations",
    "athirdpath/DPO_Pairs-Roleplay-Llama3-NSFW",
    "backpropSukuna/wifu-chat-dataset",
    "RuneForgeAI/Viking_Witch_flirty_and_erotic_behavior",
    "lemonilia/LimaRP",
    "Gryphe/Sonnet3.5-Charcard-Roleplay",
]


def local_size(path: Path) -> int:
    return sum(file.stat().st_size for file in path.rglob("*") if file.is_file()) if path.exists() else 0


def remote_size(api: HfApi, repo_id: str) -> int | None:
    """Return the advertised repository size when Hugging Face supplies it."""
    info = api.repo_info(repo_id=repo_id, repo_type="dataset", files_metadata=True)
    sizes = [getattr(sibling, "size", None) for sibling in info.siblings]
    return sum(size for size in sizes if isinstance(size, int)) if all(isinstance(size, int) for size in sizes) else None


def main() -> None:
    RAW_ROOT.mkdir(parents=True, exist_ok=True)
    api = HfApi()
    current_size = local_size(RAW_ROOT)
    manifest: dict[str, object] = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "max_bytes": MAX_BYTES,
        "datasets": [],
    }

    for repo_id in DATASETS:
        destination = RAW_ROOT / repo_id.replace("/", "--")
        estimate = remote_size(api, repo_id)
        if estimate is not None and current_size + estimate > MAX_BYTES:
            print(f"STOP: {repo_id} would exceed the 512 GiB collection cap.", file=sys.stderr)
            break

        print(f"Collecting {repo_id} into {destination}", flush=True)
        snapshot_download(
            repo_id=repo_id,
            repo_type="dataset",
            local_dir=destination,
            resume_download=True,
        )
        collected = local_size(destination)
        current_size = local_size(RAW_ROOT)
        manifest["datasets"].append(
            {
                "repo_id": repo_id,
                "destination": str(destination),
                "advertised_bytes": estimate,
                "collected_bytes": collected,
            }
        )
        MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
        MANIFEST_PATH.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        print(f"Collected {collected / 1024**3:.2f} GiB; total {current_size / 1024**3:.2f} GiB", flush=True)


if __name__ == "__main__":
    main()
