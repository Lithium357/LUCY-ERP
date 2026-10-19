# External bug ledger

This directory records failures encountered while developing or operating Lucy that appear to originate outside Lucy's own code: ROCm, HIP, PyTorch ROCm builds, WSL, Windows GPU virtualization, drivers, or filesystem layers.

It is deliberately evidence-first. A note is an observation, not a claim that a vendor caused it. Every entry identifies the affected layer, an exact environment, the smallest known reproduction, raw evidence, a control case, mitigation, and confidence.

Start with the privacy-scrubbed [reproduction environment](ENVIRONMENT.md) and
the [controlled test matrix](TEST_MATRIX.md) before comparing a new result.

## Scope

- Include platform/runtime failures and regressions with enough information for an external maintainer to investigate.
- Exclude Lucy application defects, training-data quality problems, model behavior, and configuration mistakes unless they are needed as a control.
- Never commit raw datasets, checkpoints, personal conversations, credentials, or full system logs containing private paths or identifiers.

## Status vocabulary

- **Observed:** happened, but not yet reproduced in isolation.
- **Candidate external bug:** control/affected comparison points to an external layer; not vendor-confirmed.
- **Mitigated:** a safe workaround is in place; root cause remains open.
- **Resolved:** fixed upstream or no longer reproducible on a documented version.

## New-entry checklist

1. Start from `template.md` and assign the next numeric prefix.
2. Preserve the original error text and timestamp in redacted form.
3. Record the exact runtime and hardware version set.
4. Add an affected run and a one-variable control run when feasible.
5. State whether data/checkpoints were lost and name the mitigation.
6. Update the issue only with evidence; separate inference from observation.
