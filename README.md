# BDD-API_Project

Ce projet met en place une API de gestion de salle de sport connectée à une base Oracle, avec FastAPI, SQLAlchemy, Alembic et Docker. Il permet de gérer les utilisateurs, abonnements, coachs, séances et réservations, tout en appliquant plusieurs règles métier directement au niveau de la base de données.

L'API REST utilise **FastAPI**, **Oracle Database**, **SQLAlchemy**, **Alembic** et **Docker**.

Le projet permet notamment de gérer :

- les utilisateurs ;
- les abonnements ;
- les coachs ;
- les séances ;
- les réservations ;
- l'authentification JWT.

---

## Technologies utilisées

- Python 3.11
- FastAPI
- SQLAlchemy
- Alembic
- Oracle Database Free
- OracleDB Python Driver
- Pydantic
- JWT
- Argon2
- Docker
- Docker Compose

---

## Structure du projet

```text
BDD-API_Project/
│
├── alembic/
│   └── versions/              # Migrations de la base de données
│
├── app/
│   ├── models/                # Modèles SQLAlchemy
│   ├── routers/               # Routes FastAPI
│   ├── database.py            # Connexion à Oracle
│   ├── schemas.py             # Schémas Pydantic
│   ├── security.py            # Authentification et JWT
│   └── main.py                # Point d'entrée FastAPI
│
├── Data/                      # Jeux de données du projet
│
├── docker/
│   └── oracle/
│       └── 01_create_gym_user.sh
│
├── Dockerfile
├── docker-compose.yml
├── alembic.ini
├── requirements.txt
├── .env.example
└── README.md
```

---

## Modèle de données

La base Oracle contient cinq tables principales :

### UTILISATEUR

Contient les comptes de l'application.

Rôles disponibles :

- `MEMBRE`
- `COACH`
- `ADMIN`

### ABONNEMENT

Contient les abonnements des utilisateurs.

Types disponibles :

- `MENSUEL`
- `TRIMESTRIEL`
- `ANNUEL`
- `PREMIUM`

### COACH

Associe un profil coach à un utilisateur ayant le rôle `COACH`.

### SEANCE

Contient les séances proposées par la salle de sport avec leur coach, leur date, leur durée et leur capacité maximale.

### RESERVATION

Associe un utilisateur à une séance.

Une réservation possède notamment les statuts :

- `CONFIRMEE`
- `ANNULEE`

---

## Règles métier gérées par Oracle

Plusieurs règles métier sont directement protégées au niveau de la base de données grâce à des contraintes et des triggers Oracle.

Les principales règles sont :

- un utilisateur doit posséder un abonnement actif pour confirmer une réservation ;
- la capacité maximale d'une séance ne peut pas être dépassée ;
- un profil coach ne peut être associé qu'à un utilisateur ayant le rôle `COACH` ;
- le rôle `COACH` ne peut pas être retiré tant qu'un profil coach existe ;
- un utilisateur ne peut pas réserver deux fois la même séance ;
- les dates et valeurs numériques sont contrôlées par des contraintes SQL.

Ces règles sont versionnées avec **Alembic**.

---

# Installation avec Docker

## Prérequis

Pour exécuter le projet avec Docker, il faut disposer de :

- Git
- Docker
- Docker Compose

Aucune installation locale d'Oracle n'est nécessaire.

---

## 1. Cloner le dépôt

```bash
git clone https://github.com/felixcny/BDD-API_Project.git
cd BDD-API_Project
```

---

## 2. Créer le fichier `.env`

Le fichier `.env` contient la configuration locale et les secrets de l'application.

Il ne doit jamais être ajouté au dépôt Git.

À partir de l'exemple fourni :

### Windows PowerShell

```powershell
Copy-Item .env.example .env
```

### Linux / macOS

```bash
cp .env.example .env
```

Modifier ensuite les valeurs présentes dans `.env`.

Exemple :

```env
ORACLE_PWD=CHANGE_ME
GYM_DB_PASSWORD=CHANGE_ME
SECRET_KEY=CHANGE_ME_WITH_A_LONG_RANDOM_SECRET
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

---

## 3. Démarrer l'application

```bash
docker compose up --build
```

Le premier démarrage d'Oracle peut prendre plusieurs minutes.

Docker Compose lance automatiquement :

1. Oracle Database ;
2. la création de l'utilisateur Oracle `gym_app` ;
3. l'application des migrations Alembic ;
4. la création des tables et des règles métier ;
5. l'API FastAPI.

Lorsque le démarrage est terminé, l'API est disponible sur :

```text
http://localhost:8000
```

---

## Documentation Swagger

La documentation interactive de l'API est disponible à l'adresse :

```text
http://localhost:8000/docs
```

Elle permet de consulter et de tester les différentes routes de l'API.

---

## Vérifier que l'API fonctionne

Endpoint de contrôle :

```text
GET /health
```

Adresse :

```text
http://localhost:8000/health
```

Réponse attendue :

```json
{
  "message": "OK"
}
```

---

# Alembic

Alembic est utilisé pour versionner le schéma Oracle.

Les migrations sont stockées dans :

```text
alembic/versions/
```

Lors du démarrage avec Docker Compose, la commande suivante est exécutée automatiquement :

```bash
alembic upgrade head
```

Pour afficher la migration actuellement appliquée depuis le conteneur API :

```bash
docker compose exec api alembic current
```

Pour vérifier si les modèles SQLAlchemy correspondent au schéma :

```bash
docker compose exec api alembic check
```

---

# Arrêter l'application

Pour arrêter les conteneurs :

```bash
docker compose down
```

Les données Oracle sont conservées dans un volume Docker.

Pour supprimer également la base Docker et repartir complètement de zéro :

```bash
docker compose down -v
```

> Attention : l'option `-v` supprime le volume Oracle et donc les données stockées dans cet environnement Docker.

---

# Exécution locale sans Docker

Il est également possible d'exécuter FastAPI directement avec Python.

Créer un environnement virtuel :

```bash
python -m venv venv
```

### Windows PowerShell

```powershell
.\venv\Scripts\Activate.ps1
```

Installer les dépendances :

```bash
pip install -r requirements.txt
```

Configurer `DATABASE_URL` dans `.env`, puis lancer :

```bash
uvicorn app.main:app --reload
```

Dans ce mode, une instance Oracle accessible doit déjà être disponible.

---

# Sécurité

Le fichier `.env` ne doit jamais être versionné.

Le dépôt contient uniquement `.env.example`, qui indique les variables nécessaires sans contenir de mot de passe ni de clé secrète réelle.

Les mots de passe utilisateurs sont hachés avec **Argon2**.

L'authentification de l'API utilise des **tokens JWT**.

---

# API

Les routes sont organisées par domaine :

```text
/auth
/utilisateurs
/abonnements
/coachs
/seances
/reservations
```

L'ensemble des routes et de leurs paramètres est consultable directement avec Swagger :

```text
http://localhost:8000/docs
```

---

# État du projet

Le projet comprend :

- une API FastAPI connectée à Oracle ;
- un schéma SQLAlchemy versionné avec Alembic ;
- des contraintes et règles métier Oracle ;
- une authentification JWT ;
- une configuration Docker permettant de lancer Oracle et FastAPI ;
- une documentation Swagger disponible via `/docs`.