import pandas as pd
from src.common.db import get_conn
from src.common.preprocessing import DataPreprocessor
from src.common.model_loader import TransformModel
from config.config_loader import Config


def fetch_input_data():
    """Fetch data from Postgres that needs predictions."""
    query = """
        SELECT customerID, tenure, "TotalCharges", "Contract", "PhoneService"
        FROM churn_input_data;
    """
    with get_conn() as conn:
        return pd.read_sql_query(query, conn)


def insert_predictions(df: pd.DataFrame):
    """Insert predictions into churn_predictions table."""
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.executemany(
                """
                INSERT INTO churn_predictions (customer_id, churn, probability)
                VALUES (%s, %s, %s)
                """,
                df[["customerID", "Prediction", "probability"]].values.tolist()
            )
    print("✅ Predictions saved to Postgres (churn_predictions)")


def main():
    config = Config()

    # 1. Load data from DB
    raw_data = fetch_input_data()

    # 2. Preprocess
    preprocessor = DataPreprocessor(config)
    preprocessor.fit(raw_data)
    processed_data = preprocessor.transform(raw_data)

    # 3. Predict
    model = TransformModel(config)
    predictions = model.predict(processed_data)
    probabilities = model.predict_proba(processed_data)[:, 1]

    # 4. Prepare output and write to DB
    raw_data['Prediction'] = predictions
    raw_data['probability'] = probabilities
    insert_predictions(raw_data)


if __name__ == "__main__":
    main()
