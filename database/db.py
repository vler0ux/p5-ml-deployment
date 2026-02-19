from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime

DATABASE_URL = "postgresql://attrition_user:attrition_pass@localhost/attrition_db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

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

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()