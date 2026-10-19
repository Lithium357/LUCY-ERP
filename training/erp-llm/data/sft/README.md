# Astra-6 v1 seed SFT set

`astra6-v1-seed.jsonl` is a **private, synthetic, original** seed set for a
final character QLoRA. It is deliberately separate from CPT and from the
general roleplay SFT corpus.

- Format: JSONL, one ShareGPT-style `messages` conversation per line.
- Size: 93 examples.
- Character premise: Astra is an adult and the user's established exclusive
  partner.
- Distribution: daily relationship (18), emotional support/conflict repair
  (18), playful tension (18), contextual intimacy and aftercare (18), brief
  prompts (12), and OOC/settings handling (9).

The CS degree and cafe job appear only as grounding texture. Intimate behavior
is canonical to the relationship but context-sensitive; this seed set avoids
making it the automatic answer to ordinary conversation.

## Regenerate

```powershell
wsl.exe -d Ubuntu -- /home/masonturlington/HENTAI/.venv/bin/python \
  /mnt/c/Users/turli/Documents/Codex/2026-10-09/i-w/work/erp-llm/scripts/build_astra6_sft.py
```

## Before training

Review the JSONL line by line, then combine it with the general prepared SFT
manifest using an explicit source label. Keep held-out Astra evaluation prompts
separate. This is a seed set, not a substitute for several hundred manually
reviewed scene-level conversations.
