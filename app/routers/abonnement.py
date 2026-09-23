from typing import Annotated, Literal

from fastapi import APIRouter, Depends, HTTPException, Query, status

from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import DBAPIError

from app import models, security
from app.database import get_db
from app.schemas import Abonnement, AbonnementCreate, AbonementUpdate

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

@router.post("", response_model=Abonnement, status_code=status.HTTP_201_CREATED)
def creer_abonnement(db: DB, admin: Admin, abonnement: AbonnementCreate):
    utilisateur = db.get(models.Utilisateur, abonnement.utilisateur_id)
    if utilisateur is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Utilisateur introuvable")
    if utilisateur.role != "ADMIN":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Vous devez être connecté pour acheter un abonnement")
    nouvel_abonnement = models.Abonnement(utilisateur_id = utilisateur.utilisateur_id, type_abonnement = abonnement.type_abonnement, date_debut = abonnement.date_debut, date_fin = abonnement.date_fin, prix = abonnement.prix, statut = abonnement.statut)
    try:
        db.add(nouvel_abonnement)
        db.commit()
        db.refresh(nouvel_abonnement)
    except DBAPIError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Erreur lors de l'achat de l'abonnement")
    return nouvel_abonnement

@router.delete("/{abonnement_id}", response_model=Abonnement)
def annuler_abonnement(db:DB, admin:Admin, abonnement_id:int):
    abonnement = abonnement_404(abonnement_id, db)
    if abonnement.statut == "ANNULE":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Abonnement deja annulé")
    try:
        abonnement.statut = "ANNULE"
        db.commit()
        db.refresh(abonnement)
    except DBAPIError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Erreur lors de l'annulation de l'abonnement")
    return abonnement

@router.put("/{abonnement_id}", response_model=Abonnement)
def modifier_abonnement(db: DB, admin:Admin, abonnement_id:int, modification:AbonementUpdate):
    abonnement = abonnement_404(abonnement_id, db)
    abonnement.type_abonnement = modification.type_abonnement
    abonnement.date_debut = modification.date_debut
    abonnement.date_fin = modification.date_fin
    abonnement.prix = modification.prix
    abonnement.statut = modification.statut
    try:
        db.commit()
        db.refresh(abonnement)
    except DBAPIError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Erreur lors de la modification de l'abonnement")
    return abonnement