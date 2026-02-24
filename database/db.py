from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
import os

DATABASE_URL = os.getenv("DATABASE_URL")

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

if DATABASE_URL:
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
else:
    engine = None
    SessionLocal = None

def get_db():
    if SessionLocal is None:
        yield None
        return
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()