# Private evaluation protocol

This directory contains public-safe tooling and rubrics only. Keep the actual
prompt set, outputs, and human scores outside Git. Never use a training row as
an evaluation prompt.

## Checkpoint comparison

1. Freeze a private holdout prompt set before comparing checkpoints.
2. Run each checkpoint with the same prompt, seed, generation settings, and
   context window. Use `scripts/generation_probe.py` to capture local decoder
   diagnostics and to detect repeat-token loops.
3. Have the same reviewer score blinded outputs using `scorecard.md`.
4. Record only aggregate scores and the checkpoint step in a private result
   file. A lower CPT validation loss is a useful signal, not a substitute for
   this review.

## Safety of the procedure

- CPU probes are intentionally separate from GPU training.
- Do not load an adapter on the GPU while training owns it.
- Keep any report containing prompts or completions in a local ignored output
  directory, never alongside these files.
