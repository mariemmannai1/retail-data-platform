"""Configuration pytest : se place à la racine du projet et ouvre retail.duckdb en lecture seule."""
import os
from pathlib import Path

import duckdb
import pytest

PROJECT_DIR = Path(__file__).resolve().parent.parent
os.chdir(PROJECT_DIR)  # les requêtes utilisent des chemins relatifs data/raw/...


@pytest.fixture(scope="session")
def con():
    db_path = PROJECT_DIR / "retail.duckdb"
    assert db_path.exists(), f"Base introuvable : {db_path}. Lancer le pipeline d'abord."
    connection = duckdb.connect(str(db_path), read_only=True)
    yield connection
    connection.close()


def scalar(con, sql):
    return con.execute(sql).fetchone()[0]
