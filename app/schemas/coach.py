from pydantic import BaseModel, Field, ConfigDict

class CoachCreate(BaseModel):
    utilisateur_id: int
    specialite: str = Field(min_length=3, max_length=100)

class Coach(CoachCreate):
    model_config = ConfigDict(from_attributes=True)
    coach_id: int 

class CoachUpdate(BaseModel):
    specialite: str = Field(min_length=3, max_length=100)