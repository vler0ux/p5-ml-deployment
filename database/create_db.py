from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime, text
from sqlalchemy.orm import declarative_base
from datetime import datetime

DATABASE_URL = "postgresql://attrition_user:attrition_pass@localhost/attrition_db"

engine = create_engine(DATABASE_URL)
Base = declarative_base()

class Employe(Base):
    __tablename__ = "employes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    age = Column(Integer)
    revenu_mensuel = Column(Float)
    departement = Column(String)
    poste = Column(String)
    statut_marital = Column(String)
    genre = Column(String)
    heure_supplementaires = Column(String)
    frequence_deplacement = Column(String)
    satisfaction_employee_environnement = Column(Integer)
    satisfaction_employee_nature_travail = Column(Integer)
    satisfaction_employee_equipe = Column(Integer)
    satisfaction_employee_equilibre_pro_perso = Column(Integer)
    annees_dans_l_entreprise = Column(Integer)
    a_quitte_l_entreprise = Column(String)  # valeur réelle du dataset

class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    date_prediction = Column(DateTime, default=datetime.utcnow)
    age = Column(Integer)
    revenu_mensuel = Column(Float)
    departement = Column(String)
    poste = Column(String)
    heure_supplementaires = Column(String)
    frequence_deplacement = Column(String)
    prediction = Column(Integer)
    label = Column(String)
    probabilite_depart = Column(Float)

if __name__ == "__main__":
    Base.metadata.create_all(engine)
    print("✅ Tables créées avec succès !")