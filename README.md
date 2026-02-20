# API Attrition RH — Projet P5

Déploiement d'un modèle de machine learning pour prédire le risque de départ des employés.

## 📋 Description

Ce projet expose un modèle de **Régression Logistique** entraîné sur des données RH via une API REST FastAPI. Chaque prédiction est enregistrée dans une base de données PostgreSQL pour assurer une traçabilité complète.

## Architecture

```
p5/
├── api/
│   └── main.py          # API FastAPI
├── database/
│   ├── create_db.py     # Création des tables
│   ├── insert_data.py   # Insertion du dataset
│   └── db.py            # Connexion SQLAlchemy
├── models/              # Fichiers .joblib (non versionnés)
├── notebooks/           # Notebook d'entraînement
├── tests/               # Tests unitaires
└── .github/workflows/   # CI/CD
```

## Installation

### Prérequis
- Python 3.11+
- PostgreSQL
- uv

### Étapes

```bash
# Cloner le repo
git clone https://github.com/vler0ux/p5-ml-deployment.git
cd p5-ml-deployment

# Installer les dépendances
uv install

# Configurer la base de données
sudo -u postgres psql
CREATE DATABASE attrition_db;
CREATE USER attrition_user WITH PASSWORD 'attrition_pass';
GRANT ALL PRIVILEGES ON DATABASE attrition_db TO attrition_user;
\q

# Créer les tables
uv run python database/create_db.py

# Insérer le dataset
uv run python database/insert_data.py

# Générer le modèle (exécuter le notebook)
cd notebooks && uv run jupyter lab
```

## Lancement

```bash
uv run uvicorn api.main:app --reload
```

L'API est disponible sur `http://localhost:8000`
La documentation Swagger sur `http://localhost:8000/docs`

## Endpoints

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/` | Message de bienvenue |
| GET | `/health` | Statut de l'API |
| POST | `/predict` | Prédiction de départ |

## Exemple d'utilisation

```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "age": 28,
    "revenu_mensuel": 3000,
    "heure_supplementaires": "Oui",
    "satisfaction_employee_environnement": 1,
    "frequence_deplacement": "Frequent"
  }'
```

Réponse :

```json
{
  "prediction": 1,
  "label": "Risque de départ",
  "probabilite_depart": 0.74
}
```

## Base de données

- **employes** : dataset complet (1470 lignes)
- **predictions** : historique de toutes les prédictions

### Processus de stockage
Chaque appel à `/predict` enregistre automatiquement les inputs et outputs dans la table `predictions` via SQLAlchemy, assurant une traçabilité complète.

## 🔐 Authentification et gestion des accès

### Méthode actuelle — API Key

L'endpoint `/predict` est protégé par une clé API transmise dans le header HTTP :
```
X-API-Key: votre_cle_api
```

Sans clé valide, l'API retourne une erreur `403 Forbidden`.

### Pour aller plus loin en production

| Besoin | Solution recommandée |
|--------|---------------------|
| Utilisateurs multiples | JWT (JSON Web Tokens) avec OAuth2 |
| Gestion des rôles | RBAC (Role-Based Access Control) |
| Expiration des tokens | JWT avec durée de vie limitée |
| Audit des accès | Logs des requêtes avec identifiant utilisateur |

## Bonnes pratiques de sécurité

### Gestion des secrets

Les secrets ne sont **jamais versionnés** dans Git :

```bash
# Bonne pratique
API_KEY=xxx        → stocké dans .env (ignoré par .gitignore)

# À ne jamais faire
API_KEY=xxx        → écrit directement dans le code
```

En production, utiliser un gestionnaire de secrets :

- **GitHub Actions** : secrets chiffrés dans les Settings du repo
- **Production** : HashiCorp Vault, AWS Secrets Manager, etc.

### Hachage de mot de passe

Si le projet évolue vers un système avec comptes utilisateurs, les mots de passe ne doivent **jamais être stockés en clair**. Utiliser `bcrypt` :
```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"])

# Hacher le mot de passe avant stockage
hashed = pwd_context.hash("mot_de_passe")

# Vérifier lors de la connexion
pwd_context.verify("mot_de_passe", hashed)
```

### Accès à la base de données

- Un utilisateur PostgreSQL dédié (`attrition_user`) avec droits limités
- Les credentials BDD stockés dans `.env`
- Aucun accès root en production

### Variables d'environnement requises
```bash
# .env.example
API_KEY=votre_cle_api_ici
DATABASE_URL=postgresql://user:password@localhost/attrition_db
```

## CI/CD

Le pipeline GitHub Actions (`.github/workflows/ci.yml`) :
- S'exécute à chaque push
- Lance les tests automatiquement
- Gère les environnements dev et prod via les secrets GitHub

## Stack technique

| Outil | Usage |
|-------|-------|
| FastAPI | API REST |
| Pydantic | Validation des données |
| scikit-learn | Modèle ML |
| PostgreSQL | Base de données |
| SQLAlchemy | ORM |
| uv | Gestionnaire de paquets |
| pytest | Tests unitaires |
| GitHub Actions | CI/CD |