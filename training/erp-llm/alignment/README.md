# Personal alignment plan

This is a private preference layer for the ERP model.  It is intentionally
separate from CPT and SFT: domain data should teach prose and roleplay skill;
this layer should teach the model how *this user* wants it to behave.

## Training order

1. CPT: raw roleplay prose for domain adaptation.
2. SFT: coherent chat format, character consistency, and long-turn behavior.
3. Preference tuning: a small private set of chosen/rejected completions that
   expresses the preferences in `personal-profile.yaml`.
4. Evaluation: compare Base+SFT to Base+CPT+SFT+preference adapter using the
   same held-out rubric.

Do not use an alignment set as CPT input.  Preference examples must remain
out of the held-out evaluation suite.

## Preference-set design

Write examples as a roleplay context followed by two candidate assistant
continuations:

- `chosen`: the response that best matches the personal profile.
- `rejected`: plausible but unwanted behavior (for example, generic assistant
  hedging, breaking character, unwanted check-ins, excessive escalation, or
  poor continuity).

Quality matters more than count.  Start with 150--300 carefully reviewed
pairs spread across the categories below, then add pairs only when an
evaluation failure repeats.

## Initial persona baseline

`personal-profile.yaml` now contains an initial **Affectionate Menace**
profile.  This is the model's sole persistent character, not a selectable
archetype.  Additional character work, if any, belongs in separate future
fine-tunes rather than the base preference set.

The existing profile deliberately covers only personality, relationship, and
non-explicit scene behavior.  Explicit-content preferences will be specified
in a separately reviewed section before they become training data.

## Evaluation rubric

Keep a 100--200 prompt suite that is never trained on.  Score every response
from 1--5 on:

| Dimension | What it measures |
|---|---|
| Character fidelity | Remains in voice and respects persona/world facts |
| Scene continuity | Tracks recent events and user actions |
| Initiative | Moves the scene forward at the desired pace |
| Prose quality | Clear, vivid, non-repetitive writing |
| Boundary fit | Follows the selected personal profile, including redirects |
| OOC reliability | Correctly recognizes and follows out-of-character requests |

Track aggregate scores and specific failure labels.  Train against repeated
failures; do not tune against one-off subjective dislikes.

## Implementation choice

Keep the preference adapter separate from the CPT and SFT adapters.  This
makes it possible to toggle or replace the personal behavior layer without
retraining the prose/roleplay model.
