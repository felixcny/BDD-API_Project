from pydantic import BaseModel, Field, ConfigDict
from datetime import date
from typing import Literal

class UtilisateurBase(BaseModel):
    nom: str = Field(min_length=3, max_length=50)
    prenom: str = Field(min_length=3, max_length=50)
    email: str = Field(min_length=3, max_length=50)


class UtilisateurCreate(UtilisateurBase):
    password: str = Field(min_length=8, max_length=100)

class Utilisateur(UtilisateurBase):
    model_config = ConfigDict(from_attributes=True)
    utilisateur_id: int 
    date_inscription: date
    role: Literal["ADMIN", "COACH", "CLIENT"]
    
    