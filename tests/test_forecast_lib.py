
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from forecast_lib import (
    FEATURES_PROJECT,
    predict_lag_7,
    predict_mean,
    predict_random_forest,
)


def test_predict_mean_returns_history_average():
    history = pd.Series([10, 20, 30])
    dates = pd.date_range("2026-01-01", periods=2)

    predictions = predict_mean(history, dates)

    assert predictions == [20.0, 20.0]


def test_predict_lag_7_repeats_values_from_previous_week():
    history = pd.Series(
        [10, 20, 30, 40, 50, 60, 70],
        index=pd.date_range("2026-01-01", periods=7),
    )
    dates = pd.date_range("2026-01-08", periods=7)

    predictions = predict_lag_7(history, dates)

    assert predictions == [10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0]


def test_random_forest_returns_seven_non_negative_predictions():
    dates_history = pd.date_range("2025-01-01", periods=220)
    history = pd.Series(
        100 + 20 * np.sin(np.arange(220) * 2 * np.pi / 7),
        index=dates_history,
    )
    future_dates = pd.date_range("2025-08-09", periods=7)

    predictions = predict_random_forest(
        history, future_dates, FEATURES_PROJECT
    )

    assert len(predictions) == 7
    assert all(np.isfinite(value) and value >= 0 for value in predictions)
