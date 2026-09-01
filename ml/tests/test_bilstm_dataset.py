import torch

from ml.bilstm.config import PAD_INDEX
from ml.bilstm.dataset import IntentSequenceDataset, collate_batch
from ml.bilstm.tokenizer import build_vocabulary


def test_dataset_encodes_each_example():
    vocabulary = build_vocabulary(["hello world", "foo bar baz"], min_token_freq=1)
    dataset = IntentSequenceDataset(
        texts=["hello world", "foo bar baz"], labels=[0, 1], vocabulary=vocabulary
    )

    assert len(dataset) == 2
    encoded_0, label_0 = dataset[0]
    assert label_0 == 0
    assert len(encoded_0) == 2


def test_dataset_rejects_mismatched_lengths():
    vocabulary = build_vocabulary(["hello"], min_token_freq=1)
    try:
        IntentSequenceDataset(texts=["a", "b"], labels=[0], vocabulary=vocabulary)
        assert False, "expected ValueError"
    except ValueError:
        pass


def test_collate_batch_pads_to_longest_sequence_in_batch():
    batch = [([1, 2, 3], 0), ([4, 5], 1)]

    input_ids, lengths, labels = collate_batch(batch)

    assert input_ids.shape == (2, 3)
    assert torch.equal(lengths, torch.tensor([3, 2]))
    assert torch.equal(labels, torch.tensor([0, 1]))
    # shorter sequence padded with PAD_INDEX at the end.
    assert input_ids[1, 2].item() == PAD_INDEX
