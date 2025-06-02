import pytest
import json
from config.config_loader import Config
from src.api.api_main import app as flask_app   

@pytest.fixture(scope="session")
def cfg():
    return Config() # Loads config.yaml once and reuses it in all tests

@pytest.fixture(scope="session")
def client():
    flask_app.config["TESTING"] = True
    return flask_app.test_client() # A fake client to test the API without running the real server
