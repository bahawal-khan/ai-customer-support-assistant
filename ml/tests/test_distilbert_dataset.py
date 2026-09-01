import torch

from ml.distilbert.dataset import IntentTextDataset, collate_batch
from ml.tests.distilbert_test_utils import build_tiny_tokenizer

_VOCAB_WORDS = ["topic0", "topic1", "keyword0", "keyword1", "sample", "words", "extra", "here"]


def test_intent_text_dataset_rejects_mismatched_lengths():
    tokenizer = build_tiny_tokenizer(_VOCAB_WORDS)
    try:
        IntentTextDataset(texts=["a", "b"], labels=[0], tokenizer=tokenizer)
        assert False, "expected ValueError"
    except ValueError:
        pass


def test_intent_text_dataset_encodes_and_truncates():
    tokenizer = build_tiny_tokenizer(_VOCAB_WORDS)
    texts = ["topic0 keyword0 sample words", "topic1 extra here"]
    labels = [0, 1]

    dataset = IntentTextDataset(texts=texts, labels=labels, tokenizer=tokenizer, max_seq_len=3)

    assert len(dataset) == 2
    input_ids, attention_mask, label = dataset[0]
    # max_seq_len=3 truncates the tokenizer output (including [CLS]/[SEP]) to 3 ids.
    assert len(input_ids) == 3
    assert len(attention_mask) == 3
    assert label == 0


def test_collate_batch_pads_to_longest_sequence():
    tokenizer = build_tiny_tokenizer(_VOCAB_WORDS)
    texts = ["topic0 keyword0 sample words", "topic1"]
    labels = [0, 1]
    dataset = IntentTextDataset(texts=texts, labels=labels, tokenizer=tokenizer)

    batch = [dataset[0], dataset[1]]
    input_ids, attention_mask, label_tensor = collate_batch(
        batch, pad_token_id=tokenizer.pad_token_id
    )

    assert input_ids.shape == attention_mask.shape
    assert input_ids.shape[0] == 2
    assert torch.equal(label_tensor, torch.tensor([0, 1]))
    # The shorter sequence's tail must be padded with the tokenizer's pad id.
    shorter_length = len(dataset[1][0])
    assert torch.all(input_ids[1, shorter_length:] == tokenizer.pad_token_id)
    assert torch.all(attention_mask[1, shorter_length:] == 0)
