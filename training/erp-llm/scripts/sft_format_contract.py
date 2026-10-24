"""Reference contract for SFT message rendering and loss masking.

The private trainer implementation must produce equivalent labels: only
assistant-message token spans are trainable; all prior system/user text is
masked with -100.
"""

from __future__ import annotations


def assistant_masked_labels(token_ids: list[int], assistant_spans: list[tuple[int, int]]) -> list[int]:
    labels = [-100] * len(token_ids)
    for start, end in assistant_spans:
        if not 0 <= start <= end <= len(token_ids):
            raise ValueError("assistant span is outside rendered token sequence")
        labels[start:end] = token_ids[start:end]
    if not any(label != -100 for label in labels):
        raise ValueError("rendered record contains no assistant training tokens")
    return labels
