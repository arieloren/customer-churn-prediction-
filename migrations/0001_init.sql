CREATE TABLE IF NOT EXISTS churn_input_data (
    customerID      text,
    tenure          numeric,
    "TotalCharges"  numeric,
    "Contract"      text,
    "PhoneService"  text
);

CREATE TABLE IF NOT EXISTS churn_predictions (
    id          serial PRIMARY KEY,
    customer_id text,
    churn       boolean,
    probability numeric,
    created_at  timestamp default now()
);
