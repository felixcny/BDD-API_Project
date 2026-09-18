from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app import models
from app.schemas import Coach, Seance

router = APIRouter(prefix="/coachs", tags=["Coachs"])

DB = Annotated[Session, Depends(get_db)]

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