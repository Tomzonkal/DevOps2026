# Projekt DevOps — CI/CD Pipeline

Aplikacja webowa w Pythonie (Flask) z pipeline CI/CD w GitHub Actions.

## Architektura
- GitHub Actions: automatyczny build, test i push obrazu Docker do ACR
- Azure Container Registry: rejestr obrazów
- Azure Kubernetes Service: klaster do deploymentu

## Uruchomienie lokalne
```bash
docker build -t app .
docker run -p 8080:8080 app
```