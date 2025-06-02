import yaml
import os

class Config:
    def __init__(self, path="config/config.yaml"):
        with open(path, 'r') as f:
            self.cfg = yaml.safe_load(f)
        self.base_path = os.path.dirname(os.path.abspath(path))

    def __getitem__(self, key):
        return self.cfg[key]

    def get_model_path(self):
        return os.path.join(self.base_path, '..', self.cfg['model']['path'])

    def get_dummy_columns_path(self):
        return os.path.join(self.base_path, '..', self.cfg['preprocessing']['dummy_contract_columns'])

    def get_model_columns(self):
        return self.cfg['model']['columns']

    def get_threshold(self):
        return self.cfg['model']['threshold']
