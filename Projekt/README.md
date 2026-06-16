# DevOps 2026 - projekt 422379

Projekt pokazuje pelny pipeline CI/CD dla aplikacji kontenerowej wdrazanej na Azure Kubernetes Service. Wariant odpowiada wymaganiom na ocene 5: Terraform, remote state, GitHub Actions, OIDC, ACR, AKS i automatyczny rollout aplikacji.

## Architektura

Przeplyw:

```text
GitHub branch projekt_422379
        |
        | GitHub Actions
        |
        +--> Terraform workflow
        |       - terraform init
        |       - terraform fmt
        |       - terraform validate
        |       - terraform plan
        |       - terraform apply
        |
        +--> CI/CD workflow
                - testy Python
                - docker build
                - docker push do ACR
                - kubectl rollout do AKS
```

Azure:

```text
Azure Storage Account
        |
        +--> remote Terraform state

Azure Container Registry
        |
        +--> obraz Docker: app:<github.sha>

Azure Kubernetes Service
        |
        +--> Deployment app
        +--> Service app-svc LoadBalancer
```

## Struktura projektu

```text
Projekt/
  app/
    server.py
  tests/
    test_health.py
  infra/
    backend.tf
    main.tf
    variables.tf
    outputs.tf
  k8s/
    deployment.yaml
  Dockerfile
  README.md
  OPIS_PROJEKTU_422379.md

.github/workflows/
  infra.yml
  ci.yml
```

## Aplikacja

Aplikacja to prosty serwer HTTP w Pythonie.

Endpointy:

- `GET /` - zwraca status aplikacji i wersje.
- `GET /health` - zwraca `{"status": "ok"}`.

Port:

```text
8080
```

Lokalny test:

```powershell
cd C:\DEVOPS\DevOps2026\Projekt
python -m unittest discover -s tests
```

## Docker

Obraz budowany z `python:3.12-slim`.

Build lokalny:

```powershell
cd C:\DEVOPS\DevOps2026\Projekt
docker build -t devops-lab05-app .
```

Run lokalny:

```powershell
docker run --rm -p 8080:8080 devops-lab05-app
```

Test:

```powershell
Invoke-RestMethod http://localhost:8080/health
```

W CI obraz ma tag:

```text
app:<github.sha>
```

Nie uzyto `latest`, bo `latest` nie wskazuje konkretnego commita.

## Terraform

Terraform zarzadza infrastruktura Azure.

Zasoby:

- Resource Group: `rg-lab05`
- Azure Container Registry: `acrlab05422379`
- Azure Kubernetes Service: `aks-lab05`
- Role assignment: `AcrPull`

Region:

```text
polandcentral
```

Node size AKS:

```text
Standard_B2s_v2
```

Powod: `Standard_B2s` byl zablokowany w subskrypcji/regionie.

Komendy lokalne:

```powershell
cd C:\DEVOPS\DevOps2026\Projekt\infra
terraform fmt -recursive
terraform init -backend-config="storage_account_name=stlab05tfstate422379"
terraform validate
terraform plan
```

`terraform apply` wykonuje GitHub Actions, nie lokalnie.

## Remote state

Terraform state trzymany w Azure Storage.

Backend:

```text
resource group: rg-tf-state
storage account: stlab05tfstate422379
container: tfstate
key: lab05.terraform.tfstate
```

Po co remote state:

- GitHub Actions ma dostep do tego samego state.
- State nie lezy lokalnie na komputerze.
- Latwiej pracowac zespolowo.
- Mniejsze ryzyko konfliktu infrastruktury.

## GitHub Actions

Workflowy sa w root repo:

```text
.github/workflows/infra.yml
.github/workflows/ci.yml
```

### Terraform - Infrastructure

Trigger:

- push na `projekt_422379`
- zmiany w `Projekt/infra/**`
- zmiana `.github/workflows/infra.yml`
- pull request dla zmian infrastruktury
- manualne `workflow_dispatch`

Kroki:

- checkout
- Azure login przez OIDC
- setup Terraform `1.7.5`
- `terraform init`
- `terraform fmt -check`
- `terraform validate`
- `terraform plan`
- komentarz z planem na PR
- `terraform apply` po pushu na `projekt_422379`

### CI - Build, Test, Push, Deploy

Trigger:

- push na `projekt_422379`
- zmiany w `Projekt/app/**`
- zmiany w `Projekt/tests/**`
- zmiany w `Projekt/Dockerfile`
- zmiany w `Projekt/k8s/**`
- manualne `workflow_dispatch`

Kroki:

- checkout
- setup Python `3.12`
- testy `unittest`
- Azure login przez OIDC
- setup `kubectl`
- login do ACR
- `docker build`
- `docker push`
- `az aks get-credentials`
- `kubectl apply`
- `kubectl set image`
- `kubectl rollout status`

## OIDC i sekrety

Nie ma stalego sekretu `AZURE_CLIENT_SECRET`.

GitHub Actions loguje sie do Azure przez OIDC:

- GitHub wystawia krotko zyjacy token.
- Azure ufa tokenowi przez federated credential.
- Tozsamosc w Azure: User Assigned Managed Identity.

Role identity:

- `Contributor`
- `User Access Administrator`

Sekrety GitHub:

```text
AZURE_CLIENT_ID_422379
AZURE_TENANT_ID_422379
AZURE_SUBSCRIPTION_ID_422379
TF_STORAGE_ACCOUNT_422379
ACR_LOGIN_SERVER_422379
RESOURCE_GROUP_422379
AKS_NAME_422379
```

Wazne:

- `_422379` jest w nazwach sekretow.
- ACR i Storage Account nie moga miec `_`.

## Kubernetes

Manifest: `k8s/deployment.yaml`.

Zawiera:

- `Deployment` o nazwie `app`
- 2 repliki
- kontener na porcie `8080`
- `readinessProbe` na `/health`
- `livenessProbe` na `/health`
- `Service` typu `LoadBalancer`

Po wdrozeniu:

```powershell
az aks get-credentials `
  --resource-group rg-lab05 `
  --name aks-lab05 `
  --subscription 28a99865-5bf4-4512-84f1-b3103de56b79 `
  --overwrite-existing

kubectl get pods
kubectl rollout status deployment/app
kubectl get svc app-svc
```

Test endpointu:

```powershell
$AppIp = kubectl get svc app-svc -o jsonpath="{.status.loadBalancer.ingress[0].ip}"
Invoke-RestMethod "http://$AppIp/health"
```

Oczekiwany wynik:

```json
{"status":"ok"}
```

## Co jest dowodem dzialania

- Zielony workflow `Terraform - Infrastructure`.
- Zielony workflow `CI - Build, Test, Push, Deploy`.
- `kubectl get pods` pokazuje pody `Running`.
- `kubectl rollout status deployment/app` konczy sie sukcesem.
- `kubectl get svc app-svc` pokazuje `EXTERNAL-IP`.
- `/health` zwraca `{"status":"ok"}`.

## Notatki do obrony

Szczegolowy opis i definicje sa w:

```text
OPIS_PROJEKTU_422379.md
```
