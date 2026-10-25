"""Fonctions communes de prévision : série quotidienne, modèles et validation glissante.

Utilisé par evaluate_forecast.py et forecast_champion.py.
À chaque origine, chaque modèle est entraîné uniquement sur le passé, puis prévoit les 7 jours
suivants en enchaînant ses propres prévisions, comme dans la prévision réellement livrée.
"""
import warnings
from pathlib import Path

import duckdb
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor

# Avertissement sans conséquence émis par certaines versions de scikit-learn / joblib
warnings.filterwarnings("ignore", message=r".*sklearn\.utils\.parallel\.delayed.*", category=UserWarning)

project_dir = Path(__file__).resolve().parent.parent
db_path = project_dir / "retail.duckdb"

HORIZON = 7
MIN_TRAIN_DAYS = 180
STEP_DAYS = 7
FEATURES_PROJECT = ["day_of_week", "month", "day_of_year", "lag_1", "lag_7", "rolling_mean_7"]
FEATURES_NO_CALENDAR = ["day_of_week", "lag_1", "lag_7", "rolling_mean_7"]

MEAN_MODEL = "Moyenne de l'historique"
WEEKDAY_MODEL = "Moyenne par jour de semaine"
BASELINE = "lag_7 (baseline du projet)"
RF_PROJECT = "Random Forest (variables du projet)"
RF_NO_CALENDAR = "Random Forest (sans mois ni jour de l'année)"


def load_series():
    """Ventes quotidiennes (commandes Completed, tous canaux), sans jour manquant."""
    with duckdb.connect(str(db_path), read_only=True) as con:
        df = con.execute("""
            SELECT order_date, SUM(total_revenue) AS revenue
            FROM daily_sales GROUP BY order_date ORDER BY order_date
        """).fetchdf()
    df["order_date"] = pd.to_datetime(df["order_date"])
    series = df.set_index("order_date")["revenue"].asfreq("D")
    if series.isna().any():
        raise ValueError("Des jours sans ventes doivent être traités avant la prévision.")
    return series


def predict_mean(history, dates):
    return [float(history.mean())] * len(dates)


def predict_weekday_mean(history, dates):
    by_day = history.groupby(history.index.dayofweek).mean()
    return [float(by_day[d.dayofweek]) for d in dates]


def predict_lag_7(history, dates):
    hist = history.copy()
    predictions = []
    for date in dates:
        value = float(hist.iloc[-7])
        predictions.append(value)
        hist.loc[date] = value
    return predictions


def _make_row(hist, date):
    return {
        "day_of_week": date.dayofweek, "month": date.month, "day_of_year": date.dayofyear,
        "lag_1": hist.iloc[-1], "lag_7": hist.iloc[-7], "rolling_mean_7": hist.iloc[-7:].mean(),
    }


def predict_random_forest(history, dates, features):
    table = pd.DataFrame({"y": history})
    table["day_of_week"] = history.index.dayofweek
    table["month"] = history.index.month
    table["day_of_year"] = history.index.dayofyear
    table["lag_1"] = history.shift(1)
    table["lag_7"] = history.shift(7)
    table["rolling_mean_7"] = history.shift(1).rolling(7).mean()
    table = table.dropna()
    model = RandomForestRegressor(n_estimators=300, max_depth=8, min_samples_leaf=3,
                                  random_state=42, n_jobs=1)
    model.fit(table[features], table["y"])
    hist = history.copy()
    predictions = []
    for date in dates:
        row = pd.DataFrame([_make_row(hist, date)])[features]
        value = max(0.0, float(model.predict(row)[0]))
        predictions.append(value)
        hist.loc[date] = value
    return predictions


MODELS = {
    MEAN_MODEL: predict_mean,
    WEEKDAY_MODEL: predict_weekday_mean,
    BASELINE: predict_lag_7,
    RF_PROJECT: lambda h, d: predict_random_forest(h, d, FEATURES_PROJECT),
    RF_NO_CALENDAR: lambda h, d: predict_random_forest(h, d, FEATURES_NO_CALENDAR),
}


def rolling_evaluation(series):
    """Retourne (détails par jour prévu, synthèse par modèle triée par MAE, nombre d'origines)."""
    origins = list(range(MIN_TRAIN_DAYS, len(series) - HORIZON + 1, STEP_DAYS))
    records = []
    for origin in origins:
        train = series.iloc[:origin]
        actual = series.iloc[origin:origin + HORIZON]
        for name, predict in MODELS.items():
            predicted = predict(train, list(actual.index))
            for h, (date, y, yhat) in enumerate(zip(actual.index, actual.values, predicted), start=1):
                records.append({"origin": origin, "model": name, "horizon": h, "date": date,
                                "actual": y, "predicted": yhat})
    res = pd.DataFrame(records)
    res["abs_error"] = (res["actual"] - res["predicted"]).abs()
    res["sq_error"] = (res["actual"] - res["predicted"]) ** 2

    per_origin = res.groupby(["model", "origin"])["abs_error"].mean().unstack(0)
    rows = []
    for name in MODELS:
        sub = res[res["model"] == name]
        rows.append({
            "model": name,
            "mae": round(sub["abs_error"].mean(), 2),
            "rmse": round(float(np.sqrt(sub["sq_error"].mean())), 2),
            "wape_pct": round(100 * sub["abs_error"].sum() / sub["actual"].sum(), 1),
            "beats_lag7_pct": round(100 * (per_origin[name] < per_origin[BASELINE]).mean(), 0),
            "beats_mean_pct": round(100 * (per_origin[name] < per_origin[MEAN_MODEL]).mean(), 0),
        })
    summary = pd.DataFrame(rows).sort_values("mae").reset_index(drop=True)
    return res, summary, len(origins)
