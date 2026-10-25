"""Tests des tables produites par forecast_champion.py (ignorés si le script n'a pas été lancé)."""
import pytest
from conftest import scalar


def _tables(con):
    return {row[0] for row in con.execute("SHOW TABLES").fetchall()}


def test_forecast_sales_champion(con):
    if "forecast_sales_champion" not in _tables(con):
        pytest.skip("forecast_champion.py n'a pas encore été lancé")
    rows = con.execute("SELECT forecast_date, forecast_revenue FROM forecast_sales_champion ORDER BY 1").fetchall()
    assert len(rows) == 7
    assert str(rows[0][0]) == "2026-01-01" and str(rows[-1][0]) == "2026-01-07"
    assert all(value is not None and value >= 0 for _, value in rows)
    assert scalar(con, "SELECT COUNT(DISTINCT model_name) FROM forecast_sales_champion") == 1


def test_forecast_model_evaluation_has_one_champion_with_lowest_mae(con):
    if "forecast_model_evaluation" not in _tables(con):
        pytest.skip("forecast_champion.py n'a pas encore été lancé")
    assert scalar(con, "SELECT COUNT(*) FROM forecast_model_evaluation WHERE is_champion") == 1
    champion_mae = scalar(con, "SELECT mae FROM forecast_model_evaluation WHERE is_champion")
    assert champion_mae == scalar(con, "SELECT MIN(mae) FROM forecast_model_evaluation")
    champion = scalar(con, "SELECT model_name FROM forecast_model_evaluation WHERE is_champion")
    assert champion == scalar(con, "SELECT DISTINCT model_name FROM forecast_sales_champion")
