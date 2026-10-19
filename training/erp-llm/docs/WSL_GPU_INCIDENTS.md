# ERP training incident stockpile

This is a private, evidence-first log for issues observed while training a
Qwen3-4B LoRA CPT workload on an AMD RX 7800 XT through WSL2. Do not convert
an observation into a bug claim until it has a minimal reproduction.

## Environment fingerprint

| Field | Value |
| --- | --- |
| Host GPU | AMD Radeon RX 7800 XT, 16 GB |
| WSL | 2.7.11.0 |
| Windows | 10.0.26200.9711 |
| WSL kernel | 6.18.33.2-microsoft-standard-WSL2 |
| PyTorch | 2.13.0+rocm10.0.0 |
| HIP runtime | 7.15.26333 |
| Transformers / PEFT | 4.57.6 / 0.20.0 |
| Stable control workload | Qwen3-4B LoRA, BF16, 512 context, batch 1 x accumulation 16, activation checkpointing, default SDPA |

## Candidate report: experimental attention triggers dxgkrnl synchronization failure

**Audience:** AMD ROCm and Microsoft WSL graphics teams.

**Configuration:** the stable control geometry above, with only
`TORCH_ROCM_AOTRITON_ENABLE_EXPERIMENTAL=1` added.

**Observed result:** steps 1 and 2 completed at approximately 508 and 716
tokens/sec, followed by WSL dxgkrnl warnings. The benchmark was stopped rather
than allowed to corrupt a long run.

**Kernel evidence:**

```text
memcpy: detected field-spanning write ... dxgvmbus.c:3095
WARNING: ... dxgvmb_send_wait_sync_object_gpu
dxgk: dxgkio_wait_sync_object_cpu: wait_completion_interruptible: -512
dxgk: dxgkio_wait_sync_object_cpu: Ioctl failed: -512
```

**Control:** default SDPA, with the otherwise identical geometry, completed
250 steps at a median 14.367 seconds/step and 570.20 tokens/sec without a new
dxgkrnl warning.

**Ask:** reproduce on RDNA3 under WSL2 using a small BF16 SDPA/AOTriton
comparison. Determine whether the warning is a bridge bug, a ROCm interaction,
or an unsupported experimental path. Do not present the two-step throughput as
a performance result.

## Candidate report: larger activation footprint fails via WSL allocation path

**Audience:** Microsoft WSL graphics team, with AMD ROCm visibility.

**Configuration:** Qwen3-4B LoRA, BF16, 512 context, microbatch 1,
accumulation 16, but activation checkpointing disabled.

**Observed result:** model setup failed before a usable first training step.

**Kernel evidence:**

```text
dxgk: create_existing_sysmem: get_user_pages_fast failed: 2534
dxgk: dxgvmb_send_sync_msg: wait_for_completion failed: fffffe00
dxgk: create_local_allocations: failed to destroy allocations: fffffe00
dxgk: dxgkio_create_allocation: Ioctl failed: -12
```

**Interpretation:** likely allocation/resource exhaustion in the WSL graphics
bridge. It is not a confirmed VRAM-OOM: PyTorch did not report an explicit OOM
and WSL lacked usable ROCm CLI telemetry at the time.

**Ask:** improve error propagation so this fails as an actionable allocation or
out-of-memory error rather than opaque dxgkrnl messages. Retest after a clean
WSL restart and record host-side VRAM metrics.

## WSL filesystem report: active `/mnt/d` cache returned Errno 5

**Audience:** Microsoft WSL filesystem team. This is not evidence of an AMD
GPU defect.

**Configuration:** stable control geometry; 29 GB packed `uint32` cache read
from a Windows-mounted `/mnt/d` packed-cache path during long training.

**Observed result:** after a complete step-2000 checkpoint, the trainer raised:

```text
OSError: [Errno 5] Input/output error
  PackedBlocks.__iter__ -> handle.read(context_length * 4)
```

There was no CUDA/HIP exception, dxgkrnl warning, OOM, or thermal event.

**Mitigation and outcome:** copied the active cache to WSL ext4, verified both
file sizes and `manifest.json` SHA-256, and resumed from step 2000. The run
continued at approximately 565 tokens/sec. Keep archival data/checkpoints on
Windows storage if desired, but keep active read-heavy training caches on ext4.

## Evidence to attach to any public report

1. This environment table and exact command/configuration.
2. Full unedited `journalctl --user` excerpt and relevant `dmesg` lines.
3. A control run and an affected run with one intentional variable changed.
4. Checkpoint state and whether data was lost.
5. A clear statement of what is observed versus inferred.
