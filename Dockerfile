# Image Python légère utilisée pour exécuter l'API
FROM python:3.11-slim

# Tous les fichiers du projet seront placés dans /app dans le conteneur
WORKDIR /app

# Copie d'abord requirements.txt.
# Cela permet à Docker de réutiliser le cache des dépendances
# si le code change mais pas requirements.txt.
COPY requirements.txt .

# Installe toutes les dépendances Python du projet
RUN pip install --no-cache-dir -r requirements.txt

# Copie ensuite le reste du projet dans le conteneur
COPY . .

# Documentation : notre API écoute sur le port 8000
EXPOSE 8000

# Commande lancée lorsque le conteneur démarre
# 0.0.0.0 permet d'accéder à FastAPI depuis l'extérieur du conteneur.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]