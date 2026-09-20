from typing import Annotated, Literal

from fastapi import APIRouter, Depends, HTTPException, Query

from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models, security
from app.database import get_db
from app.schemas import Abonnement, AbonnementCreate

router = APIRouter(prefix="/abonnements", tags=["Abonnements"])

DB = Annotated[Session, Depends(get_db)]

current_user = Annotated[models.Utilisateur, Depends(security.current_user)]
Admin = Annotated[models.Utilisateur, Depends(security.get_admin)]

def abonnement_404(abonnement_id: int, db: Session) -> models.Abonnement:
    abonnement = db.get(models.Abonnement, abonnement_id)
    if abonnement is None:
        raise HTTPException(status_code=404, detail="Abonnement introuvable")
    return abonnement

@router.get("", response_model=list[Abonnement])
def lister_abonnements(db: DB, admin:Admin, utilisateur_id: int | None = Query(default=None), statut: Literal["ACTIF", "EXPIRE", "ANNULE"] | None = Query(default=None)):
    requete = select(models.Abonnement).order_by(models.Abonnement.date_debut.desc())
    if utilisateur_id is not None:
        requete = requete.where(models.Abonnement.utilisateur_id == utilisateur_id)
    if statut is not None:
        requete = requete.where(models.Abonnement.statut == statut)
    return db.scalars(requete).all()

@router.get("/me", response_model=list[Abonnement])
def lire_abonnement_me(db: DB, utilisateur: current_user):
    requete = select(models.Abonnement).where(models.Abonnement.utilisateur_id == utilisateur.utilisateur_id).order_by(models.Abonnement.date_debut.desc())
    return db.scalars(requete).all()


@router.get("/{abonnement_id}", response_model=Abonnement)
def lire_abonnement(db: DB, admin:Admin, abonnement_id: int):
    return abonnement_404(abonnement_id, db)
