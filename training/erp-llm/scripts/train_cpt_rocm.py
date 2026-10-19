"""Streaming LoRA continued-pretraining for the raw ERP archive on AMD ROCm.

The loader normalizes HTML into text only.  It intentionally applies no
content filtering, sampling, quality scoring, or source exclusions.
"""

from __future__ import annotations

import argparse
import csv
import glob
import html
import random
import re
from pathlib import Path

import torch
from peft import LoraConfig, get_peft_model
from torch.utils.data import IterableDataset
from transformers import AutoModelForCausalLM, AutoTokenizer, Trainer, TrainingArguments


TAG_RE = re.compile(r"<[^>]+>")
SPACE_RE = re.compile(r"\s+")


def normalize_html(raw: str) -> str:
    """Lossless-for-content presentation normalization, not a quality filter."""
    text = html.unescape(raw)
    text = re.sub(r"(?i)<br\s*/?>", "\n", text)
    text = re.sub(r"(?i)</p\s*>", "\n\n", text)
    text = TAG_RE.sub("", text)
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    return "\n".join(SPACE_RE.sub(" ", line).strip() for line in text.split("\n")).strip()


class RawArchiveDataset(IterableDataset):
    def __init__(self, archive_dir: Path, tokenizer, sequence_length: int, seed: int) -> None:
        self.paths = sorted(glob.glob(str(archive_dir / "*.csv")))
        self.tokenizer = tokenizer
        self.sequence_length = sequence_length
        self.seed = seed

    def __iter__(self):
        paths = self.paths.copy()
        random.Random(self.seed).shuffle(paths)
        token_buffer: list[int] = []
        eos = self.tokenizer.eos_token_id
        for csv_path in paths:
            with open(csv_path, "r", encoding="utf-8", errors="replace", newline="") as stream:
                for row in csv.DictReader(stream):
                    body = normalize_html(row.get("message", ""))
                    if not body:
                        continue
                    token_buffer.extend(self.tokenizer(body, add_special_tokens=False)["input_ids"])
                    token_buffer.append(eos)
                    while len(token_buffer) >= self.sequence_length:
                        chunk, token_buffer = token_buffer[: self.sequence_length], token_buffer[self.sequence_length :]
                        yield {
                            "input_ids": torch.tensor(chunk, dtype=torch.long),
                            "attention_mask": torch.ones(self.sequence_length, dtype=torch.long),
                            "labels": torch.tensor(chunk, dtype=torch.long),
                        }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=Path, default=Path("/mnt/d/ERP-LLM/models/Qwen3-4B-Base"))
    parser.add_argument("--archive", type=Path, default=Path("/mnt/d/ERP-LLM/data/raw/sdsr--erp-and-erotica"))
    parser.add_argument("--output", type=Path, default=Path("/mnt/d/ERP-LLM/adapters/cpt-smoke"))
    parser.add_argument("--max-steps", type=int, default=25)
    parser.add_argument("--sequence-length", type=int, default=512)
    parser.add_argument("--gradient-accumulation", type=int, default=16)
    parser.add_argument("--save-steps", type=int, default=500)
    args = parser.parse_args()

    tokenizer = AutoTokenizer.from_pretrained(args.model, local_files_only=True)
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token = tokenizer.eos_token
    model = AutoModelForCausalLM.from_pretrained(
        args.model,
        local_files_only=True,
        torch_dtype=torch.bfloat16,
        attn_implementation="sdpa",
    )
    model.config.use_cache = False
    # Required when the base is frozen and activation checkpointing is enabled:
    # it gives LoRA's downstream trainable modules a differentiable input path.
    model.enable_input_require_grads()
    model = get_peft_model(
        model,
        LoraConfig(
            r=16,
            lora_alpha=32,
            lora_dropout=0.05,
            bias="none",
            task_type="CAUSAL_LM",
            target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
        ),
    )
    model.print_trainable_parameters()
    dataset = RawArchiveDataset(args.archive, tokenizer, args.sequence_length, seed=42)
    training_args = TrainingArguments(
        output_dir=str(args.output),
        max_steps=args.max_steps,
        per_device_train_batch_size=1,
        gradient_accumulation_steps=args.gradient_accumulation,
        gradient_checkpointing=True,
        gradient_checkpointing_kwargs={"use_reentrant": False},
        learning_rate=1e-4,
        warmup_ratio=0.05,
        lr_scheduler_type="cosine",
        optim="adamw_torch",
        bf16=True,
        fp16=False,
        logging_steps=1,
        save_strategy="steps",
        save_steps=args.save_steps,
        save_total_limit=1,
        report_to="none",
        remove_unused_columns=False,
        dataloader_num_workers=0,
        seed=42,
    )
    Trainer(model=model, args=training_args, train_dataset=dataset).train()
    model.save_pretrained(args.output / "final")
    tokenizer.save_pretrained(args.output / "final")


if __name__ == "__main__":
    main()
