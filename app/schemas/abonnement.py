from pydantic import BaseModel, ConfigDict, Field, model_validator
from datetime import date
from typing import Literal


class AbonnementCreate(BaseModel):
    utilisateur_id: int
    type_abonnement: Literal["MENSUEL", "TRIMESTRIEL", "PREMIUM", "ANNUEL"]
    date_debut: date 
    date_fin: date 
    prix: float = Field(gt=0)   
    statut: Literal["ACTIF", "EXPIRE", "ANNULE"] = "ACTIF"
    @model_validator(mode="after")  
    def validate_date_fin(self):
        if self.date_fin <= self.date_debut:
            raise ValueError("La date de fin doit être supérieure à la date de début")
        return self
    

class Abonnement(AbonnementCreate):
    model_config = ConfigDict(from_attributes=True)
    abonnement_id: int