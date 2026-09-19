from typing import Annotated, Literal

from fastapi import APIRouter, Depends, HTTPException, Query

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app import models
from app.schemas import Utilisateur, Abonnement

router = APIRouter(prefix="/utilisateurs", tags=["Utilisateurs"])

DB = Annotated[Session, Depends(get_db)]

def utilisateur_404(utilisateur_id: int, db: Session):
    utilisateur = db.get(models.Utilisateur, utilisateur_id)
    if utilisateur is None:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")
    return utilisateur

@router.get("", response_model=list[Utilisateur])
def lister_utilisateurs(db: DB, role: Literal["ADMIN","MEMBRE", "COACH"] | None = Query(default=None)):
    requete = select(models.Utilisateur).order_by(models.Utilisateur.nom, models.Utilisateur.prenom)
    if role is not None:
        requete = requete.where(models.Utilisateur.role == role)
    return db.scalars(requete).all()

@router.get("/{utilisateur_id}", response_model=Utilisateur)
def lire_utilisateur(db: DB, utilisateur_id: int):
    return utilisateur_404(utilisateur_id, db)