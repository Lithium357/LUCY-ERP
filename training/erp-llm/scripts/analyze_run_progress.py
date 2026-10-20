#!/usr/bin/env python3
"""Summarize a local CPT progress CSV without reading model data or outputs."""

from __future__ import annotations

import argparse
import csv
import json
import statistics
from pathlib import Path
from typing import Iterable


def number(row: dict[str, str], field: str) -> float | None:
    value = (row.get(field) or "").strip()
    try:
        return float(value) if value else None
    except ValueError:
        return None


def linear_slope(points: Iterable[tuple[float, float]]) -> float | None:
    values = list(points)
    if len(values) < 2:
        return None
    xs, ys = zip(*values)
    denominator = len(values) * sum(x * x for x in xs) - sum(xs) ** 2
    if denominator == 0:
        return None
    return (len(values) * sum(x * y for x, y in values) - sum(xs) * sum(ys)) / denominator


def mean(values: Iterable[float]) -> float | None:
    values = list(values)
    return statistics.fmean(values) if values else None


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--csv", required=True, type=Path, help="Run-local progress/train.csv")
    parser.add_argument("--window", type=int, default=500, help="Recent training-row window")
    parser.add_argument("--expected-eval-every", type=int, default=500)
    parser.add_argument("--out", type=Path, help="Optional local JSON report path")
    args = parser.parse_args()

    with args.csv.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise SystemExit(f"No progress rows found: {args.csv}")

    last = rows[-1]
    recent = rows[-args.window :]
    train_points = [(number(row, "step"), number(row, "train_loss")) for row in recent]
    train_points = [(step, loss) for step, loss in train_points if step is not None and loss is not None]
    validations = [(number(row, "step"), number(row, "eval_loss")) for row in rows]
    validations = [(step, loss) for step, loss in validations if step is not None and loss is not None]
    validation_window = validations[-min(10, len(validations)) :]
    last_step = int(number(last, "step") or 0)
    total_steps = int(number(last, "total_steps") or 0)
    latest_eval_step = int(validations[-1][0]) if validations else None
    warnings: list[str] = []
    if not validations:
        warnings.append("No validation rows have been written yet.")
    elif last_step - latest_eval_step > args.expected_eval_every:
        warnings.append("Validation is older than one expected evaluation interval.")
    if len(validations) < 3:
        warnings.append("Too few validation observations to judge a trend.")

    report = {
        "schema_version": 1,
        "source": str(args.csv),
        "rows": len(rows),
        "latest": {
            "step": last_step,
            "total_steps": total_steps,
            "progress_percent": number(last, "progress_percent"),
            "session_id": last.get("session_id"),
            "resumed_from_step": int(number(last, "resumed_from_step") or 0),
            "train_loss": number(last, "train_loss"),
            "eval_loss": number(last, "eval_loss"),
            "seconds_per_step": number(last, "seconds_per_step"),
            "tokens_per_second": number(last, "tokens_per_second"),
        },
        "train": {
            "window_rows": len(train_points),
            "window_mean": mean(loss for _, loss in train_points),
            "window_slope_per_1000_steps": (
                linear_slope(train_points) * 1000 if linear_slope(train_points) is not None else None
            ),
        },
        "validation": {
            "observations": len(validations),
            "latest_step": latest_eval_step,
            "latest_loss": validations[-1][1] if validations else None,
            "last_ten_mean": mean(loss for _, loss in validation_window),
            "best_loss": min((loss for _, loss in validations), default=None),
            "best_step": (min(validations, key=lambda item: item[1])[0] if validations else None),
            "last_ten_slope_per_1000_steps": (
                linear_slope(validation_window) * 1000 if linear_slope(validation_window) is not None else None
            ),
        },
        "interpretation": {
            "train_vs_validation": "Training loss is sampled while weights update; validation loss is sparse and measured in eval mode. Matching values are neither expected nor required.",
            "warnings": warnings,
        },
    }
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(rendered, encoding="utf-8")
    print(rendered, end="")


if __name__ == "__main__":
    main()
