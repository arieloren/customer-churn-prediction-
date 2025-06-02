import pandas as pd
from src.common.model_loader import TransformModel
from src.common.preprocessing import DataPreprocessor

def test_model_predict_shape(cfg):
    df = pd.DataFrame({
        "TotalCharges": ["108.5"],
        "tenure": [5],
        "Contract": ["Month-to-month"],
        "PhoneService": ["Yes"]
    })
    prep   = DataPreprocessor(cfg).fit(df)
    model  = TransformModel(cfg)
    X      = prep.transform(df)
    preds  = model.predict(X)
    assert len(preds) == 1
    assert preds[0] in [0, 1]
