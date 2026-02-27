import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys
sys.path.append(".")
from database.create_db import Employe, Base

DATABASE_URL = "postgresql://attrition_user:attrition_pass@localhost/attrition_db"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

df = pd.read_csv("notebooks/data_complete.csv")
print(f"📊 {len(df)} employés à insérer...")

for _, row in df.iterrows():
    employe = Employe(
        age=row["age"],
        revenu_mensuel=row["revenu_mensuel"],
        departement=row["departement"],
        poste=row["poste"],
        statut_marital=row["statut_marital"],
        genre=row["genre"],
        heure_supplementaires=row["heure_supplementaires"],
        frequence_deplacement=row["frequence_deplacement"],
        satisfaction_employee_environnement=row["satisfaction_employee_environnement"],
        satisfaction_employee_nature_travail=row["satisfaction_employee_nature_travail"],
        satisfaction_employee_equipe=row["satisfaction_employee_equipe"],
        satisfaction_employee_equilibre_pro_perso=row["satisfaction_employee_equilibre_pro_perso"],
        annees_dans_l_entreprise=row["annees_dans_l_entreprise"],
        a_quitte_l_entreprise=row["a_quitte_l_entreprise"],
        nombre_experiences_precedentes=row["nombre_experiences_precedentes"],
        annee_experience_totale=row["annee_experience_totale"],
        annees_dans_le_poste_actuel=row["annees_dans_le_poste_actuel"],
        note_evaluation_precedente=row["note_evaluation_precedente"],
        note_evaluation_actuelle=row["note_evaluation_actuelle"],
        augmentation_salaire_precedente=row["augmentation_salaire_precedente"],
        nombre_participation_pee=row["nombre_participation_pee"],
        nb_formations_suivies=row["nb_formations_suivies"],
        distance_domicile_travail=row["distance_domicile_travail"],
        niveau_education=row["niveau_education"],
        domaine_etude=row["domaine_etude"],
        annees_depuis_la_derniere_promotion=row["annees_depuis_la_derniere_promotion"]
    )
    session.add(employe)

session.commit()
session.close()
print("✅ Dataset inséré avec succès !")