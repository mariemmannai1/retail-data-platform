"""Évaluation de la prévision des ventes sur plusieurs périodes (validation glissante).

Ce script n'écrit rien dans DuckDB : il affiche les résultats et écrit des CSV dans data/analysis/.
Les modèles et la méthode sont dans forecast_lib.py.
"""
from forecast_lib import (
      HORIZON,
      MEAN_MODEL,
      MIN_TRAIN_DAYS,
      load_series,
      project_dir,
      rolling_evaluation,
)

out_dir = project_dir / "data" / "analysis"
out_dir.mkdir(parents=True, exist_ok=True)

series = load_series()
res, summary, n_origins = rolling_evaluation(series)

res.to_csv(out_dir / "forecast_evaluation_details.csv", index=False)
summary.to_csv(out_dir / "forecast_evaluation_summary.csv", index=False)

print("EVALUATION GLISSANTE DE LA PREVISION DES VENTES")
print("=" * 60)
print(f"Origines : {n_origins} | entraînement minimal : {MIN_TRAIN_DAYS} jours | horizon : {HORIZON} jours | "
      f"jours évalués par modèle : {len(res[res['model'] == MEAN_MODEL])}")
print(f"Vente quotidienne moyenne : {series.mean():.2f}\n")
print(summary.to_string(index=False))
print("\n(beats_lag7_pct / beats_mean_pct : part des origines où le modèle a une erreur plus faible que la référence)")

by_horizon = res.pivot_table(index="horizon", columns="model", values="abs_error", aggfunc="mean").round(2)
print("\nMAE selon le jour de prévision (1 = lendemain, 7 = septième jour)")
print(by_horizon[[MEAN_MODEL, "Random Forest (variables du projet)"]].to_string())
by_horizon.to_csv(out_dir / "forecast_evaluation_by_horizon.csv")
print(f"\nFichiers enregistrés dans : {out_dir}")
