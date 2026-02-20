import pytest
from fastapi.testclient import TestClient
import sys
sys.path.append(".")
from api.main import app

client = TestClient(app)

API_KEY = "ma_cle_secrete_futurisys"
HEADERS = {"X-API-Key": API_KEY}

VALID_INPUT = {
    "age": 35,
    "revenu_mensuel": 5000.0,
    "heure_supplementaires": "Oui",
    "satisfaction_employee_environnement": 2,
    "frequence_deplacement": "Frequent"
}

# ── Tests endpoint GET ──────────────────────────────────────────

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

# ── Tests endpoint POST /predict ────────────────────────────────

def test_predict_valid_input():
    response = client.post("/predict", json=VALID_INPUT, headers=HEADERS)
    assert response.status_code == 200
    data = response.json()
    assert "prediction" in data
    assert "label" in data
    assert "probabilite_depart" in data
    assert data["prediction"] in [0, 1]
    assert 0.0 <= data["probabilite_depart"] <= 1.0

def test_predict_without_api_key():
    response = client.post("/predict", json=VALID_INPUT)
    assert response.status_code == 401

def test_predict_invalid_api_key():
    response = client.post("/predict", json=VALID_INPUT, headers={"X-API-Key": "mauvaise_cle"})
    assert response.status_code == 403

def test_predict_missing_required_field():
    invalid_input = {"age": 35}  # manque revenu_mensuel etc.
    response = client.post("/predict", json=invalid_input, headers=HEADERS)
    assert response.status_code == 422

def test_predict_invalid_satisfaction_value():
    invalid_input = {**VALID_INPUT, "satisfaction_employee_environnement": 10}  # max = 4
    response = client.post("/predict", json=invalid_input, headers=HEADERS)
    assert response.status_code == 422

def test_predict_invalid_heure_supplementaires():
    invalid_input = {**VALID_INPUT, "heure_supplementaires": "Maybe"}
    response = client.post("/predict", json=invalid_input, headers=HEADERS)
    assert response.status_code == 422

def test_predict_label_coherent():
    response = client.post("/predict", json=VALID_INPUT, headers=HEADERS)
    data = response.json()
    if data["prediction"] == 1:
        assert data["label"] == "Risque de départ"
    else:
        assert data["label"] == "Employé stable"