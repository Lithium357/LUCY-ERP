# ERP LLM project

This project uses a two-stage adapter workflow intended for a single 16 GB GPU:

1. Continued pretraining (CPT) on raw, long-form roleplay prose.
2. Supervised fine-tuning (SFT) on curated multi-turn roleplay conversations.

Raw source files are deliberately preserved without transformation in a local
data root chosen at collection time. Collection defaults to a 512 GiB cap.
No training job should read raw data directly; a later preparation step will
create versioned, auditable CPT and SFT manifests.

## Current source assignment

| Source | Planned use |
|---|---|
| `sdsr/erp-and-erotica` | CPT candidate |
| `PygmalionAI/PIPPA` | Supplemental SFT candidate |
| `chimbiwide/RolePlay-NPCv2` | Supplemental SFT candidate |
| `openerotica/erotica-analysis` | Auxiliary analysis/task data |
| `openerotica/mixed-rp` | Supplemental SFT candidate |
| `devesh75/NSFW-Roleplay-Conversations` | Supplemental SFT candidate |
| `athirdpath/DPO_Pairs-Roleplay-Llama3-NSFW` | DPO only |
| `backpropSukuna/wifu-chat-dataset` | Small supplemental SFT candidate |
| `RuneForgeAI/Viking_Witch_flirty_and_erotic_behavior` | Character-adapter candidate |
| `lemonilia/LimaRP` | Core SFT candidate |
| `Gryphe/Sonnet3.5-Charcard-Roleplay` | Supplemental SFT candidate; license review required |

## Collection

Install the lightweight collector dependency and run it:

```powershell
& $python -m pip install huggingface_hub
& $python .\scripts\collect_datasets.py --root D:\LucyData
```

The script resumes interrupted Hugging Face transfers and writes a JSON
manifest beside the raw data.  It collects repositories as-is and does not
filter, normalize, or generate training examples.
