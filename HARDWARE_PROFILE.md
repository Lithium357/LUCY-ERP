# LUCY training and evaluation environment

This is the sanitized local platform profile for the active LUCY experiments.
It supports reproducibility without publishing serial numbers, account details,
personal paths, network identifiers, private workloads, model artifacts, or
training data.

Captured: 2026-10-21

| Area | Configuration |
|---|---|
| Host OS | Windows 11 Home, x64, build 26200 |
| Board | ASRock B550 PG Velocita |
| CPU | AMD Ryzen 5 5600 (6 cores / 12 threads) |
| Host memory | 32 GB installed |
| GPU | AMD Radeon RX 7800 XT, 16 GB dedicated VRAM |
| Windows driver | 32.0.31041.1004 |
| Storage | 1 TB SATA SSD and 2 TB NVMe SSD |
| WSL | WSL 2.7.11.0; Linux 6.18.33.2-microsoft-standard-WSL2 |
| WSL allocation observed | 12 vCPUs, 15 GiB RAM, 4 GiB swap |
| ML environment | Python 3.14; PyTorch 2.13.0+rocm10.0.0; Transformers 4.57.6; PEFT 0.20.0 |

## Caveat

The generic Windows WMI `AdapterRAM` field reports 4 GiB for this GPU under
the current WDDM stack. It is not used by this project; the 16 GB value is
from Windows dedicated-GPU-memory telemetry. `rocm-smi` and `amd-smi` are not
exposed inside this WSL image.

For synthetic ROCm/WSL reproductions and external runtime findings, see the
separate [ROCm WSL Lab](https://github.com/Lithium357/rocm-wsl-lab).
