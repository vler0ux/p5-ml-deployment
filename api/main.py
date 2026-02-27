from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Literal, Optional
from sqlalchemy.orm import Session
from fastapi import Depends
import sys
sys.path.append(".")
from database.db import get_db, Prediction  #connexion avec SQLAlchemy
import joblib
import pandas as pd

from fastapi.security.api_key import APIKeyHeader
from fastapi import Security
import os
from dotenv import load_dotenv

# Chargement du modèle et des features
try:
    model = joblib.load("models/model.joblib")
    feature_names = joblib.load("models/feature_names.joblib")
except FileNotFoundError:
    model = None
    feature_names = []
    
app = FastAPI(
    title="API Attrition RH",
    description="Prédit si un employé va quitter l'entreprise",
    version="1.0.0"
)

#authentification
load_dotenv()

API_KEY = os.getenv("API_KEY")
api_key_header = APIKeyHeader(name="X-API-Key")

def verify_api_key(key: str = Security(api_key_header)):
    if key != API_KEY:
        raise HTTPException(status_code=403, detail="Clé API invalide")
    return key

# Schéma des données d'entrée
class EmployeeInput(BaseModel):
    age: int = Field(..., example=35)
    revenu_mensuel: float = Field(..., example=5000.0)
    heure_supplementaires: Literal["Oui", "Non"] = Field(..., example="Non")
    satisfaction_employee_environnement: int = Field(..., ge=1, le=4, example=3)
    frequence_deplacement: Literal["Aucun", "Occasionnel", "Frequent"] = Field(..., example="Occasionnel")
    genre: Literal["M", "F"] = Field("M", example="M")
    statut_marital: Literal["Célibataire", "Marié(e)", "Divorcé(e)"] = Field("Célibataire", example="Célibataire")
    departement: Literal["Consulting", "Finance", "Recherche & Développement", "Ressources Humaines", "Ventes"] = Field("Finance", example="Finance")
    poste: Literal["Cadre Commercial", "Consultant", "Directeur Technique", "Manager", "Représentant Commercial", "Ressources Humaines", "Senior Manager", "Tech Lead"] = Field("Consultant", example="Consultant")
    domaine_etude: Literal["Entrepreunariat", "Infra & Cloud", "Marketing", "Ressources Humaines", "Sciences", "Transformation Digitale"] = Field("Sciences", example="Sciences")
    nombre_experiences_precedentes: int = Field(2, example=2)
    annee_experience_totale: int = Field(10, example=10)
    annees_dans_l_entreprise: int = Field(5, example=5)
    annees_dans_le_poste_actuel: int = Field(3, example=3)
    note_evaluation_precedente: float = Field(3.5, example=3.5)
    satisfaction_employee_nature_travail: int = Field(3, ge=1, le=4, example=3)
    satisfaction_employee_equipe: int = Field(3, ge=1, le=4, example=3)
    satisfaction_employee_equilibre_pro_perso: int = Field(3, ge=1, le=4, example=3)
    note_evaluation_actuelle: float = Field(3.5, example=3.5)
    augmentation_salaire_precedente: float = Field(10.0, example=10.0)
    nombre_participation_pee: int = Field(2, example=2)
    nb_formations_suivies: int = Field(3, example=3)
    distance_domicile_travail: float = Field(10.0, example=10.0)
    niveau_education: int = Field(3, ge=1, le=5, example=3)
    annees_depuis_la_derniere_promotion: int = Field(2, example=2)

    class Config:
        populate_by_name = True
    

class PredictionOutput(BaseModel):
    prediction: int
    label: str
    probabilite_depart: float
    
def preprocess(data: EmployeeInput) -> pd.DataFrame:
    d = data.model_dump(exclude_unset=False) 

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
def predict(data: EmployeeInput, db: Session = Depends(get_db), key: str = Security(verify_api_key)):
    if model is None:
        raise HTTPException(status_code=503, detail="Modèle non disponible")
    
    try:
        print(data.model_dump()) 
        input_df = preprocess(data)
        prediction = model.predict(input_df)[0]
        proba = model.predict_proba(input_df)[0][1]

        # Enregistrer en BDD
        log = Prediction(
            age=data.age,
            revenu_mensuel=data.revenu_mensuel,
            departement=data.departement,
            poste=data.poste,
            heure_supplementaires=data.heure_supplementaires,
            frequence_deplacement=data.frequence_deplacement,
            prediction=int(prediction),
            label="Risque de départ" if prediction == 1 else "Employé stable",
            probabilite_depart=round(float(proba), 4)
        )
        if db is not None:
            db.add(log)
            db.commit()

        return {
            "prediction": int(prediction),
            "label": log.label,
            "probabilite_depart": log.probabilite_depart
        }
    except Exception as e:
        print(f"ERREUR: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    


