#!/usr/bin/env bash
set -euo pipefail

PROJECT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON="${LUCY_PYTHON:-python}"
OUTPUT="${LUCY_OUTPUT:-$PROJECT/outputs/cpt-smoke}"

exec "$PYTHON" "$PROJECT/scripts/train_cpt_rocm.py" \
  --max-steps 500 \
  --save-steps 500 \
  --sequence-length 512 \
  --gradient-accumulation 16 \
  --output "$OUTPUT"
