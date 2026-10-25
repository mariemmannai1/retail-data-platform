"""Prévision à 7 jours avec le modèle retenu par validation glissante.

1. Évalue les modèles candidats sur plusieurs périodes (forecast_lib.rolling_evaluation).
2. Retient le modèle dont le MAE est le plus faible (le « champion »).
3. Réentraîne le champion sur tout l'historique et prévoit les 7 jours suivants.
4. Contrôle les prévisions, puis écrit deux NOUVELLES tables dans DuckDB :
   - forecast_model_evaluation : métriques de chaque modèle, avec le champion marqué ;
   - forecast_sales_champion : les 7 prévisions du champion.
Les tables existantes (forecast_sales, forecast_model_metrics) ne sont pas modifiées.
"""
import sys

import duckdb
import pandas as pd

from forecast_lib import (
    HORIZON,
    MODELS,
    db_path,
    load_series,
    project_dir,
    rolling_evaluation,
)

out_dir = project_dir / "data" / "analysis"
out_dir.mkdir(parents=True, exist_ok=True)

series = load_series()
res, summary, n_origins = rolling_evaluation(series)

champion = summary.loc[0, "model"]
summary["n_origins"] = n_origins
summary["horizon_days"] = HORIZON
summary["is_champion"] = summary["model"] == champion

print("EVALUATION GLISSANTE ET CHOIX DU MODELE")
print("=" * 60)
print(f"Origines : {n_origins} | horizon : {HORIZON} jours")
print(summary[["model", "mae", "rmse", "wape_pct", "is_champion"]].to_string(index=False))
print(f"\nModèle retenu (MAE le plus faible) : {champion}")

# Prévision des 7 jours suivant la dernière date connue
last_date = series.index[-1]
future_dates = [last_date + pd.Timedelta(days=i) for i in range(1, HORIZON + 1)]
values = MODELS[champion](series, future_dates)
forecast = pd.DataFrame({
    "forecast_date": [d.date() for d in future_dates],
    "forecast_revenue": [round(v, 2) for v in values],
    "model_name": champion,
})
print("\nPREVISION DES VENTES SUR 7 JOURS (modèle retenu)")
print(forecast.to_string(index=False))

# Contrôles AVANT toute écriture dans la base
errors = []
if len(forecast) != HORIZON:
    errors.append(f"nombre de prévisions : {len(forecast)} au lieu de {HORIZON}")
if forecast["forecast_revenue"].isna().any():
    errors.append("valeurs manquantes")
if (forecast["forecast_revenue"] < 0).any():
    errors.append("prévisions négatives")
if forecast["forecast_date"].iloc[0] != (last_date + pd.Timedelta(days=1)).date():
    errors.append("la première date n'est pas le lendemain de la dernière date connue")
if int(summary["is_champion"].sum()) != 1:
    errors.append("il doit y avoir exactement un modèle retenu")
if errors:
    print("\nECHEC : " + " ; ".join(errors))
    sys.exit(1)

# Écriture dans DuckDB (nouvelles tables uniquement)
run_ts = pd.Timestamp.now().floor("s").to_pydatetime()
forecast["run_ts"] = run_ts
summary["run_ts"] = run_ts
with duckdb.connect(str(db_path)) as con:
    con.register("forecast_df", forecast)
    con.register("summary_df", summary)
    con.execute("CREATE OR REPLACE TABLE forecast_sales_champion AS "
                "SELECT CAST(forecast_date AS DATE) AS forecast_date, forecast_revenue, model_name, run_ts FROM forecast_df")
    con.execute("CREATE OR REPLACE TABLE forecast_model_evaluation AS "
                "SELECT model AS model_name, mae, rmse, wape_pct, beats_lag7_pct, beats_mean_pct, "
                "n_origins, horizon_days, is_champion, run_ts FROM summary_df")
    n_forecast = con.execute("SELECT COUNT(*) FROM forecast_sales_champion").fetchone()[0]
    n_models = con.execute("SELECT COUNT(*) FROM forecast_model_evaluation").fetchone()[0]

forecast.to_csv(out_dir / "forecast_champion_7days.csv", index=False)
summary.to_csv(out_dir / "forecast_model_evaluation.csv", index=False)
print(f"\nforecast_sales_champion : {n_forecast} lignes | forecast_model_evaluation : {n_models} lignes")
print("Les tables forecast_sales et forecast_model_metrics ne sont pas modifiées par ce script.")
print("\nPrévision terminée avec succès.")
