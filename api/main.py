from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import joblib
import pandas as pd
import numpy as np

# Chargement du modèle et des features
model = joblib.load("models/model.joblib")
feature_names = joblib.load("models/feature_names.joblib")

app = FastAPI(
    title="API Attrition RH",
    description="Prédit si un employé va quitter l'entreprise",
    version="1.0.0"
)

# Schéma des données d'entrée
class EmployeeInput(BaseModel):
    age: int = Field(..., example=35)
    anciennete: int = Field(..., example=5)
    salaire_mensuel: float = Field(..., example=5000.0)
    satisfaction_emploi: int = Field(..., ge=1, le=4, example=3)
    satisfaction_environnement: int = Field(..., ge=1, le=4, example=2)
    satisfaction_relation: int = Field(..., ge=1, le=4, example=3)
    equilibre_vie: int = Field(..., ge=1, le=4, example=2)
    implication_emploi: int = Field(..., ge=1, le=4, example=3)
    nb_entreprises_precedentes: int = Field(..., example=2)
    annees_experience: int = Field(..., example=10)
    formation_annee: int = Field(..., ge=0, le=6, example=3)
    heure_supplementaires_encoded: int = Field(..., ge=0, le=1, example=1)
    genre_encoded: int = Field(..., ge=0, le=1, example=1)
    frequence_deplacement_encoded: int = Field(..., ge=0, le=2, example=1)
    # Ajouter ici les colonnes OneHotEncoded (statut_marital, poste, domaine_etude)

class PredictionOutput(BaseModel):
    prediction: int
    label: str
    probabilite_depart: float

@app.get("/")
def root():
    return {"message": "API Attrition RH opérationnelle"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/predict", response_model=PredictionOutput)
def predict(data: EmployeeInput):
    try:
        input_df = pd.DataFrame([data.dict()])
        input_df = input_df.reindex(columns=feature_names, fill_value=0)
        
        prediction = model.predict(input_df)[0]
        proba = model.predict_proba(input_df)[0][1]
        
        return {
            "prediction": int(prediction),
            "label": "Risque de départ" if prediction == 1 else "Employé stable",
            "probabilite_depart": round(float(proba), 4)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))