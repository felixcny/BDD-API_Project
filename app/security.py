from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

import os
from datetime import datetime, timedelta, timezone
import jwt
from dotenv import load_dotenv

from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from sqlalchemy.orm import Session
from app.database import get_db
from app import models

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

password_hasher = PasswordHasher()

def password_hash(mdp:str)->str:
    return password_hasher.hash(mdp)

def verify_password(mdp:str, mdp_hash:str)->bool:
    try:
        password_hasher.verify(mdp_hash, mdp)
        return True
    except VerifyMismatchError:
        return False

def create_token(donnees:dict)->str:
    donnees = donnees.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    donnees.update({"exp": expire})
    token = jwt.encode(donnees, SECRET_KEY, algorithm=ALGORITHM)
    return token

bearer = HTTPBearer()

def current_user(credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer)], db:Annotated[Session, Depends(get_db)]) -> models.Utilisateur:
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        utilisateur_id = payload.get("sub")
        if utilisateur_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token invalide", headers={"WWW-Authenticate": "Bearer"})
        utilisateur_id = int(utilisateur_id)
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, ValueError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token invalide ou expiré", headers={"WWW-Authenticate": "Bearer"})
    utilisateur = db.get(models.Utilisateur, utilisateur_id)
    if utilisateur is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Utilisateur introuvable", headers={"WWW-Authenticate": "Bearer"})
    return utilisateur
        
def get_admin(current_user: Annotated[models.Utilisateur, Depends(current_user)]) -> models.Utilisateur:
    if current_user.role != "ADMIN":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Accès réservé aux administrateurs")
    return current_user