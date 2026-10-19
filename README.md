# LUCY

Private local training, evaluation, and runtime work for Lucy: one persistent personal roleplay LLM.

## Scope

This repository contains only Lucy-specific language-model work and reproducible AMD/ROCm/WSL training notes. It deliberately excludes unrelated applications, dashboards, diffusion tooling, raw datasets, user conversations, model weights, checkpoints, generated outputs, credentials, and private source code from other projects.

## Contents

- `training/erp-llm/configs/` — 16 GB-class CPT and SFT configuration references.
- `training/erp-llm/scripts/` — dataset preparation, training, CPU chat, and diagnostic helpers.
- `training/erp-llm/alignment/` — Lucy-specific alignment material.
- `training/erp-llm/data/sft/` — small synthetic seed data for the final character fine-tune.
- `training/erp-llm/docs/` — ROCm and WSL observations from the RX 7800 XT training path.

## Data and artifacts

Raw source data, packed caches, model weights, LoRA adapters, checkpoints, active runs, logs, and generated content are intentionally not committed. Keep those on local storage.

## Status

The active experiment uses Qwen3-4B Base with LoRA continued pretraining on a 16 GB AMD GPU. Character SFT is a later, deliberately separate stage.
