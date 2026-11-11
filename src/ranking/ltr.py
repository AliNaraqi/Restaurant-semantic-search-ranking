"""LightGBM LambdaRank learning-to-rank model."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import lightgbm as lgb
import numpy as np

from src.config import LTR_MODEL_PATH
from src.ranking.features import FEATURE_NAMES


def train_ltr(
    X: np.ndarray,
    y: np.ndarray,
    group: list[int],
    params: dict[str, Any] | None = None,
) -> lgb.Booster:
    """Train a LambdaRank model.

    group: list of query group sizes (sum == len(y)).
    y: graded relevance labels (0..4).
    """
    default_params = {
        "objective": "lambdarank",
        "metric": "ndcg",
        "ndcg_eval_at": [5, 10],
        "learning_rate": 0.05,
        "num_leaves": 31,
        "min_data_in_leaf": 5,
        "feature_fraction": 0.9,
        "verbosity": -1,
        "label_gain": list(range(5)),
    }
    if params:
        default_params.update(params)

    train_set = lgb.Dataset(
        X, label=y, group=group, feature_name=FEATURE_NAMES, free_raw_data=False
    )
    model = lgb.train(default_params, train_set, num_boost_round=120)
    return model


def save_ltr(model: lgb.Booster, path: Path = LTR_MODEL_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    model.save_model(str(path))


def load_ltr(path: Path = LTR_MODEL_PATH) -> lgb.Booster:
    return lgb.Booster(model_file=str(path))


def predict_ltr(model: lgb.Booster, X: np.ndarray) -> np.ndarray:
    return model.predict(X)
