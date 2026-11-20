
import json
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_FILE = BASE_DIR / "data" / "records.json"


def explore_records():
    with open(DATA_FILE, "r", encoding="utf-8") as file:
        records = json.load(file)

    df = pd.DataFrame(records)

    print("\n--- JALSANCHAY DATA EXPLORATION ---")

    print("\n1. Total technical records:", len(df))

    print("\n2. Records by topic:")
    print(df["topic"].value_counts().to_string())

    print("\n3. Records by document:")
    print(df["document"].value_counts().to_string())


if __name__ == "__main__":
    explore_records()
