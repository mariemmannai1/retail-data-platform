
from pathlib import Path
import pandas as pd

DATA_DIR = Path("data/raw")

for file_path in sorted(DATA_DIR.glob("*.csv")):
    print("\n" + "=" * 60)
    print(f"FICHIER : {file_path.name}")

    df = pd.read_csv(file_path)

    print(f"Nombre de lignes : {len(df)}")
    print(f"Nombre de colonnes : {len(df.columns)}")
    print("Colonnes :", list(df.columns))
    print("\nAperçu :")
    print(df.head(3).to_string(index=False))
