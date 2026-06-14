# DevOps 2026 — Projekt na ocenę 4.0

Aplikacja **Calculator API** (Python/Flask) z pełnym potokiem CI/CD:  
**GitHub Actions → Azure Container Registry → Azure Kubernetes Service**

---

## Architektura

```
[Commit / Push]
      │
      ▼
[GitHub Actions CI]
  ├─ pytest (testy jednostkowe)
  ├─ docker build
  └─ docker push → ACR
      │
      ▼
[GitHub Actions CD]
  ├─ az aks get-credentials
  ├─ kubectl apply (Deployment + Service)
  └─ kubectl set image (rolling update)
      │
      ▼
[AKS — 2 repliki kalkulatora]
```

---

## Wymagania wstępne

| Narzędzie | Wersja |
|-----------|--------|
| Azure CLI | ≥ 2.60 |
| Terraform | ≥ 1.7  |
| kubectl   | ≥ 1.28 |
| Docker    | ≥ 24   |
| Python    | ≥ 3.12 |

---

## Krok 1 — Infrastruktura (Terraform)

```bash
cd terraform

# Skopiuj przykładowy plik z wartościami
cp terraform.tfvars.example terraform.tfvars
# ✏️  Uzupełnij terraform.tfvars swoimi wartościami

# Zaloguj się do Azure
az login

# Zainicjuj i wdroż infrastrukturę
terraform init
terraform plan
terraform apply
```

Po `apply` zapisz wyniki outputów:
```bash
terraform output acr_login_server   # np. devops2026acr.azurecr.io
terraform output aks_cluster_name
terraform output resource_group_name
```

---

## Krok 2 — Sekrety GitHub

Przejdź do **Settings → Secrets and variables → Actions** i dodaj:

| Secret | Skąd pobrać |
|--------|-------------|
| `ACR_LOGIN_SERVER` | `terraform output acr_login_server` |
| `ACR_USERNAME` | Portal Azure → ACR → Access keys |
| `ACR_PASSWORD` | Portal Azure → ACR → Access keys |
| `AKS_CLUSTER_NAME` | `terraform output aks_cluster_name` |
| `AZURE_RESOURCE_GROUP` | `terraform output resource_group_name` |
| `AZURE_CREDENTIALS` | patrz niżej |

### Generowanie `AZURE_CREDENTIALS`

```bash
# Pobierz ID subskrypcji
SUBSCRIPTION_ID=$(az account show --query id -o tsv)

# Utwórz Service Principal
az ad sp create-for-rbac \
  --name "github-cicd-sp" \
  --role Contributor \
  --scopes /subscriptions/$SUBSCRIPTION_ID \
  --sdk-auth
```

Skopiuj **cały JSON** jako wartość sekretu `AZURE_CREDENTIALS`.

---

## Krok 3 — Testy lokalne

```bash
pip install flask pytest
pytest tests/ -v
```

---

## Krok 4 — Uruchomienie lokalne (Docker)

```bash
docker build -t calculator .
docker run -p 5000:5000 calculator

# Test
curl http://localhost:5000/health
curl -X POST http://localhost:5000/add \
     -H "Content-Type: application/json" \
     -d '{"a": 10, "b": 5}'
```

---

## Krok 5 — Wdrożenie (CI/CD)

Po skonfigurowaniu sekretów każdy push na branch `main` lub `student/**` uruchamia pipeline:

1. Uruchamia testy (`pytest`)
2. Buduje i publikuje obraz do ACR
3. Aktualizuje deployment w AKS (rolling update)

---

## Endpointy API

| Metoda | Ścieżka | Opis |
|--------|---------|------|
| GET | `/` | Lista endpointów |
| GET | `/health` | Health check |
| POST | `/add` | Dodawanie |
| POST | `/subtract` | Odejmowanie |
| POST | `/multiply` | Mnożenie |
| POST | `/divide` | Dzielenie |

**Przykładowe żądanie:**
```json
POST /add
{ "a": 15, "b": 7 }

→ { "result": 22.0 }
```

---

## Struktura projektu

```
.
├── app/
│   ├── app.py              # Aplikacja Flask
│   └── requirements.txt
├── tests/
│   └── test_app.py         # Testy jednostkowe (pytest)
├── terraform/
│   ├── main.tf             # ACR + AKS
│   ├── variables.tf
│   ├── outputs.tf
│   └── terraform.tfvars.example
├── k8s/
│   ├── deployment.yaml     # Kubernetes Deployment (2 repliki)
│   └── service.yaml        # LoadBalancer Service
├── .github/workflows/
│   └── cicd.yml            # Pipeline CI/CD
├── Dockerfile
└── README.md
```
