from ml.bilstm.config import PAD_INDEX, PAD_TOKEN, UNK_INDEX, UNK_TOKEN
from ml.bilstm.tokenizer import Vocabulary, build_vocabulary, tokenize


def test_tokenize_lowercases_and_keeps_contractions():
    assert tokenize("Can't Cancel My Order!") == ["can't", "cancel", "my", "order"]


def test_build_vocabulary_reserves_pad_and_unk_at_fixed_indices():
    vocabulary = build_vocabulary(["hello world", "hello there"])
    assert vocabulary.to_dict()[PAD_TOKEN] == PAD_INDEX
    assert vocabulary.to_dict()[UNK_TOKEN] == UNK_INDEX


def test_build_vocabulary_drops_tokens_below_min_frequency():
    texts = ["frequent frequent frequent", "rare_once nothing_else"]
    vocabulary = build_vocabulary(texts, max_vocab_size=100, min_token_freq=2)

    assert "frequent" in vocabulary.to_dict()
    assert "rare_once" not in vocabulary.to_dict()


def test_build_vocabulary_respects_max_vocab_size_budget():
    texts = [f"token{i}" for i in range(50)]
    vocabulary = build_vocabulary(texts, max_vocab_size=12, min_token_freq=1)

    # 12 total slots minus 2 reserved for <pad>/<unk> leaves 10 real tokens.
    assert len(vocabulary) == 12


def test_encode_maps_out_of_vocabulary_tokens_to_unk():
    vocabulary = build_vocabulary(["known token here"], min_token_freq=1)

    encoded = vocabulary.encode("known totally_unseen_word")

    known_id = vocabulary.to_dict()["known"]
    assert encoded[0] == known_id
    assert encoded[1] == UNK_INDEX


def test_encode_truncates_to_max_seq_len():
    vocabulary = build_vocabulary(["a b c d e f"], min_token_freq=1)

    encoded = vocabulary.encode("a b c d e f", max_seq_len=3)

    assert len(encoded) == 3


def test_encode_empty_text_falls_back_to_single_unk_token():
    vocabulary = build_vocabulary(["hello world"], min_token_freq=1)

    encoded = vocabulary.encode("!!!")

    assert encoded == [UNK_INDEX]


def test_build_vocabulary_only_sees_training_text():
    """A word appearing only in held-out text must never enter the fit vocabulary."""
    train_texts = ["order status", "cancel order"]
    vocabulary = build_vocabulary(train_texts, min_token_freq=1)

    leaked_word = "onlyinvalidationtext"
    assert leaked_word not in vocabulary.to_dict()


def test_vocabulary_roundtrips_through_dict():
    original = build_vocabulary(["hello world foo bar"], min_token_freq=1)
    restored = Vocabulary.from_dict(original.to_dict())

    assert restored.to_dict() == original.to_dict()
    assert len(restored) == len(original)
