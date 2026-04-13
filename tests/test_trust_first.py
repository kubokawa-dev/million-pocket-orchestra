from src.trust_first import (
    GovernanceBucket,
    apply_trust_first_hot_models,
    apply_trust_first_weights,
    classify_numbers3_metrics,
    classify_numbers4_metrics,
)


def test_classify_numbers4_metrics_buckets():
    assert classify_numbers4_metrics(40.0, 12.0) == "preferred"
    assert classify_numbers4_metrics(12.0, 4.0) == "deprioritized"
    assert classify_numbers4_metrics(24.0, 10.0) == "watch"


def test_classify_numbers3_metrics_buckets():
    assert classify_numbers3_metrics(30.0, 1, 2) == "preferred"
    assert classify_numbers3_metrics(8.0, 0, 1) == "deprioritized"
    assert classify_numbers3_metrics(15.0, 1, 1) == "watch"


def test_apply_trust_first_weights_and_hot_models():
    governance = {
        "box_model": GovernanceBucket("box_model", "preferred", 1.0),
        "lightgbm": GovernanceBucket("lightgbm", "deprioritized", 0.55),
    }

    adjusted_weights = apply_trust_first_weights(
        {"box_model": 40.0, "lightgbm": 20.0, "unknown_model": 10.0},
        governance,
    )
    assert adjusted_weights["box_model"] == 40.0
    assert adjusted_weights["lightgbm"] == 11.0
    assert adjusted_weights["unknown_model"] == 7.5

    adjusted_hot_models = apply_trust_first_hot_models(
        [("lightgbm", 100.0), ("box_model", 80.0)],
        governance,
    )
    assert adjusted_hot_models[0][0] == "box_model"
    assert adjusted_hot_models[0][1] == 80.0
    assert adjusted_hot_models[1][0] == "lightgbm"
    assert adjusted_hot_models[1][1] == 55.0
