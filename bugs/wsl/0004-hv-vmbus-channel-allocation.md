# 0004 — WSL Hyper-V VMBus channel allocation warnings under sustained memory pressure

**Status:** Observed
**Affected layer:** WSL / Hyper-V VMBus memory allocation
**Potential audience:** Microsoft WSL graphics and virtualization teams
**First observed:** 2026-10-19

## Environment

| Field | Value |
| --- | --- |
| GPU | AMD Radeon RX 7800 XT, 16 GB |
| Windows | 10.0.26200.9711 |
| WSL / kernel | 2.7.11.0 / 6.18.33.2-microsoft-standard-WSL2 |
| PyTorch / ROCm | 2.13.0+rocm10.0.0 |
| Active workload | Long Qwen3-4B LoRA CPT, BF16, context 512, microbatch 1, accumulation 16 |

## Observed behavior

The WSL kernel log contains repeated allocation warnings from Hyper-V VMBus workqueue activity:

```text
kworker/0:*: page allocation failure: order:7, mode:0xdc0(GFP_KERNEL|__GFP_ZERO)
Workqueue: hv_pri_chan vmbus_add_channel_work
vmbus_alloc_ring
hvs_probe
```

At observation time, WSL reported 15 GiB total memory, roughly 415 MiB free,
about 13 GiB page cache/buffers, and 851 MiB swap in use. The trainer remained
active with zero service restarts.

## Minimal reproduction

Not yet isolated. The warnings occurred during a long-running GPU training
session with constrained WSL guest memory and service activity.

## Control result

Not yet collected. A future controlled test should compare the same WSL memory
limit with and without sustained page-cache pressure, without the production
trainer running.

## Impact

No trainer failure, checkpoint loss, GPU reset, or visible service outage was
observed. The warnings taint the WSL kernel and may affect creation of VMBus
channels (for example, host-service or vsock activity), so they merit capture
before a user-visible failure occurs.

## Mitigation

No active mitigation was applied to avoid perturbing the production run. Future
experiments should leave headroom in the WSL memory cap and characterize cache
reclaim behavior after the training window.

## Assessment

Observed: the kernel emitted repeated Hyper-V VMBus allocation failures while
WSL was memory-constrained. Inference: this is a WSL/Hyper-V resource-pressure
signal, not evidence of an AMD GPU or ROCm defect. It should not be reported
to AMD as a GPU issue without a direct ROCm linkage.
