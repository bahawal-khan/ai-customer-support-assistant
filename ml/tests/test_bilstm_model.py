import torch

from ml.bilstm.dataset import collate_batch
from ml.bilstm.model import BiLSTMClassifier, build_model


def test_build_model_uses_project_configuration():
    model = build_model(vocab_size=50, num_classes=5)

    assert isinstance(model, BiLSTMClassifier)
    assert model.embedding.num_embeddings == 50
    assert model.classifier.out_features == 5


def test_forward_returns_logits_shaped_batch_by_num_classes():
    model = build_model(vocab_size=20, num_classes=4)
    batch = [([1, 2, 3], 0), ([4, 5], 1), ([6], 2)]
    input_ids, lengths, _ = collate_batch(batch)

    logits = model(input_ids, lengths)

    assert logits.shape == (3, 4)


def test_forward_is_deterministic_in_eval_mode():
    model = build_model(vocab_size=20, num_classes=4)
    model.eval()
    batch = [([1, 2, 3], 0)]
    input_ids, lengths, _ = collate_batch(batch)

    with torch.no_grad():
        first = model(input_ids, lengths)
        second = model(input_ids, lengths)

    assert torch.equal(first, second)
