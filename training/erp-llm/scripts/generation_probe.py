#!/usr/bin/env python3
"""CPU-only adapter generation probe with repeat-token diagnostics.

Supply prompts locally at execution time. This tool intentionally stores no
prompts or completions in the repository.
"""

from __future__ import annotations

import argparse
import json
import random
from pathlib import Path


def longest_equal_run(values: list[int]) -> int:
    best = current = 0
    previous: int | None = None
    for value in values:
        current = current + 1 if value == previous else 1
        best = max(best, current)
        previous = value
    return best


def longest_character_run(text: str) -> int:
    best = current = 0
    previous: str | None = None
    for character in text:
        current = current + 1 if character == previous else 1
        best = max(best, current)
        previous = character
    return best


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", required=True, type=Path)
    parser.add_argument("--adapter", type=Path, help="Optional PEFT adapter directory")
    parser.add_argument("--prompt", required=True, help="One private, local prompt")
    parser.add_argument("--max-new-tokens", type=int, default=160)
    parser.add_argument("--temperature", type=float, default=0.7)
    parser.add_argument("--top-p", type=float, default=0.9)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--greedy", action="store_true", help="Disable sampling for a deterministic probe")
    parser.add_argument("--json-out", type=Path, help="Optional local diagnostic report; never commit it")
    args = parser.parse_args()

    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    random.seed(args.seed)
    torch.manual_seed(args.seed)
    tokenizer = AutoTokenizer.from_pretrained(args.model, local_files_only=True)
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token = tokenizer.eos_token
    model = AutoModelForCausalLM.from_pretrained(args.model, local_files_only=True, torch_dtype=torch.float32)
    if args.adapter:
        from peft import PeftModel
        model = PeftModel.from_pretrained(model, str(args.adapter))
    model.to("cpu").eval()
    inputs = tokenizer(args.prompt, return_tensors="pt")
    options = {
        "max_new_tokens": args.max_new_tokens,
        "do_sample": not args.greedy,
        "pad_token_id": tokenizer.pad_token_id,
        "eos_token_id": tokenizer.eos_token_id,
        "repetition_penalty": 1.08,
    }
    if not args.greedy:
        options.update({"temperature": args.temperature, "top_p": args.top_p})
    with torch.inference_mode():
        output = model.generate(**inputs, **options)
    token_ids = output[0, inputs["input_ids"].shape[1] :].tolist()
    completion = tokenizer.decode(token_ids, skip_special_tokens=True)
    report = {
        "schema_version": 1,
        "device": "cpu",
        "adapter": str(args.adapter) if args.adapter else None,
        "seed": args.seed,
        "generated_tokens": len(token_ids),
        "longest_equal_token_run": longest_equal_run(token_ids),
        "longest_equal_character_run": longest_character_run(completion),
        "possible_repetition_loop": longest_equal_run(token_ids) >= 12 or longest_character_run(completion) >= 32,
        "eos_token_id": tokenizer.eos_token_id,
        "completion": completion,
    }
    rendered = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(rendered, encoding="utf-8")
    print(rendered, end="")


if __name__ == "__main__":
    main()
