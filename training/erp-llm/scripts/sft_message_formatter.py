"""Assistant-only Qwen chat formatting for the private SFT stage."""

from __future__ import annotations


def encode_record(tokenizer, messages: list[dict[str, str]], max_length: int):
    """Return input ids and labels, masking all non-assistant token spans."""
    ids: list[int] = []
    labels: list[int] = []
    prefix: list[dict[str, str]] = []
    for message in messages:
        role, content = message["role"], message["content"]
        prefix.append({"role": role, "content": content})
        current = tokenizer.apply_chat_template(prefix, tokenize=True, add_generation_prompt=False)
        new = current[len(ids):]
        if not new:
            continue
        ids.extend(new)
        labels.extend(new if role == "assistant" else [-100] * len(new))
    if not any(value != -100 for value in labels):
        raise ValueError("record has no assistant tokens")
    return ids[:max_length], labels[:max_length]
