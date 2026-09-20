from typing import Annotated, Literal

from fastapi import APIRouter, Depends, HTTPException, Query, status

from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import DBAPIError

from app.database import get_db
from app import models, security, schemas
from app.schemas import Utilisateur, Abonnement

router = APIRouter(prefix="/utilisateurs", tags=["Utilisateurs"])

DB = Annotated[Session, Depends(get_db)]

current_user = Annotated[models.Utilisateur, Depends(security.current_user)]
Admin = Annotated[models.Utilisateur, Depends(security.get_admin)]

def utilisateur_404(utilisateur_id: int, db: Session):
    utilisateur = db.get(models.Utilisateur, utilisateur_id)
    if utilisateur is None:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")
    return utilisateur

@router.get("", response_model=list[Utilisateur])
def lister_utilisateurs(db: DB, admin:Admin, role: Literal["ADMIN","MEMBRE", "COACH"] | None = Query(default=None)):
    requete = select(models.Utilisateur).order_by(models.Utilisateur.nom, models.Utilisateur.prenom)
    if role is not None:
        requete = requete.where(models.Utilisateur.role == role)
    return db.scalars(requete).all()

@router.get("/me", response_model=Utilisateur)
def lire_utilisateur_me(utilisateur: current_user):
    return utilisateur

@router.get("/{utilisateur_id}", response_model=Utilisateur)
def lire_utilisateur(db: DB, utilisateur_id: int, admin:Admin):
    return utilisateur_404(utilisateur_id, db)

@router.put("/{utilisateur_id}/role")
def modifier_utilisateur_role(db: DB, utilisateur_id: int, admin: Admin, modification: schemas.UtilisateurUpdateRole):
    utilisateur = utilisateur_404(utilisateur_id, db)
    utilisateur.role = modification.role
    try:
        db.commit()
        db.refresh(utilisateur)
    except DBAPIError:
        db.rollback()
        raise HTTPException(status_code=HTTP_409_CONFLICT, detail="Erreur lors de la modification")
    return utilisateur