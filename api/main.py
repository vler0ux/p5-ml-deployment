from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Literal, Optional
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
    revenu_mensuel: float = Field(..., example=5000.0)
    heure_supplementaires: Literal["Oui", "Non"] = Field(..., example="Non")
    satisfaction_employee_environnement: int = Field(..., ge=1, le=4, example=3)
    frequence_deplacement: Literal["Aucun", "Occasionnel", "Frequent"] = Field(..., example="Occasionnel")


    class Config:
        populate_by_name = True
    

class PredictionOutput(BaseModel):
    prediction: int
    label: str
    probabilite_depart: float
    
def preprocess(data: EmployeeInput) -> pd.DataFrame:
    d = data.dict()

    # Encodage ordinal
    freq_map = {"Aucun": 0, "Occasionnel": 1, "Frequent": 2}
    d["frequence_deplacement_encoded"] = freq_map[d.pop("frequence_deplacement")]
    d["heure_supplementaires_encoded"] = 1 if d.pop("heure_supplementaires") == "Oui" else 0
    d["genre_encoded"] = 1 if d.pop("genre") == "M" else 0

    # Encodage OneHot statut_marital (ref = Célibataire)
    statut = d.pop("statut_marital")
    d["statut_marital_Divorcé(e)"] = 1 if statut == "Divorcé(e)" else 0
    d["statut_marital_Marié(e)"] = 1 if statut == "Marié(e)" else 0

    # Encodage OneHot departement (ref = Finance)
    dept = d.pop("departement")
    d["departement_Consulting"] = 1 if dept == "Consulting" else 0

    # Encodage OneHot poste (ref = Analyste)
    poste = d.pop("poste")
    for p in ["Cadre Commercial", "Consultant", "Directeur Technique", "Manager",
              "Représentant Commercial", "Ressources Humaines", "Senior Manager", "Tech Lead"]:
        d[f"poste_{p}"] = 1 if poste == p else 0

    # Encodage OneHot domaine_etude (ref = Sciences)
    domaine = d.pop("domaine_etude")
    for dom in ["Entrepreunariat", "Infra & Cloud", "Marketing", "Ressources Humaines", "Transformation Digitale"]:
        d[f"domaine_etude_{dom}"] = 1 if domaine == dom else 0

    df = pd.DataFrame([d])
    df = df.reindex(columns=feature_names, fill_value=0)
    return df

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