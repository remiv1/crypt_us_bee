# Utiliser une image de base officielle Python complète
FROM python:3.12

# Définir le répertoire de travail dans le conteneur
WORKDIR /app

# Copier les fichiers de l'application dans le conteneur
# COPY . /app # En développement, le dossier des documents est monté en tant que volume
COPY requirements-app.txt /app/requirements.txt

# Installer les dépendances nécessaires
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Exposer le port sur lequel l'application Flask s'exécute
EXPOSE 5000

# Définir la commande par défaut pour exécuter l'application
CMD ["python", "application.py"]
