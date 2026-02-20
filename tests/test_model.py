import pytest
import pandas as pd
import joblib
import sys
sys.path.append(".")
from api.main import preprocess, EmployeeInput

import os
import pytest
from dotenv import load_dotenv

load_dotenv()

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
    assert list(result.columns) == feature_names

def test_preprocess_heure_supplementaires_encoding():
    input_oui = EmployeeInput(**{**VALID_INPUT.dict(), "heure_supplementaires": "Oui"})
    input_non = EmployeeInput(**{**VALID_INPUT.dict(), "heure_supplementaires": "Non"})
    assert preprocess(input_oui)["heure_supplementaires_encoded"].values[0] == 1
    assert preprocess(input_non)["heure_supplementaires_encoded"].values[0] == 0

def test_preprocess_frequence_deplacement_encoding():
    for val, expected in [("Aucun", 0), ("Occasionnel", 1), ("Frequent", 2)]:
        inp = EmployeeInput(**{**VALID_INPUT.dict(), "frequence_deplacement": val})
        assert preprocess(inp)["frequence_deplacement_encoded"].values[0] == expected

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