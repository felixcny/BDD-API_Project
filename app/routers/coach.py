from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import DBAPIError

from app.database import get_db
from app import models, schemas, security
from app.schemas import Coach, Seance, CoachCreate, CoachUpdate

router = APIRouter(prefix="/coachs", tags=["Coachs"])

DB = Annotated[Session, Depends(get_db)]

current_user = Annotated[models.Utilisateur, Depends(security.current_user)]
Admin = Annotated[models.Utilisateur, Depends(security.get_admin)]

def coach_404(coach_id: int, db: Session) -> models.Coach:
    coach = db.get(models.Coach, coach_id)
    if coach is None:
        raise HTTPException(status_code=404, detail="Coach introuvable")
    return coach

@router.get("", response_model=list[Coach])
def lister_coach(db: DB):
    requete = select(models.Coach).order_by(models.Coach.coach_id)
    return db.scalars(requete).all()

@router.get("/{coach_id}", response_model=Coach)
def lire_coach(db: DB, coach_id: int):
    return coach_404(coach_id, db)

@router.get("/{coach_id}/seances", response_model=list[Seance])
def lister_seances_coach(db: DB, coach_id: int):
    coach_404(coach_id, db)
    requete = select(models.Seance).where(models.Seance.coach_id == coach_id).order_by(models.Seance.date_heure)
    return db.scalars(requete).all()

@router.post("", response_model=Coach, status_code=status.HTTP_201_CREATED)
def creer_coach(db: DB, admin:Admin, coach:CoachCreate):
    utilisateur = db.get(models.Utilisateur, coach.utilisateur_id)
    if utilisateur is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Utilisateur introuvable")
    if utilisateur.role != "COACH":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="L'utilisateur doit avoir le role de coach")
    requete = select(models.Coach).where(models.Coach.utilisateur_id == coach.utilisateur_id)
    coach_existant = db.scalar(requete)
    if coach_existant is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Utilisateur déjà coach")
    nouveau_coach = models.Coach(utilisateur_id=coach.utilisateur_id, specialite=coach.specialite)
    try:
        db.add(nouveau_coach)
        db.commit()
        db.refresh(nouveau_coach)
    except DBAPIError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Erreur lors de la création du coach")
    return nouveau_coach

@router.put("/{coach_id}", response_model=Coach)
def modifier_coach(db: DB, admin:Admin, coach_id:int, modification:CoachUpdate):
    coach = coach_404(coach_id, db)
    coach.specialite = modification.specialite
    try:
        db.commit()
        db.refresh(coach)
    except DBAPIError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Erreur lors de la modification du coach")
    return coach
