"""Heuristic content audit for private Astra SFT candidates.

This complements the schema audit: it flags near-duplicate assistant replies,
unwanted role leakage, and training rows that narrate the user's inner state.
It never rewrites data; review remains a human decision.
"""

from __future__ import annotations

import argparse
import json
import re
from itertools import combinations
from pathlib import Path


WORD = re.compile(r"[a-z']+")
LEAKS = ("as an ai", "i am an assistant", "language model", "system prompt")
INNER = ("you felt", "you thought", "you realized", "your mind")


def tokens(text: str) -> set[str]:
    return set(WORD.findall(text.lower()))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", required=True, type=Path)
    parser.add_argument("--near-duplicate", type=float, default=0.72)
    args = parser.parse_args()
    rows = [json.loads(line) for line in args.data.read_text(encoding="utf-8").splitlines() if line]
    replies = [(row["id"], next(m["content"] for m in reversed(row["messages"]) if m["role"] == "assistant")) for row in rows]
    pairs = []
    for (left_id, left), (right_id, right) in combinations(replies, 2):
        a, b = tokens(left), tokens(right)
        similarity = len(a & b) / len(a | b) if a | b else 0.0
        if similarity >= args.near_duplicate:
            pairs.append({"left": left_id, "right": right_id, "jaccard": round(similarity, 3)})
    flags = []
    for record_id, reply in replies:
        low = reply.lower()
        for phrase in LEAKS:
            if phrase in low:
                flags.append({"id": record_id, "kind": "role_leak", "phrase": phrase})
        for phrase in INNER:
            if phrase in low:
                flags.append({"id": record_id, "kind": "user_interior", "phrase": phrase})
    print(json.dumps({"records": len(rows), "near_duplicate_pairs": pairs[:100], "near_duplicate_count": len(pairs), "flags": flags}, indent=2))


if __name__ == "__main__":
    main()
