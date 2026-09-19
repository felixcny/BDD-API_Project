from typing import Annotated

from fastapi import APIRouter, Depends, status, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas
from app import security

router = APIRouter(prefix="/auth", tags=["Authentification"])

DB = Annotated[Session, Depends(get_db)]

@router.post("/register", response_model=schemas.Utilisateur, status_code=status.HTTP_201_CREATED)
def register(utilisateur:schemas.UtilisateurCreate, db:DB):
    email = str(utilisateur.email).lower()
    requete_mail = select(models.Utilisateur.email).where(models.Utilisateur.email == email)
    mail_existant = db.scalar(requete_mail)
    if mail_existant is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email déjà utilisé")
    nouveau_utilisateur = models.Utilisateur(nom = utilisateur.nom, prenom = utilisateur.prenom, password_hash = security.password_hash(utilisateur.password), role = "MEMBRE", email = email)
    db.add(nouveau_utilisateur)
    db.commit()
    db.refresh(nouveau_utilisateur)
    return nouveau_utilisateur

@router.post("/token", response_model=schemas.TokenResponse)
def login(connexion:schemas.LoginRequest, db:DB):
    email = str(connexion.email).lower()
    requete = select(models.Utilisateur).where(models.Utilisateur.email == email)
    utilisateur = db.scalar(requete)
    if utilisateur is None:
        raise HTTPException(status_code=401, detail="Email ou mot de passe incorrect")
    if not security.verify_password(connexion.password, utilisateur.password_hash):
        raise HTTPException(status_code=401, detail="Email ou mot de passe incorrect")
    token = security.create_token({"sub": str(utilisateur.utilisateur_id)})
    return ({"access_token":token, "token_type":"bearer"})