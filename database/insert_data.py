import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from create_db import Employe, Base

DATABASE_URL = "postgresql://attrition_user:attrition_pass@localhost/attrition_db"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

# Charger le dataset
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
        a_quitte_l_entreprise=row["a_quitte_l_entreprise"]
    )
    session.add(employe)

session.commit()
session.close()
print("✅ Dataset inséré avec succès !")