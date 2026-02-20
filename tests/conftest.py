import pytest
from unittest.mock import MagicMock, patch
import numpy as np

@pytest.fixture(autouse=True)
def mock_model(monkeypatch):
    mock = MagicMock()
    mock.predict.return_value = [0]
    mock.predict_proba.return_value = [[0.6, 0.4]]
    monkeypatch.setattr("api.main.model", mock)
    monkeypatch.setattr("api.main.feature_names", [
        'age', 'revenu_mensuel', 'nombre_experiences_precedentes'
    ])