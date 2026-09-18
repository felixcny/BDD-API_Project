from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Literal

class ReservationCreate(BaseModel):
    seance_id: int

class Reservation(ReservationCreate):
    model_config = ConfigDict(from_attributes=True)
    reservation_id: int
    utilisateur_id: int
    seance_id: int
    date_reservation: datetime
    statut: Literal["CONFIRMEE", "ANNULEE"] 