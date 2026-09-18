from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query

from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.schemas import Seance, SeanceCreate

router = APIRouter(prefix="/seances", tags=["seances"])

DB = Annotated[Session, Depends(get_db)]

def seance_404(seance_id: int, db: Session) -> models.Seance:
    seance = db.get(models.Seance, seance_id)
    if seance is None:
        raise HTTPException(status_code=404, detail="Seance introuvable")
    return seance

@router.get("", response_model=list[Seance])
def lister_seance(db: DB, coach_id: int | None = Query(default=None)):
    requete = select(models.Seance).order_by(models.Seance.date_heure)
    if coach_id is not None:
        requete = requete.where(models.Seance.coach_id == coach_id)
    return db.scalars(requete).all()

@router.get("/{seance_id}", response_model=Seance)
def lire_seance(db: DB, seance_id: int): 
    return seance_404(seance_id, db)

    