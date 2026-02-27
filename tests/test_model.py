import pytest
import pandas as pd
import joblib
import sys
import os
sys.path.append(".")
from dotenv import load_dotenv
load_dotenv()
from api.main import preprocess, EmployeeInput

pytestmark = pytest.mark.skipif(
    not os.path.exists("models/model.joblib"),
    reason="Modèle non disponible en CI"
)

VALID_INPUT = EmployeeInput(
    age=35,
    revenu_mensuel=5000.0,
    heure_supplementaires="Oui",
    satisfaction_employee_environnement=2,
    frequence_deplacement="Frequent"
)

# ── Tests preprocessing ─────────────────────────────────────────
def test_preprocess_returns_dataframe():
    result = preprocess(VALID_INPUT)
    assert isinstance(result, pd.DataFrame)

def test_preprocess_correct_columns():
    feature_names = joblib.load("models/feature_names.joblib")
    result = preprocess(VALID_INPUT)
    assert list(result.columns) == list(feature_names)

def test_preprocess_heure_supplementaires_encoding():
    input_oui = EmployeeInput(**{**VALID_INPUT.model_dump(), "heure_supplementaires": "Oui"})
    input_non = EmployeeInput(**{**VALID_INPUT.model_dump(), "heure_supplementaires": "Non"})
    assert not preprocess(input_oui).equals(preprocess(input_non))

def test_preprocess_frequence_deplacement_encoding():
    results = []
    for val in ["Aucun", "Occasionnel", "Frequent"]:
        inp = EmployeeInput(**{**VALID_INPUT.model_dump(), "frequence_deplacement": val})
        results.append(preprocess(inp))
    assert not results[0].equals(results[1])
    assert not results[1].equals(results[2])

def test_preprocess_no_missing_values():
    result = preprocess(VALID_INPUT)
    assert result.isnull().sum().sum() == 0

# ── Tests modèle ────────────────────────────────────────────────
def test_model_loads():
    model = joblib.load("models/model.joblib")
    assert model is not None

def test_model_predict_output():
    model = joblib.load("models/model.joblib")
    df = preprocess(VALID_INPUT)
    prediction = model.predict(df)[0]
    assert prediction in [0, 1]

def test_model_predict_proba_range():
    model = joblib.load("models/model.joblib")
    df = preprocess(VALID_INPUT)
    proba = model.predict_proba(df)[0][1]
    assert 0.0 <= proba <= 1.0