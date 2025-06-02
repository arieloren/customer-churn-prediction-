import pandas as pd
from src.common.preprocessing import DataPreprocessor

def test_clean_total_charges_handles_spaces(cfg):
    df = pd.DataFrame({
        "TotalCharges": ["  "],
        "tenure": [10],
        "Contract": ["One year"],
        "PhoneService": ["Yes"]
    })
    prep = DataPreprocessor(cfg).fit(df)
    out  = prep.transform(df)
    assert out["TotalCharges"].iloc[0] == 2279.0      # default fill value

def test_missing_contract_raises_error(cfg):
    df = pd.DataFrame({
        "TotalCharges": ["100.0"],
        "tenure": [10],
        "Contract": [None],
        "PhoneService": ["Yes"]
    })
    prep = DataPreprocessor(cfg).fit(df)
    
    try:
        prep.transform(df)
        assert False  # should not reach here
    except ValueError as e:
        assert str(e) == "Contract cannot be null - model will not predict"

def test_null_phone_service_is_filled(cfg):
    df = pd.DataFrame({
        "TotalCharges": ["100.0"],
        "tenure": [5],
        "Contract": ["Month-to-month"],
        "PhoneService": [None]
    })
    prep = DataPreprocessor(cfg).fit(df)
    out = prep.transform(df)
    assert out["PhoneService"].iloc[0] == 0
