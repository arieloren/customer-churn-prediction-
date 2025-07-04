import pandas as pd
import pickle
from config.config_loader import Config
import logging
import numpy as np 
class DataPreprocessor:
    def __init__(self, config: Config):
        self.config = config
        self.tenure_mean = None
        self.__load_dependency()
        
    def __validation(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Drop rows that contain *no information whatsoever*:
        every cell is either NaN or an empty-string/blank.
        """
        def _blank_to_nan(x):
            if isinstance(x, str) and x.strip() == "":
                return np.nan
            return x

        cleaned   = df.applymap(_blank_to_nan)
        empty_mask = cleaned.isna().all(axis=1)   # True ⇢ row has 0 signals

        if empty_mask.any():
            logging.warning(f"❌ Skipping {empty_mask.sum()} completely empty row(s).")

        return df.loc[~empty_mask].copy()


    def __load_dependency(self):

        # Load dummy column structure for Contract
        with open(self.config.get_dummy_columns_path(), 'rb') as f:
            self.dummy_columns = pickle.load(f)
        
    def fit(self, dataset):
        self.tenure_mean = dataset['tenure'].mean()
        return self
    
    def clean_total_charges(self, data):
        data['TotalCharges'] = data['TotalCharges'].fillna(2279)
        
        # ✅ Ensure string type before using .str methods
        data['TotalCharges'] = data['TotalCharges'].astype(str).replace(r'^\s*$', '2279', regex=True)

        # ✅ Convert back to float after cleaning
        data['TotalCharges'] = data['TotalCharges'].astype(float)
        
        return data
    
    def transform(self, dataset):
        data = dataset.copy()
        # Validation pre-clean
        data = self.__validation(data)
        # Nulls:
        data = self.clean_total_charges(data)  
        # Contract validation
        if data['Contract'].isnull().any():
            raise ValueError("Contract cannot be null - model will not predict")
        
        data['PhoneService'] = data['PhoneService'].fillna('No')
        data['tenure'] = data['tenure'].fillna(self.tenure_mean)
        
        # Feature handling:
        data['PhoneService'] = data['PhoneService'].map({'Yes':1,'No':0})
        # One-hot encode 'Contract'
        contract_dummies = pd.get_dummies(data['Contract']).astype(int)

        # Ensure all expected dummy columns exist
        for col in self.dummy_columns:
            if col not in contract_dummies:
                contract_dummies[col] = 0

        # Order columns and join
        contract_dummies = contract_dummies[self.dummy_columns]
        data = data.join(contract_dummies)

        # Return only model input columns
        return data[self.config.get_model_columns()]
        
    def fit_transform(self, dataset):
        return self.fit(dataset).transform(dataset)
