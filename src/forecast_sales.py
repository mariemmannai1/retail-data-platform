
from pathlib import Path

import duckdb
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error
import os   # avec les imports

DB_PATH = PROJECT_DIR / os.getenv("RETAIL_DB_NAME", "retail.duckdb")
PROJECT_DIR = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_DIR / "retail.duckdb"

# 1. Charger les ventes quotidiennes
with duckdb.connect(str(DB_PATH), read_only=True) as con:
    df = con.execute("""
        SELECT
            order_date,
            SUM(total_revenue) AS revenue
        FROM daily_sales
        GROUP BY order_date
        ORDER BY order_date
    """).fetchdf()

df["order_date"] = pd.to_datetime(df["order_date"])
df = df.set_index("order_date").asfreq("D")

if df["revenue"].isna().any():
    raise ValueError("Des jours sans ventes doivent être traités avant l'entraînement.")

# 2. Créer les variables explicatives
df["day_of_week"] = df.index.dayofweek
df["month"] = df.index.month
df["day_of_year"] = df.index.dayofyear
df["lag_1"] = df["revenue"].shift(1)
df["lag_7"] = df["revenue"].shift(7)
df["rolling_mean_7"] = df["revenue"].shift(1).rolling(7).mean()

features = [
    "day_of_week",
    "month",
    "day_of_year",
    "lag_1",
    "lag_7",
    "rolling_mean_7",
]

data = df.dropna(subset=features + ["revenue"]).copy()

# 3. Séparer chronologiquement : pas de mélange aléatoire
split_date = pd.Timestamp("2025-12-01")
train = data[data.index < split_date]
test = data[data.index >= split_date]

X_train, y_train = train[features], train["revenue"]
X_test, y_test = test[features], test["revenue"]

# 4. Entraîner le modèle
model = RandomForestRegressor(
    n_estimators=300,
    max_depth=8,
    min_samples_leaf=3,
    random_state=42,
    n_jobs=-1,
)
model.fit(X_train, y_train)

predictions = model.predict(X_test)

# 5. Évaluer le modèle et la référence lag_7
mae = mean_absolute_error(y_test, predictions)
rmse = np.sqrt(mean_squared_error(y_test, predictions))
baseline_mae = mean_absolute_error(y_test, test["lag_7"])

print("EVALUATION DU MODELE")
print("=" * 40)
print(f"Jours d'entraînement : {len(train)}")
print(f"Jours de test : {len(test)}")
print(f"MAE Random Forest : {mae:.2f}")
print(f"RMSE Random Forest : {rmse:.2f}")
print(f"MAE référence lag_7 : {baseline_mae:.2f}")

# 6. Réentraîner sur tout l'historique disponible
model.fit(data[features], data["revenue"])

# 7. Prévoir les 7 jours suivant la dernière date connue
history = df["revenue"].copy()
future_rows = []

for _ in range(7):
    next_date = history.index[-1] + pd.Timedelta(days=1)

    row = pd.DataFrame([{
        "day_of_week": next_date.dayofweek,
        "month": next_date.month,
        "day_of_year": next_date.dayofyear,
        "lag_1": history.iloc[-1],
        "lag_7": history.iloc[-7],
        "rolling_mean_7": history.iloc[-7:].mean(),
    }], index=[next_date])

    forecast = max(0, float(model.predict(row[features])[0]))
    future_rows.append({
        "date": next_date.date(),
        "forecast_revenue": round(forecast, 2),
    })

    history.loc[next_date] = forecast

forecast_df = pd.DataFrame(future_rows)

print("\nPREVISION DES VENTES SUR 7 JOURS")
print("=" * 40)
print(forecast_df.to_string(index=False))

output_path = PROJECT_DIR / "data" / "sales_forecast_7days.csv"
forecast_df.to_csv(output_path, index=False)
print(f"\nPrévisions enregistrées dans : {output_path}")
# 8. Enregistrer les métriques du modèle
metrics_df = pd.DataFrame([{
    "model_name": "Random Forest",
    "training_days": len(train),
    "test_days": len(test),
    "mae": round(float(mae), 2),
    "rmse": round(float(rmse), 2),
    "baseline_lag7_mae": round(float(baseline_mae), 2),
}])

metrics_path = PROJECT_DIR / "data" / "forecast_metrics.csv"
metrics_df.to_csv(metrics_path, index=False)

print(f"Métriques enregistrées dans : {metrics_path}")
print(metrics_df.to_string(index=False))
