# LAB-05 — Pełny GitOps: Terraform przez GHA + remote state

## Cel zadania

Celem jest wyeliminowanie ostatniego ręcznego elementu — lokalnego wykonywania `terraform apply`. Infrastruktura zarządzana jest wyłącznie przez GitHub Actions: każda zmiana w katalogu `infra/` przechodzi przez pull request z automatycznym `terraform plan` jako komentarzem, a merge do `main` wyzwala `terraform apply`. State Terraform przechowywany jest zdalnie w Azure Storage Account — umożliwia to współpracę wielu osób i środowisk bez ryzyka konfliktu stanu.

> **Kontekst:** Niniejszy lab bazuje na LAB-04. Wymagana jest znajomość Terraform, GitHub Actions i konfiguracji Azure z poprzednich zadań.

---

## Wymagania wstępne

- Uprawnienia do tworzenia Storage Account 
- Zainstalowane lokalnie: `terraform`, `az` CLI (do bootstrapu)

---

## Architektura

```
GitHub Repo
    │                              │
    │ Plan and apply (GHA)         │ Build Pipeline
    │                              │ Test + Update Obrazu
    ▼                              ▼
Azure via Terraform          Azure Container Registry
    │    │                              │
    │    └──▶ Storage Account           ▼
    │          (TF state file)    Azure Kubernetes Service
    │
    └──▶ ACR + AKS (provisioned)
```

---

## Krok 1 — Bootstrap: Storage Account na remote state

Przed użyciem Terraform z backendem zdalnym konieczne jest jednorazowe utworzenie Storage Account. Nie może to być wykonane przez sam Terraform — chicken-and-egg problem.

Należy wykonać skrypt bootstrapowy **lokalnie, jednorazowo**:

```bash
RESOURCE_GROUP="rg-tf-state"
STORAGE_ACCOUNT="stlab05tfstate<suffix>"   # nazwa globalna, 3–24 znaki, tylko [a-z0-9]
CONTAINER_NAME="tfstate"
LOCATION="westeurope"

az group create \
  --name $RESOURCE_GROUP \
  --location $LOCATION

az storage account create \
  --resource-group $RESOURCE_GROUP \
  --name $STORAGE_ACCOUNT \
  --sku Standard_LRS \
  --encryption-services blob

az storage container create \
  --name $CONTAINER_NAME \
  --account-name $STORAGE_ACCOUNT
```

> **Uwaga:** Nazwy tych zasobów należy zanotować — będą potrzebne w bloku `backend` Terraform oraz w sekretach GitHub.

---

## Krok 2 — Konfiguracja remote backend w Terraform

### 2.1 Blok backend

Należy dodać blok `backend "azurerm"` do pliku `infra/main.tf` lub osobnego pliku `infra/backend.tf`:

```hcl
terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.90"
    }
  }

  backend "azurerm" {
    resource_group_name  = "rg-tf-state"
    storage_account_name = "stlab05tfstate<suffix>"
    container_name       = "tfstate"
    key                  = "lab05.terraform.tfstate"
  }
}
```

Po dodaniu bloku należy wykonać jednorazowo lokalnie:

```bash
cd infra/
terraform init -migrate-state   # migruje lokalny state do remote backendu
```

Od tego momentu lokalny plik `terraform.tfstate` jest pusty i można go usunąć.

---

## Krok 3 — Autoryzacja GitHub Actions do Azure (OIDC)

Zamiast długożyciowych sekretów service principal zalecane jest użycie Workload Identity Federation (OIDC). Nie są wtedy potrzebne wygasające klucze.


### 3.3 Sekrety GitHub dla OIDC

W ustawieniach repozytorium należy dodać:

| Nazwa sekretu | Wartość |
|---|---|
| `AZURE_CLIENT_ID` | `$APP_ID` |
| `AZURE_TENANT_ID` | ID tenanta |
| `AZURE_SUBSCRIPTION_ID` | ID subskrypcji |
| `TF_STORAGE_ACCOUNT` | Nazwa Storage Account z TF state |
| `ACR_LOGIN_SERVER` | Pełna domena ACR |
| `AKS_NAME` | Nazwa klastra AKS |
| `RESOURCE_GROUP` | Grupa zasobów ACR + AKS |


---

## Krok 4 — Workflow infrastrukturowy

Należy utworzyć plik `.github/workflows/infra.yml`:

```yaml
name: Terraform — Infrastruktura

on:
  push:
    branches: [main]
    paths: [infra/**]
  pull_request:
    paths: [infra/**]

permissions:
  id-token: write       # wymagane dla OIDC
  contents: read
  pull-requests: write  # wymagane do dodawania komentarza z planem

concurrency:
  group: terraform
  cancel-in-progress: false   # nigdy nie anuluj trwającego apply

jobs:
  terraform:
    runs-on: ubuntu-latest
    env:
      ARM_CLIENT_ID: ${{ secrets.AZURE_CLIENT_ID }}
      ARM_TENANT_ID: ${{ secrets.AZURE_TENANT_ID }}
      ARM_SUBSCRIPTION_ID: ${{ secrets.AZURE_SUBSCRIPTION_ID }}
      ARM_USE_OIDC: "true"

    steps:
      - uses: actions/checkout@v4

      - uses: hashicorp/setup-terraform@v3
        with:
          terraform_version: "~1.7"

      - name: Terraform Init
        working-directory: infra
        run: terraform init

      - name: Terraform Format Check
        working-directory: infra
        run: terraform fmt -check

      - name: Terraform Validate
        working-directory: infra
        run: terraform validate

      - name: Terraform Plan
        id: plan
        working-directory: infra
        run: terraform plan -no-color -out=tfplan
        continue-on-error: true

      - name: Dodaj komentarz z planem do PR
        if: github.event_name == 'pull_request'
        uses: actions/github-script@v7
        with:
          script: |
            const plan = `${{ steps.plan.outputs.stdout }}`.substring(0, 65000);
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: `### Terraform Plan\n\`\`\`terraform\n${plan}\n\`\`\``
            });

      - name: Terraform Apply
        if: github.ref == 'refs/heads/main' && github.event_name == 'push'
        working-directory: infra
        run: terraform apply -auto-approve tfplan
```

---

## Krok 5 — Workflow aplikacyjny


```yaml
name: CI — Build, Test, Push, Deploy

on:
  push:
    branches: [main]
    paths:
      - app/**
      - Dockerfile
      - k8s/**

permissions:
  id-token: write
  contents: read

jobs:
  ci-cd:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Uruchom testy
        run: pytest

      - name: Zaloguj się do Azure (OIDC)
        uses: azure/login@v2
        with:
          client-id: ${{ secrets.AZURE_CLIENT_ID }}
          tenant-id: ${{ secrets.AZURE_TENANT_ID }}
          subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}

      - name: Zaloguj się do ACR
        run: az acr login --name ${{ secrets.ACR_LOGIN_SERVER }}

      - name: Zbuduj i wypchnij obraz
        run: |
          IMAGE=${{ secrets.ACR_LOGIN_SERVER }}/app:${{ github.sha }}
          docker build -t $IMAGE .
          docker push $IMAGE

      - name: Pobierz kubeconfig AKS
        run: |
          az aks get-credentials \
            --resource-group ${{ secrets.RESOURCE_GROUP }} \
            --name ${{ secrets.AKS_NAME }} \
            --overwrite-existing

      - name: Zaktualizuj obraz w AKS
        run: |
          kubectl set image deployment/app \
            app=${{ secrets.ACR_LOGIN_SERVER }}/app:${{ github.sha }}
          kubectl rollout status deployment/app --timeout=120s
```

### Separacja triggerów

Workflow `infra.yml` odpala się wyłącznie przy zmianach w katalogu `infra/`. Workflow `ci.yml` odpala się przy zmianach w `app/`, `Dockerfile` lub `k8s/`. Zmiana kodu aplikacji nie powinna odpalać Terraform i odwrotnie.

