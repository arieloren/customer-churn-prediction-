import pandas as pd
import os
from src.common.db import get_conn  # assuming this file exists now

class ExtractFile():
    def __init__(self, file_path):
        self.file_path = file_path

    def load_data(self):
        return pd.read_csv(self.file_path)


class ExtractFromDB():
    def __init__(self, query="SELECT customer_id, tenure, TotalCharges, Contract, PhoneService FROM input_data"):
        self.query = query

    def load_data(self):
        with get_conn() as conn:
            return pd.read_sql_query(self.query, conn)
