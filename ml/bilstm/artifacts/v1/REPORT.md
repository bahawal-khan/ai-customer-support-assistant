# Embedding + BiLSTM Baseline — v1

## Configuration
- Vocabulary size: 1065
- Max sequence length: 32
- Model: {'embedding_dim': 128, 'hidden_dim': 128, 'num_lstm_layers': 1, 'dropout': 0.3}
- Training: {'batch_size': 64, 'learning_rate': 0.001, 'weight_decay': 0.0, 'max_epochs': 20, 'early_stopping_patience': 3, 'seed': 42}

## Training summary
- Epochs run: 7
- Best epoch: 4
- Stopped early: True

## Validation metrics
- Accuracy: 0.9913
- Macro precision: 0.9912
- Macro recall: 0.9911
- Macro F1: 0.9911
- Weighted F1: 0.9912

## Test metrics
- Accuracy: 0.9926
- Macro precision: 0.9926
- Macro recall: 0.9928
- Macro F1: 0.9926
- Weighted F1: 0.9926
