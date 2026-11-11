"""Small helpers for values loaded from parquet / numpy."""

from __future__ import annotations

from typing import Any


def as_list(value: Any) -> list:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    try:
        import numpy as np

        if isinstance(value, np.ndarray):
            return value.tolist()
    except ImportError:
        pass
    try:
        import pandas as pd

        if isinstance(value, float) and pd.isna(value):
            return []
    except Exception:  # noqa: BLE001
        pass
    if isinstance(value, (str, bytes)):
        return [value]
    if hasattr(value, "__iter__"):
        return list(value)
    return [value]
