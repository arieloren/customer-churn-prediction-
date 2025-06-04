from flask import Flask, request, jsonify
from marshmallow import ValidationError
import pandas as pd

from src.api.request_schema import CustomerChurnRequestSchema
from src.common.preprocessing import DataPreprocessor
from src.common.model_loader import TransformModel
from src.common.db import get_conn
from config.config_loader import Config

# ────────────────────  Prometheus  ────────────────────
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

REQUEST_COUNT = Counter(
    "api_requests_total",
    "Total prediction requests",
    ["endpoint", "http_status"],
)

PREDICT_LATENCY = Histogram(
    "api_predict_seconds",
    "Time spent in /predict handler",
)
# ───────────────────────────────────────────────────────

app = Flask(__name__)
config = Config()

schema       = CustomerChurnRequestSchema()
preprocessor = DataPreprocessor(config)
model        = TransformModel(config)


# Prometheus scrape target
@app.route("/metrics")
def metrics():
    return generate_latest(), 200, {"Content-Type": CONTENT_TYPE_LATEST}


# Main prediction endpoint
@app.route("/predict", methods=["POST"])
@PREDICT_LATENCY.time()
def predict():
    # 1️⃣  Validate JSON
    try:
        req_json       = request.get_json()
        validated_data = schema.load(req_json)
    except ValidationError as err:
        REQUEST_COUNT.labels("/predict", "400").inc()
        return jsonify({"error": err.messages}), 400

    # 2️⃣  Pre-process & inference  – any error here is a real 500
    try:
        df         = pd.DataFrame([validated_data])
        preprocessor.fit(df)
        processed  = preprocessor.transform(df)

        prob       = model.predict_proba(processed)[0, 1]
        prediction = int(prob >= config.get_threshold())

        # 3️⃣  Best-effort DB insert
        try:
            with get_conn() as conn, conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO churn_predictions (customer_id, churn, probability)
                    VALUES (%s,%s,%s)
                    """,
                    (validated_data["customerID"], prediction, round(prob, 3)),
                )
        except Exception as db_err:
            app.logger.warning("DB insert failed: %s", db_err)

    except Exception as e:
        REQUEST_COUNT.labels("/predict", "500").inc()
        return jsonify({"error": f"internal error: {e}"}), 500

    # 4️⃣  Success
    REQUEST_COUNT.labels("/predict", "200").inc()
    return jsonify({"prediction": prediction, "probability": round(prob, 3)}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=9999, debug=True)
