# Fine-tuned DistilBERT — v1

## Configuration
- Mode: smoke
- Checkpoint: distilbert-base-uncased
- Max sequence length: 64
- Model: {'checkpoint': 'distilbert-base-uncased', 'seq_classif_dropout': 0.1}
- Training: {'batch_size': 16, 'learning_rate': 5e-05, 'weight_decay': 0.01, 'max_epochs': 1, 'early_stopping_patience': 1, 'max_train_examples': 270, 'max_eval_examples': 135, 'seed': 42}

## Training summary
- Epochs run: 1
- Best epoch: 1
- Stopped early: False
- Row counts used: {'train': 270, 'validation': 135, 'test': 135}

## Validation metrics
- Accuracy: 0.1111
- Macro precision: 0.0191
- Macro recall: 0.1111
- Macro F1: 0.0319
- Weighted F1: 0.0319

## Test metrics
- Accuracy: 0.1333
- Macro precision: 0.0769
- Macro recall: 0.1333
- Macro F1: 0.0645
- Weighted F1: 0.0645
