# Fine-tuned DistilBERT — v2

## Configuration
- Mode: full
- Checkpoint: distilbert-base-uncased
- Max sequence length: 64
- Model: {'checkpoint': 'distilbert-base-uncased', 'seq_classif_dropout': 0.1}
- Training: {'batch_size': 16, 'learning_rate': 3e-05, 'weight_decay': 0.01, 'max_epochs': 5, 'early_stopping_patience': 2, 'max_train_examples': None, 'max_eval_examples': None, 'seed': 42}

## Training summary
- Epochs run: 5
- Best epoch: 3
- Stopped early: True
- Row counts used: {'train': 21430, 'validation': 2743, 'test': 2699}

## Validation metrics
- Accuracy: 0.9982
- Macro precision: 0.9982
- Macro recall: 0.9982
- Macro F1: 0.9982
- Weighted F1: 0.9982

## Test metrics
- Accuracy: 0.9978
- Macro precision: 0.9979
- Macro recall: 0.9980
- Macro F1: 0.9979
- Weighted F1: 0.9978
