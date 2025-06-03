"""
Batch prediction job.

• Reads all records from churn_input_data
• Generates churn / probability with the trained model
• Inserts results into churn_predictions
• Exposes metrics via Pushgateway so Prometheus / Grafana can track the run
"""

import os
import sys
import time
import pandas as pd
from prometheus_client import (
    CollectorRegistry, Gauge, Histogram, push_to_gateway,
)

from src.common.db import get_conn
from src.common.preprocessing import DataPreprocessor
from src.common.model_loader import TransformModel
from config.config_loader import Config

# ---------------------------------------------------------------------
# Prometheus metric definitions (in a private registry)
# ---------------------------------------------------------------------
REGISTRY       = CollectorRegistry()
ROWS_READ      = Gauge(
    "batch_rows_read_total",
    "Number of rows fetched from churn_input_data",
    registry=REGISTRY,
)
ROWS_INSERTED  = Gauge(
    "batch_rows_inserted_total",
    "Number of rows written to churn_predictions",
    registry=REGISTRY,
)
JOB_DURATION   = Histogram(
    "batch_job_seconds",
    "Total batch-run wall-time in seconds",
    registry=REGISTRY,
)


# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------
def fetch_input_data() -> pd.DataFrame:
    """Pull raw feature rows that need scoring."""
    query = """
        SELECT customerID, tenure, "TotalCharges", "Contract", "PhoneService"
        FROM churn_input_data;
    """
    with get_conn() as conn:
        return pd.read_sql_query(query, conn)


def insert_predictions(df: pd.DataFrame) -> None:
    """Bulk-insert results into churn_predictions."""
    if df.empty:
        return
    with get_conn() as conn, conn.cursor() as cur:
        cur.executemany(
            """
            INSERT INTO churn_predictions (customer_id, churn, probability)
            VALUES (%s, %s, %s)
            """,
            df[["customerID", "Prediction", "probability"]].values.tolist(),
        )


# ---------------------------------------------------------------------
# Main workflow
# ---------------------------------------------------------------------
@JOB_DURATION.time()          # record total run-time
def main() -> None:
    config = Config()

    # 1️⃣ Fetch
    raw = fetch_input_data()
    ROWS_READ.set(len(raw))

    if raw.empty:
        print("ℹ️  No new rows – nothing to predict today")
        push_metrics()
        sys.exit(0)

    # 2️⃣ Pre-process
    pre = DataPreprocessor(config)
    pre.fit(raw)
    processed = pre.transform(raw)

    # 3️⃣ Predict
    model        = TransformModel(config)
    raw["Prediction"]  = model.predict(processed)
    raw["probability"] = model.predict_proba(processed)[:, 1]

    # 4️⃣ Insert
    insert_predictions(raw)
    ROWS_INSERTED.set(len(raw))
    print(f"✅ Inserted {len(raw)} rows into churn_predictions")

    # 5️⃣ Push metrics
    push_metrics()


def push_metrics() -> None:
    """
    Send the custom registry to Pushgateway.
    Default URL is 'pushgateway:9091', override with env PUSHGATEWAY_URL.
    """
    gw = os.getenv("PUSHGATEWAY_URL", "pushgateway:9091")
    try:
        push_to_gateway(gw, job="batch-runner", registry=REGISTRY)
        print(f"📊 Metrics pushed to {gw}")
    except Exception as exc:
        # Never crash the batch because of metrics
        print(f"⚠️  Failed to push metrics: {exc}")


if __name__ == "__main__":
    main()