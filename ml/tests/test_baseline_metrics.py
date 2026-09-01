from ml.baseline.metrics import compute_metrics


def test_compute_metrics_perfect_predictions_score_one():
    label_names = ["cancel_order", "track_refund"]
    y_true = [0, 0, 1, 1]
    y_pred = [0, 0, 1, 1]

    metrics = compute_metrics(y_true, y_pred, label_names)

    assert metrics["accuracy"] == 1.0
    assert metrics["macro_f1"] == 1.0
    assert metrics["weighted_f1"] == 1.0
    assert metrics["confusion_matrix"] == [[2, 0], [0, 2]]
    assert metrics["confusion_matrix_labels"] == label_names


def test_compute_metrics_reports_per_class_precision_recall_and_support():
    label_names = ["cancel_order", "track_refund"]
    y_true = [0, 0, 1, 1]
    y_pred = [0, 1, 1, 1]

    metrics = compute_metrics(y_true, y_pred, label_names)

    assert metrics["per_class"]["cancel_order"]["precision"] == 1.0
    assert metrics["per_class"]["cancel_order"]["recall"] == 0.5
    assert metrics["per_class"]["cancel_order"]["support"] == 2
    assert metrics["per_class"]["track_refund"]["recall"] == 1.0
    assert metrics["per_class"]["track_refund"]["support"] == 2
    assert 0.0 < metrics["accuracy"] < 1.0
