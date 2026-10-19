#!/usr/bin/env bash
set -euo pipefail

PYTHON=/home/masonturlington/HENTAI/.venv/bin/python
PROJECT=/mnt/c/Users/turli/Documents/Codex/2026-10-09/i-w/work/erp-llm

exec "$PYTHON" "$PROJECT/scripts/train_cpt_rocm.py" \
  --max-steps 500 \
  --save-steps 500 \
  --sequence-length 512 \
  --gradient-accumulation 16 \
  --output /mnt/d/ERP-LLM/adapters/cpt-v1
