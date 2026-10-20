#!/usr/bin/env python3
"""Report structural quality metrics for a private ShareGPT-style SFT JSONL.

The report deliberately contains no training text, hashes, or identifiers from
the records, so it can be used to decide whether a seed set needs expansion.
"""

from __future__ import annotations

import argparse
import collections
import hashlib
import json
from pathlib import Path


def fingerprint(value: object) -> str:
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", required=True, type=Path)
    parser.add_argument("--out", type=Path, help="Optional local JSON report")
    args = parser.parse_args()
    rows = []
    malformed = 0
    for line in args.data.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError:
            malformed += 1
            continue
        if not isinstance(value, dict) or not isinstance(value.get("messages"), list):
            malformed += 1
            continue
        rows.append(value)

    pairs: list[str] = []
    replies: list[str] = []
    role_errors = 0
    turn_counts: list[int] = []
    bucket_counts: collections.Counter[str] = collections.Counter()
    for row in rows:
        messages = row["messages"]
        turn_counts.append(len(messages))
        bucket_counts[str(row.get("bucket", "unspecified"))] += 1
        if len(messages) < 2 or any(not isinstance(message, dict) or not isinstance(message.get("role"), str) or not isinstance(message.get("content"), str) for message in messages):
            role_errors += 1
            continue
        if messages[-1]["role"] != "assistant":
            role_errors += 1
            continue
        user = next((message["content"] for message in reversed(messages[:-1]) if message["role"] == "user"), None)
        if user is None:
            role_errors += 1
            continue
        pairs.append(fingerprint({"user": user, "assistant": messages[-1]["content"]}))
        replies.append(fingerprint(messages[-1]["content"]))

    report = {
        "schema_version": 1,
        "records": len(rows),
        "malformed_records": malformed,
        "role_or_shape_errors": role_errors,
        "buckets": dict(sorted(bucket_counts.items())),
        "unique_final_user_assistant_pairs": len(set(pairs)),
        "unique_final_assistant_replies": len(set(replies)),
        "duplicate_final_pairs": len(pairs) - len(set(pairs)),
        "duplicate_final_assistant_replies": len(replies) - len(set(replies)),
        "min_message_count": min(turn_counts, default=0),
        "max_message_count": max(turn_counts, default=0),
        "recommendation": "Expand with genuinely new multi-turn records before SFT when duplicate final replies are common; changing only a wrapper around the same answer is not useful diversity.",
    }
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(rendered, encoding="utf-8")
    print(rendered, end="")


if __name__ == "__main__":
    main()
