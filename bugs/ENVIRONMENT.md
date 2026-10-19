# Reproduction environment

Last verified: **2026-10-19**. This is the exact non-identifying hardware and
software fingerprint for the Lucy ROCm/WSL observations. It intentionally
excludes usernames, serial numbers, device IDs, network information, and local
filesystem paths.

## Host hardware

| Component | Configuration |
| --- | --- |
| CPU | AMD Ryzen 5 5600 — 6 cores / 12 threads |
| Host memory | 31.9 GiB physical memory |
| GPU | ASRock Challenger AMD Radeon RX 7800 XT, 16 GiB VRAM |
| GPU driver | AMD Windows driver `32.0.31041.1004` (2026-08-16) |
| Sustained-training cooling observation | GPU core ~54°C, hotspot ~85°C, fan ~2,858 RPM at full compute; observational, not a test limit |

## Windows and WSL

| Component | Configuration |
| --- | --- |
| Windows host version reported by WSL | `10.0.26200.9711` |
| WSL | `2.7.11.0` |
| WSL kernel | `6.18.33.2-microsoft-standard-WSL2` |
| WSLg | `1.0.73.2` |
| Direct3D bridge | `1.611.1-81528511` |
| WSL distribution | Ubuntu 26.04 LTS |
| Guest CPU topology | 12 vCPUs, one NUMA node |
| Effective guest memory / swap observed during CPT | 15 GiB / 4 GiB |

The effective guest-memory limit matters: the VMBus allocation warnings in
[0004](wsl/0004-hv-vmbus-channel-allocation.md) occurred with low free guest
memory and a large page cache.

## ML runtime

| Component | Configuration |
| --- | --- |
| Python | 3.14.4 |
| PyTorch | `2.13.0+rocm10.0.0` |
| HIP runtime | `7.15.26333` |
| Transformers | 4.57.6 |
| PEFT | 0.20.0 |
| Attention path for stable training | Default SDPA |
| Experimental path tested | `TORCH_ROCM_AOTRITON_ENABLE_EXPERIMENTAL=1` — unstable; see [0001](rocm-wsl/0001-experimental-aotriton-dxg-sync.md) |

## Active CPT geometry

| Setting | Value |
| --- | --- |
| Base model | Qwen3-4B Base |
| Adaptation | LoRA rank 16, alpha 32, dropout 0.05 |
| Precision | BF16 |
| Context length | 512 tokens |
| Microbatch / accumulation | 1 / 16 (8,192 tokens per optimizer step) |
| Activation checkpointing | Enabled |
| Learning rate / weight decay | 1e-4 / 0.01 |
| Validation split / cadence | 1% / every 500 optimizer steps |
| Adapter and resume checkpoints | Every 500 optimizer steps |
| Packed-cache location for stable run | WSL ext4; mounted Windows storage produced an `Errno 5` event ([0003](wsl/0003-mnt-d-errno5-packed-cache.md)) |

## Control baseline

The stable 250-step SDPA control run had a median **14.367 seconds per step**
and **570.20 tokens per second**. Normal sustained operation is roughly
14.5 seconds/step and 565 tokens/second. Treat material deviations alongside
new kernel errors as an investigation trigger, not proof of a regression by
themselves.

## Reproduction hygiene

1. Record this page's version table with every report.
2. Reproduce one changed variable at a time using [the test matrix](TEST_MATRIX.md).
3. Attach the relevant `dmesg` delta, unedited application error, and control result.
4. Do not include raw training data, model weights, checkpoints, or personal paths in public reports.
