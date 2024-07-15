# Utilise l'image de base officielle de Python
FROM python:3.11-slim

# Configure l'environnement
## Ne pas créer de fichier de compilation .pyc
ENV PYTHONDONTWRITEBYTECODE 1 
## Ecrire le retour dans la console sans bufferisation
ENV PYTHONUNBUFFERED 1

# Configure le répertoire de travail
WORKDIR /app

# Copie le code de l'application dans le conteneur
COPY . /app/

# Installe les dépendances
RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

# Expose le port de l'application
EXPOSE 5000

# Commande pour exécuter l'application
CMD ["python", "app.py"]
