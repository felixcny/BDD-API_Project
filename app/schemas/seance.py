from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime

class SeanceCreate(BaseModel):
    nom: str= Field(min_length=3, max_length=50)
    coach_id: int
    date_heure: datetime
    duree_min: int = Field(gt=0)
    capacite_max: int = Field(gt=0)

class Seance(SeanceCreate):
    model_config = ConfigDict(from_attributes=True)
    seance_id: int