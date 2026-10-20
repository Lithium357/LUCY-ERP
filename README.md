# LUCY

Private local training, evaluation, and runtime work for Lucy: one persistent personal roleplay LLM.

## Scope

This repository contains only Lucy-specific language-model work and reproducible AMD/ROCm/WSL training notes. It deliberately excludes unrelated applications, dashboards, diffusion tooling, raw datasets, user conversations, model weights, checkpoints, generated outputs, credentials, and private source code from other projects.

## Contents

- `training/erp-llm/configs/` — 16 GB-class CPT and SFT configuration references.
- `training/erp-llm/scripts/` — progress, checkpoint, and CPU-generation diagnostics.
- `training/erp-llm/evaluation/` — public-safe evaluation procedure and reviewer scorecard.

External ROCm/WSL evidence and synthetic reproduction work live in the separate
[ROCm WSL Lab](https://github.com/Lithium357/rocm-wsl-lab). This repository
does not duplicate runtime bug reports or contain private Studio code.

## Data and artifacts

Raw source data, packed caches, model weights, LoRA adapters, checkpoints, active runs, logs, and generated content are intentionally not committed. Keep those on local storage.

## Status

The active experiment uses Qwen3-4B Base with LoRA continued pretraining on a
16 GB AMD GPU. Character SFT is a later, deliberately separate stage. Metrics,
evaluation prompts, generated completions, adapters, and checkpoints remain
local.
