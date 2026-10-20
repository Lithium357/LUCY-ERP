# Checkpoint scorecard

Score each axis from 1 (poor) to 5 (strong). Compare a candidate checkpoint
with a fixed baseline under identical generation settings.

| Axis | What a strong result looks like |
| --- | --- |
| Character voice | Distinct, consistent voice rather than generic assistant prose. |
| Initiative | Advances the moment appropriately without forcing scene changes. |
| Continuity | Respects the current setting and prior turns; never invents the user's inner state. |
| Emotional intelligence | Responds to tone, conflict, and repair with believable specificity. |
| Prose control | Natural dialogue/action balance, varied syntax, no bloated meta-commentary. |
| Instruction following | Follows explicit scene and style requests without derailing. |
| Repetition | No token loops, phrase echoes, or recycled replies. |

Flag any response that contains a decoder loop, ignores a stop request, breaks
the current scene, narrates the user's thoughts, or invents a time/location
change. A flagged response is a regression even if its average score is high.
