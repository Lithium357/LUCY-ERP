#!/usr/bin/env bash
# Read-only diagnostic snapshot for a future ERP/ROCm/WSL incident.
set -euo pipefail

project_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
run_dir="${1:?pass the affected run directory as the first argument}"
stamp="$(date -u +%Y%m%dT%H%M%SZ)"
out_dir="${2:-$project_dir/incident-reports}/${stamp}"
python_cmd="${LUCY_PYTHON:-python}"
service_name="${LUCY_TRAINER_SERVICE:-erp-qwen3-4b-cpt-v2.service}"
mkdir -p "$out_dir"

{
  echo "captured_utc=$stamp"
  echo
  echo '## kernel'
  uname -a
  echo
  echo '## Python and ROCm'
  "$python_cmd" -c 'import torch, transformers, peft; print("torch="+torch.__version__); print("hip="+str(torch.version.hip)); print("transformers="+transformers.__version__); print("peft="+peft.__version__)'
  echo
  echo '## Trainer service'
  systemctl --user show "$service_name" -p ActiveState -p SubState -p Result -p ExecMainStatus -p MainPID -p NRestarts -p Restart --no-pager || true
  journalctl --user -u "$service_name" -n 300 --no-pager || true
  echo
  echo '## WSL GPU bridge kernel lines'
  dmesg --color=never | grep -Ei 'dxg|amdgpu|rocm|gpu|oom' | tail -n 300 || true
  echo
  echo '## Run config and latest progress'
  sed -n '1,200p' "$run_dir/config.json" || true
  tail -n 200 "$run_dir/progress/train.csv" || true
} > "$out_dir/incident.txt"

printf 'Incident evidence written to %s\n' "$out_dir/incident.txt"
