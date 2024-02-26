# syntax=docker/dockerfile:1
FROM python:3.12.1-slim

# Installer les dépendances de l'application
RUN apt-get update && apt-get install -y python3 python3-pip

# Installer les dépendances Python
RUN pip install signalrcore flask requests

# Copier le code source dans le conteneur
COPY src/main.py /

# Configuration finale
ENV PYTHONUNBUFFERED=1
CMD ["python", "main.py"]
