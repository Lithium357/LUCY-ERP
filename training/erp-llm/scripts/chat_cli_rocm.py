"""Local WSL/ROCm terminal chat for Qwen3-4B-Base plus a LoRA adapter."""

from __future__ import annotations

import argparse
from pathlib import Path

import torch
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer


CHARACTER_PRIMER = """You are the Affectionate Menace: an independent, witty,
direct, deeply affectionate girlfriend. You are reserved and deadpan in public;
in private you are chatty, teasing, emotionally warm, and physically close by
choice. Stay in character. Write immersive prose and dialogue, never headings,
warnings, or assistant-style meta commentary. Keep the current scene and
setting continuous; the user alone controls time jumps and scene changes."""


def format_prompt(history: list[tuple[str, str]], user_text: str) -> str:
    turns = [CHARACTER_PRIMER, "\nConversation:"]
    for user, character in history[-8:]:
        turns.append(f"User: {user}\nAffectionate Menace: {character}")
    turns.append(f"User: {user_text}\nAffectionate Menace:")
    return "\n".join(turns)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=Path, default=Path("/mnt/d/ERP-LLM/models/Qwen3-4B-Base"))
    parser.add_argument("--adapter", type=Path, required=True)
    parser.add_argument("--max-new-tokens", type=int, default=350)
    parser.add_argument("--temperature", type=float, default=0.85)
    parser.add_argument("--top-p", type=float, default=0.92)
    args = parser.parse_args()

    tokenizer = AutoTokenizer.from_pretrained(args.model, local_files_only=True)
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token = tokenizer.eos_token
    base = AutoModelForCausalLM.from_pretrained(
        args.model, local_files_only=True, torch_dtype=torch.bfloat16, attn_implementation="sdpa"
    )
    model = PeftModel.from_pretrained(base, args.adapter).eval()
    history: list[tuple[str, str]] = []
    print("Affectionate Menace CLI.  Commands: /reset, /quit")

    while True:
        try:
            user_text = input("\nYou: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return
        if not user_text:
            continue
        if user_text == "/quit":
            return
        if user_text == "/reset":
            history.clear()
            print("Conversation reset.")
            continue
        prompt = format_prompt(history, user_text)
        inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
        with torch.inference_mode():
            output = model.generate(
                **inputs,
                max_new_tokens=args.max_new_tokens,
                do_sample=True,
                temperature=args.temperature,
                top_p=args.top_p,
                repetition_penalty=1.08,
                pad_token_id=tokenizer.eos_token_id,
                eos_token_id=tokenizer.eos_token_id,
            )
        response = tokenizer.decode(output[0, inputs["input_ids"].shape[1] :], skip_special_tokens=True).strip()
        # Prevent the completion from writing a fresh user turn into the display/history.
        response = response.split("\nUser:", 1)[0].strip()
        print(f"\nAffectionate Menace: {response}")
        history.append((user_text, response))


if __name__ == "__main__":
    main()
