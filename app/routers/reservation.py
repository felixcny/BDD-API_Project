from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import DBAPIError

from app import models, security
from app.database import get_db
from app.schemas import Reservation, ReservationCreate

router = APIRouter(prefix="/reservations", tags=["Reservations"])

DB = Annotated[Session, Depends(get_db)]

current_user = Annotated[models.Utilisateur, Depends(security.current_user)]
Admin = Annotated[models.Utilisateur, Depends(security.get_admin)]

def reservation_404(reservation_id: int, db: Session) -> models.Reservation:
    reservation = db.get(models.Reservation, reservation_id)
    if reservation is None:
        raise HTTPException(status_code=404, detail="Reservation introuvable")
    return reservation

@router.get("", response_model=list[Reservation])
def lister_reservations(db: DB, admin:Admin):
    requete = select(models.Reservation).order_by(models.Reservation.date_reservation.desc())
    return db.scalars(requete).all()

@router.get("/me", response_model=list[Reservation])
def lire_reservation_me(db: DB, utilisateur: current_user):
    requete = select(models.Reservation).where(models.Reservation.utilisateur_id == utilisateur.utilisateur_id).order_by(models.Reservation.date_reservation.desc())
    return db.scalars(requete).all()

@router.get("/{reservation_id}", response_model=Reservation)
def lire_reservation(db: DB, admin:Admin, reservation_id: int):
    return reservation_404(reservation_id, db)

@router.post("", response_model=Reservation, status_code=status.HTTP_201_CREATED)
def creer_reservation(db: DB, utilisateur: current_user, reservation: ReservationCreate):
    seance = db.get(models.Seance, reservation.seance_id)
    if seance is None:
        raise HTTPException(status_code=404, detail="Seance introuvable")
    nouvelle_reservation = models.Reservation(utilisateur_id = utilisateur.utilisateur_id, seance_id = reservation.seance_id, statut="CONFIRMEE")
    try:
        db.add(nouvelle_reservation)
        db.commit()
    except DBAPIError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Erreur lors de la reservation")
    db.refresh(nouvelle_reservation)
    return nouvelle_reservation

@router.delete("/{reservation_id}")
def annuler_reservation(db: DB, utilisateur: current_user, reservation_id: int):
    reservation = reservation_404(reservation_id, db)
    if reservation.utilisateur_id != utilisateur.utilisateur_id and utilisateur.role != "ADMIN":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Vous ne pouvez pas annuler la reservation")
    if reservation.statut == "ANNULEE":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Reservation deja annulée")
    try:
        reservation.statut = "ANNULEE"
        db.commit()
    except DBAPIError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Erreur lors de l'annulation de la reservation")
    db.refresh(reservation)
    return reservation

