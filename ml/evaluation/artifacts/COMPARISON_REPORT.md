# Phase 06 — Model Evaluation & Selection

Generated: 2026-08-27T14:40:10.152343+00:00
Seed: 42
Held-out test set: `E:\Summer-2026-projects\AI-Based-cutomer Support\data\processed\test.csv` (2699 examples, used identically by every model)

## Reproducibility & leakage check
- All three training runs (ml/baseline/train.py, ml/bilstm/train.py, ml/distilbert/train.py) share the same seed=42 data/processed split and select their final model/checkpoint using only validation macro-F1. The test split is scored exactly once, after the model is frozen, and only for reporting -- never for training or checkpoint selection.

## Comparison

| Model | Version | Accuracy | Macro P | Macro R | Macro F1 | Weighted F1 | Size | Latency (mean / p95) |
|---|---|---|---|---|---|---|---|---|
| tfidf_logreg | v1 | 0.9918 | 0.9920 | 0.9919 | 0.9918 | 0.9919 | 1.22 MB | 2.06 ms / 3.59 ms |
| embedding_bilstm | v1 | 0.9926 | 0.9926 | 0.9928 | 0.9926 | 0.9926 | 1.61 MB | 2.84 ms / 5.09 ms |
| distilbert | v2 | 0.9978 | 0.9979 | 0.9980 | 0.9979 | 0.9978 | 256.21 MB | 86.81 ms / 209.69 ms |

## Per-model detail

### tfidf_logreg (v1)
- Test examples: 2699
- Accuracy: 0.9918
- Macro precision / recall / F1: 0.9920 / 0.9919 / 0.9918
- Weighted precision / recall / F1: 0.9921 / 0.9918 / 0.9919
- Model size on disk: 1.22 MB
- Inference latency (n=2694, warmup excluded): mean=2.06 ms, median=1.59 ms, p95=3.59 ms, min=1.26 ms, max=44.03 ms
- Most confused label pairs (true → predicted: count):
  - create_account → delete_account: 6
  - get_invoice → check_invoice: 4
  - track_order → change_order: 4
  - cancel_order → check_cancellation_fee: 1
  - change_order → edit_account: 1

### embedding_bilstm (v1)
- Test examples: 2699
- Accuracy: 0.9926
- Macro precision / recall / F1: 0.9926 / 0.9928 / 0.9926
- Weighted precision / recall / F1: 0.9927 / 0.9926 / 0.9926
- Model size on disk: 1.61 MB
- Inference latency (n=2694, warmup excluded): mean=2.84 ms, median=2.52 ms, p95=5.09 ms, min=1.40 ms, max=131.62 ms
- Most confused label pairs (true → predicted: count):
  - cancel_order → change_order: 5
  - get_invoice → check_invoice: 2
  - change_order → edit_account: 1
  - change_order → place_order: 1
  - check_invoice → get_invoice: 1

### distilbert (v2)
- Test examples: 2699
- Accuracy: 0.9978
- Macro precision / recall / F1: 0.9979 / 0.9980 / 0.9979
- Weighted precision / recall / F1: 0.9978 / 0.9978 / 0.9978
- Model size on disk: 256.21 MB
- Inference latency (n=2694, warmup excluded): mean=86.81 ms, median=65.50 ms, p95=209.69 ms, min=35.58 ms, max=3797.83 ms
- Most confused label pairs (true → predicted: count):
  - track_order → cancel_order: 2
  - track_order → delivery_period: 2
  - create_account → registration_problems: 1
  - newsletter_subscription → get_invoice: 1

## Production model selection

**Selected: `distilbert` (version `v2`)**

- Primary metric: macro_f1
- Secondary metrics considered: weighted_f1, accuracy
- Tie epsilon on primary metric: 0.002
- Rationale: 'distilbert' has the highest macro_f1 (0.9979) among all candidates; no tie-break was needed.
- Full ranking: [{'model_name': 'distilbert', 'macro_f1': 0.9979129056211727}, {'model_name': 'embedding_bilstm', 'macro_f1': 0.9926278168330116}, {'model_name': 'tfidf_logreg', 'macro_f1': 0.9918283409687751}]
