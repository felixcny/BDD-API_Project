from fastapi import FastAPI

from app.routers import seance, coach, abonnement, utilisateur, auth


app = FastAPI(title="API GYM", version="1.0.0", description="API pour la gestion d'une salle de sport")


app.include_router(seance.router)
app.include_router(coach.router)
app.include_router(abonnement.router)
app.include_router(utilisateur.router)
app.include_router(auth.router)

@app.get("/health", tags=["system"])
def health():
    return {"message": "OK"}