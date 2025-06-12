"""
Load every data/*input*.csv into churn_input_data.

Run inside any service that has psycopg2 + pandas:
$ docker compose run --rm batch-runner python -m src.tools.load_csv_to_db
"""
import glob, os
import pandas as pd
from io import StringIO
from src.common.db import get_conn


def copy_df(cur, df):
    buf = StringIO()
    # ➊  blanks → NaN, convert to numeric
    df["TotalCharges"] = (
        pd.to_numeric(df["TotalCharges"], errors="coerce")  # blanks → NaN
    )
    df.to_csv(buf, index=False, header=False)
    buf.seek(0)
    cur.copy_expert(
        """
        COPY churn_input_data (customerID, tenure, "TotalCharges",
                            "Contract", "PhoneService")
        FROM STDIN WITH (FORMAT csv)
        """,
        file=buf,
    )


pattern = os.path.join("data", "*input*.csv")
files = sorted(glob.glob(pattern))

print(f"Loading {len(files)} CSV file(s)…")

with get_conn() as conn, conn.cursor() as cur:
    for f in files:
        df = pd.read_csv(f)
        needed = ["customerID", "tenure", "TotalCharges", "Contract", "PhoneService"]
        df = df[needed]          # keep the 5 columns and in the right order
        copy_df(cur, df)
        print(f"  ✔ {os.path.basename(f):<25} {len(df):>6} rows")

print("All done – data available in churn_input_data")
