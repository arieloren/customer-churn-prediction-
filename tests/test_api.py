def test_api_predict_success(client):
    payload = {
        "customerID": "0001",
        "tenure": 5,
        "TotalCharges": "108.5",
        "Contract": "Month-to-month",
        "PhoneService": "Yes"
    }
    res = client.post("/predict", json=payload)
    assert res.status_code == 200
    data = res.get_json()
    assert "prediction" in data and "probability" in data
    assert data["prediction"] in [0, 1]
    assert 0.0 <= data["probability"] <= 1.0
