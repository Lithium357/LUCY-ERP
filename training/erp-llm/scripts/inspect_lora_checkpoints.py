#!/usr/bin/env python3
"""Verify complete LoRA inference and restart checkpoints for one local run."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


STEP = re.compile(r"^step-(\d+)$")
WEIGHTS = ("adapter/adapter_config.json", "adapter/adapter_model.safetensors", "metadata.json")
RESUME = WEIGHTS + ("optimizer.pt", "rng-state.pt", "trainer-state.json")


def step_from(path: Path) -> int | None:
    match = STEP.match(path.name)
    return int(match.group(1)) if match else None


def inspect(root: Path, required: tuple[str, ...]) -> list[dict[str, object]]:
    if not root.is_dir():
        return []
    result = []
    for path in sorted(root.iterdir(), key=lambda item: step_from(item) or -1):
        step = step_from(path)
        if step is None or not path.is_dir():
            continue
        missing = [item for item in required if not (path / item).is_file()]
        result.append({"step": step, "path": str(path), "complete": not missing, "missing": missing})
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--out", type=Path, help="Optional local JSON report")
    args = parser.parse_args()
    weights = inspect(args.run_dir / "checkpoints" / "weights", WEIGHTS)
    resume = inspect(args.run_dir / "checkpoints" / "resume", RESUME)
    complete_resume = [item for item in resume if item["complete"]]
    report = {
        "schema_version": 1,
        "run_dir": str(args.run_dir),
        "weights": weights,
        "resume": resume,
        "recommended_resume": complete_resume[-1] if complete_resume else None,
    }
    rendered = json.dumps(report, indent=2) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    if not complete_resume:
        raise SystemExit("No complete resume checkpoint found.")


if __name__ == "__main__":
    main()
