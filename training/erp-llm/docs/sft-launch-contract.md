# Private SFT launch contract

This is the implementation contract for Lucy's separate supervised
fine-tuning stage. It prevents a plausible-looking command from silently
training the wrong objective or overwriting the CPT handoff.

## Inputs

- A complete, immutable CPT parent adapter. The selected parent is the
  step-39,500 adapter and its SHA-256 is recorded alongside the SFT run.
- One frozen, private ShareGPT-style JSONL manifest. Rejected candidates and
  the holdout suite are excluded by path and fingerprint.
- A local Qwen base-model directory matching the CPT parent's adapter config.

## Training semantics

- Render each `system`, `user`, and `assistant` turn with the Qwen chat
  template. Add labels only for assistant content; system/user/control tokens
  use `-100` and cannot contribute to loss.
- Keep records intact during the deterministic train/validation split. A
  multi-turn scene must never span both splits.
- Load the CPT adapter as trainable, then save every SFT checkpoint to its own
  run directory. Do not merge, mutate, rotate, or delete CPT checkpoints.
- Resume only from complete SFT resume checkpoints within the same run and
  only when its manifest and CPT-parent checksum agree.

## Required smoke proof

Before a real GPU run, a disposable two-step SFT smoke run must prove:

1. the selected CPT adapter loads;
2. at least one assistant-token label exists in each training batch;
3. prompt labels are masked;
4. a separate SFT adapter/checkpoint is written and integrity-checked;
5. the frozen holdout is untouched.

The final `start SFT` action is permitted only when the corpus content review,
structural audit, semantic audit, frozen evaluation manifest, and smoke proof
are all green.
