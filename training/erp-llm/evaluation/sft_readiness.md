# Character SFT readiness gate

The character set is a reviewed seed, not a row-count race. Do not start its
GPU stage until all conditions are true:

1. Run `scripts/audit_sft_dataset.py` and require zero malformed records, zero
   role/shape errors, and zero accidental duplicate final replies.
2. Expand the private character set toward at least 250 genuinely distinct,
   reviewed replies. Include multi-turn records; do not count prompt wrappers
   around the same answer as new data.
3. Freeze a separate private evaluation suite before SFT. It must never appear
   in the character data or preference data.
4. Select the CPT checkpoint with the fixed rubric, then preserve that adapter
   before beginning SFT.
5. Stop CPT intentionally and confirm a complete resume checkpoint before any
   GPU SFT smoke run. Run a tiny disposable smoke adapter before a real pass.

The preferred order is CPT → general chat/roleplay formatting SFT → character
adapter → separate preference adapter. Keep adapters and their metadata
separate so a weaker personal layer can be replaced without retraining the
domain adaptation stage.
