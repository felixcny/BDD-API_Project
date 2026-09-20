from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status

from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import DBAPIError

from app import models, schemas, security
from app.database import get_db
from app.schemas import Seance, SeanceCreate, SeanceStats

router = APIRouter(prefix="/seances", tags=["Seances"])

DB = Annotated[Session, Depends(get_db)]
current_user = Annotated[models.Utilisateur, Depends(security.current_user)]
Admin = Annotated[models.Utilisateur, Depends(security.get_admin)]

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

@router.post("", response_model=Seance, status_code=status.HTTP_201_CREATED)
def creer_seance(db: DB, admin:Admin, seance:SeanceCreate):
    coach = db.get(models.Coach, seance.coach_id)
    if coach is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Coach introuvable")
    nouvelle_seance = models.Seance(nom=seance.nom, date_heure=seance.date_heure, capacite_max=seance.capacite_max, coach_id=seance.coach_id, duree_min=seance.duree_min)
    try:
        db.add(nouvelle_seance)
        db.commit()
        db.refresh(nouvelle_seance)
    except DBAPIError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Erreur lors de la création de la séance")
    return nouvelle_seance

@router.put("/{seance_id}", response_model=Seance)
def modifier_seance(db: DB, admin:Admin, seance_id:int, modification:SeanceCreate):
    seance = seance_404(seance_id, db)
    coach = db.get(models.Coach, modification.coach_id)
    if coach is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Coach introuvable")
    requete = (select(func.count(models.Reservation.reservation_id)).where(models.Reservation.seance_id == seance_id).where(models.Reservation.statut == "CONFIRMEE"))
    nombre_reservations = db.scalar(requete)
    if nombre_reservations > modification.capacite_max:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Le nombre de reservations est superieur a la capacite maximale")
    seance.nom = modification.nom
    seance.date_heure = modification.date_heure
    seance.capacite_max = modification.capacite_max
    seance.coach_id = modification.coach_id
    seance.duree_min = modification.duree_min
    try:
        db.commit()
        db.refresh(seance)
    except DBAPIError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Erreur lors de la modification de la séance")
    return seance
    
@router.delete("/{seance_id}", response_model=Seance)
def supprimer_seance(db: DB, admin:Admin, seance_id:int):
    seance = seance_404(seance_id, db)
    requete = (select(func.count(models.Reservation.reservation_id)).where(models.Reservation.seance_id == seance_id).where(models.Reservation.statut == "CONFIRMEE"))
    nombre_reservations = db.scalar(requete)
    if nombre_reservations > 0:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Impossible de supprimer la séance car il y a des réservations")
    try:
        db.delete(seance)
        db.commit()
    except DBAPIError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Erreur lors de la suppression de la séance")
    return seance

@router.get("/{seance_id}/stats", response_model=SeanceStats)
def lire_seance_stats(db: DB, seance_id:int):
    seance = seance_404(seance_id, db)
    requete = (select(func.count(models.Reservation.reservation_id)).where(models.Reservation.seance_id == seance_id).where(models.Reservation.statut == "CONFIRMEE"))
    nombre_reservations = db.scalar(requete)
    places_restantes = seance.capacite_max - nombre_reservations
    return SeanceStats(seance_id=seance.seance_id, capacite_max=seance.capacite_max, nombre_reservations=nombre_reservations, nombre_places_disponibles=places_restantes)