# Projekt DevOps 2026

Projekt przedstawia podstawowy potok CI/CD dla aplikacji kontenerowej wdrażanej na Azure Kubernetes Service.

## Opis aplikacji

Aplikacja została napisana w Pythonie z użyciem Flask. Udostępnia dwa endpointy:

- `/` — strona główna aplikacji
- `/health` — endpoint sprawdzający stan aplikacji

## Technologie

- Python
- Flask
- Docker
- GitHub Actions
- Azure Container Registry
- Azure Kubernetes Service
- Kubernetes

## Uruchomienie lokalne

```bash
docker build -t projekt-devops .
docker run -p 8080:8080 projekt-devops
