# LUCY training and evaluation environment

This is the sanitized local platform profile for the active LUCY experiments.
It supports reproducibility without publishing serial numbers, account details,
personal paths, network identifiers, private workloads, model artifacts, or
training data.

Captured: 2026-10-21

| Area | Configuration |
|---|---|
| Host OS | Windows 11 Home, x64, version 10.0.26200 (build 26200) |
| Board / BIOS | ASRock B550 PG Velocita; AMI P2.40, released 2022-10-18 |
| CPU | AMD Ryzen 5 5600; 1 socket, 6 cores / 12 threads; 32 MiB L3 cache |
| Host memory | 32 GB: 2 × 16 GB DIMMs, configured at 2400 MT/s |
| GPU | AMD Radeon RX 7800 XT, 16 GB dedicated VRAM |
| Windows driver | AMD provider; 32.0.31041.1004; driver date 2026-08-16 |
| Storage | Samsung 870 EVO 1 TB SATA SSD; TEAM TM8FP6002T 2 TB NVMe SSD |
| WSL | WSL 2.7.11.0; kernel 6.18.33.2-microsoft-standard-WSL2; WSLg 1.0.73.2; Direct3D 1.611.1 |
| WSL allocation observed | 12 vCPUs, 15 GiB RAM, 4 GiB swap |
| Python | Python 3.14 virtual environment |
| Framework | PyTorch 2.13.0+rocm10.0.0; Triton 3.8.0+git4cff872c.rocm10.0.0 |
| LLM packages | Transformers 4.57.6; PEFT 0.20.0; Accelerate 1.14.0; Tokenizers 0.22.2; Safetensors 0.8.0 |
| ROCm packages | `rocm` 10.0.0; `rocm-bootstrap` 0.1.0; `amd-torch-device-gfx1101` 2.13.0+rocm10.0.0 |

## Caveat

The generic Windows WMI `AdapterRAM` field reports 4 GiB for this GPU under
the current WDDM stack. It is not used by this project; the 16 GB value is
from Windows dedicated-GPU-memory telemetry. `rocm-smi` and `amd-smi` are not
exposed inside this WSL image.

For synthetic ROCm/WSL reproductions and external runtime findings, see the
separate [ROCm WSL Lab](https://github.com/Lithium357/rocm-wsl-lab).
