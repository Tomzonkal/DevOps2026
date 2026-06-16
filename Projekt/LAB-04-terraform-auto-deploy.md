# LAB-04 — Infrastruktura jako kod + automatyczny deployment

## Cel zadania

Celem jest wyeliminowanie ręcznych kroków przy tworzeniu infrastruktury Azure oraz przy aktualizacji obrazu w klastrze Kubernetes. Infrastruktura — ACR i AKS — opisywana jest w Terraform i może być odtworzona deterministycznie. Pipeline GitHub Actions realizuje pełny cykl: build → test → push → rollout w AKS, bez konieczności ingerencji człowieka po każdym commicie.

> **Kontekst:** Niniejszy lab bazuje na LAB-03. Zakłada się znajomość konfiguracji GitHub Actions, ACR i AKS z poprzedniego zadania.

---

## Wymagania wstępne

- Zainstalowane lokalnie: `terraform` (>= 1.5), `az` CLI, `kubectl`
- Service principal z uprawnieniami `Contributor` na subskrypcji lub dedykowanej grupie zasobów

---

## Architektura

```
GitHub Repo
    │
    │  (Build Pipeline + Test + Update Obrazu)
    ▼
Azure Container Registry
    │
    ▼
Azure Kubernetes Service
    ▲
    │
Azure via Terraform
(może być apply ręcznie)
```

---

## Krok 1 — Struktura projektu

Należy zorganizować repozytorium według następującego układu katalogów:

```
.
├── .github/
│   └── workflows/
│       └── ci.yml
├── infra/
│   ├── main.tf
│   ├── variables.tf
│   ├── outputs.tf
│   └── terraform.tfvars      ← NIE commitować do repo jeśli zawiera sekrety
├── k8s/
│   └── deployment.yaml
├── app/
│   └── ...
└── Dockerfile
```

---

## Krok 2 — Kod Terraform

### 2.1 Provider i zmienne

Plik `infra/variables.tf`:

```hcl
variable "resource_group_name" {
  type    = string
  default = "rg-lab04"
}

variable "location" {
  type    = string
  default = "westeurope"
}

variable "acr_name" {
  type = string
}

variable "aks_name" {
  type    = string
  default = "aks-lab04"
}
```

### 2.2 Zasoby główne

Plik `infra/main.tf`:

```hcl
terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.90"
    }
  }
}

provider "azurerm" {
  features {}
}

resource "azurerm_resource_group" "main" {
  name     = var.resource_group_name
  location = var.location
}

resource "azurerm_container_registry" "main" {
  name                = var.acr_name
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  sku                 = "Basic"
  admin_enabled       = false
}

resource "azurerm_kubernetes_cluster" "main" {
  name                = var.aks_name
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  dns_prefix          = var.aks_name

  default_node_pool {
    name       = "default"
    node_count = 1
    vm_size    = "Standard_B2s"
  }

  identity {
    type = "SystemAssigned"
  }
}

resource "azurerm_role_assignment" "aks_acr_pull" {
  scope                = azurerm_container_registry.main.id
  role_definition_name = "AcrPull"
  principal_id         = azurerm_kubernetes_cluster.main.kubelet_identity[0].object_id
}
```

### 2.3 Outputs

Plik `infra/outputs.tf`:

```hcl
output "acr_login_server" {
  value = azurerm_container_registry.main.login_server
}

output "aks_name" {
  value = azurerm_kubernetes_cluster.main.name
}

output "resource_group_name" {
  value = azurerm_resource_group.main.name
}
```

### 2.4 Zastosowanie infrastruktury

Infrastrukturę należy zaaplikować lokalnie z katalogu `infra/`:

```bash
terraform init
terraform plan -var="acr_name=acrlab04<suffix>"
terraform apply -var="acr_name=acrlab04<suffix>"
```

> **Uwaga:** State Terraform jest w tym labie przechowywany lokalnie (`terraform.tfstate`). Plik ten należy dodać do `.gitignore`. Problem lokalnego state zostanie rozwiązany w LAB-05.

---

## Krok 3 — Zaktualizowany workflow GitHub Actions

### 3.1 Nowy krok: aktualizacja obrazu w AKS

Workflow należy rozbudować o kroki logowania do Azure i aktualizacji deploymenta:

```yaml
name: CI — Build, Test, Push, Deploy

on:
  push:
    branches: [main]

jobs:
  ci-cd:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Uruchom testy
        run: pytest   # dostosować do stacku

      - name: Zaloguj się do Azure
        uses: azure/login@v1
        with:
          creds: ${{ secrets.AZURE_CREDENTIALS }}

      - name: Zaloguj się do ACR
        run: az acr login --name ${{ secrets.ACR_NAME }}

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

### 3.2 Wymagane sekrety GitHub

| Nazwa sekretu | Wartość |
|---|---|
| `AZURE_CREDENTIALS` | JSON z service principal (`az ad sp create-for-rbac --sdk-auth`) |
| `ACR_NAME` | Nazwa ACR bez domeny |
| `ACR_LOGIN_SERVER` | Pełna domena ACR |
| `AKS_NAME` | Nazwa klastra AKS |
| `RESOURCE_GROUP` | Nazwa grupy zasobów |

---

## Krok 4 — Manifest Kubernetes

Manifest w `k8s/deployment.yaml` nie musi zawierać hardcodowanego tagu — `kubectl set image` nadpisuje go dynamicznie:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app
spec:
  replicas: 2
  selector:
    matchLabels:
      app: app
  template:
    metadata:
      labels:
        app: app
    spec:
      containers:
        - name: app
          image: placeholder   # nadpisywane przez kubectl set image
          ports:
            - containerPort: 8080
```

Manifest należy zastosować jednorazowo po pierwszym `terraform apply`:

```bash
az aks get-credentials --resource-group rg-lab04 --name aks-lab04
kubectl apply -f k8s/deployment.yaml
```

Kolejne deploye realizowane są wyłącznie przez pipeline.

