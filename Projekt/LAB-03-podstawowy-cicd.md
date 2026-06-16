# LAB-03 — Podstawowy pipeline CI/CD z ręcznym deploymentem

## Cel zadania

Celem jest zbudowanie pierwszego pipeline CI/CD w GitHub Actions, który automatycznie buduje, testuje i publikuje obraz Docker do Azure Container Registry. Infrastruktura Azure tworzona jest ręcznie. Aktualizacja obrazu w klastrze Kubernetes również wymaga ręcznej interwencji — pozwala to dostrzec ograniczenia takiego podejścia i zrozumieć motywację do automatyzacji w kolejnych labach.

---

## Wymagania wstępne

- Dostęp do konta Azure z uprawnieniami do tworzenia zasobów
- Zainstalowane lokalnie: `az` CLI, `kubectl`, `docker`
- Konto GitHub z możliwością tworzenia repozytoriów

---

## Architektura

```
GitHub Repo
    │
    │  (Build Pipeline + Test)
    ▼
Azure Container Registry   ──── (Update obrazu — ręcznie) ────▶  Azure Kubernetes Service
```

---

## Krok 1 — Przygotowanie repozytorium

Należy utworzyć repozytorium GitHub zawierające:

- kod aplikacji webowej (dowolny framework lub prosta aplikacja w Pythonie/Node.js/Go),
- plik `Dockerfile` budujący obraz aplikacji,
- co najmniej jeden test jednostkowy lub endpoint `/health` weryfikowany w pipeline,
- plik `README.md` z opisem projektu.

> **Uwaga:** Obraz powinien być możliwy do uruchomienia lokalnie poleceniem `docker build` i `docker run` przed przystąpieniem do konfiguracji pipeline.

---

## Krok 2 — Ręczne utworzenie infrastruktury Azure

### 2.1 Azure Container Registry

Należy utworzyć rejestr kontenerów za pomocą portalu Azure lub polecenia CLI:

```bash
az group create --name rg-lab03 --location westeurope

az acr create \
  --resource-group rg-lab03 \
  --name <nazwa-acr> \
  --sku Basic
```

Należy zanotować pełną nazwę rejestru w formacie `<nazwa-acr>.azurecr.io` — będzie potrzebna w konfiguracji pipeline.

### 2.2 Azure Kubernetes Service

Należy utworzyć klaster AKS z minimalną konfiguracją (1–2 węzły) oraz podłączyć go do ACR:

```bash
az aks create \
  --resource-group rg-lab03 \
  --name aks-lab03 \
  --node-count 1 \
  --generate-ssh-keys \
  --attach-acr <nazwa-acr>

az aks get-credentials \
  --resource-group rg-lab03 \
  --name aks-lab03
```

Opcja `--attach-acr` konfiguruje dostęp klastra do rejestru przez managed identity — nie jest wymagane stosowanie `imagePullSecret`.

---

## Krok 3 — Konfiguracja GitHub Actions

### 3.1 Sekrety repozytorium

W ustawieniach repozytorium (`Settings → Secrets and variables → Actions`) należy dodać następujące sekrety:

| Nazwa sekretu | Wartość |
|---|---|
| `AZURE_CLIENT_ID` | ID aplikacji service principal |
| `AZURE_CLIENT_SECRET` | Sekret aplikacji service principal |
| `AZURE_TENANT_ID` | ID tenanta Azure |
| `AZURE_SUBSCRIPTION_ID` | ID subskrypcji Azure |
| `ACR_LOGIN_SERVER` | `<nazwa-acr>.azurecr.io` |

### 3.2 Plik workflow

Należy utworzyć plik `.github/workflows/ci.yml` realizujący następującą sekwencję:

```yaml
name: CI — Build, Test, Push

on:
  push:
    branches: [main]

jobs:
  build-test-push:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Uruchom testy
        run: |
          # przykład dla aplikacji Python
          pip install -r requirements.txt
          pytest

      - name: Zaloguj się do ACR
        uses: azure/docker-login@v1
        with:
          login-server: ${{ secrets.ACR_LOGIN_SERVER }}
          username: ${{ secrets.AZURE_CLIENT_ID }}
          password: ${{ secrets.AZURE_CLIENT_SECRET }}

      - name: Zbuduj i wypchnij obraz
        run: |
          IMAGE=${{ secrets.ACR_LOGIN_SERVER }}/app:${{ github.sha }}
          docker build -t $IMAGE .
          docker push $IMAGE
```

> **Ważne:** Należy używać tagu `${{ github.sha }}` zamiast `:latest`. Stosowanie tagu `:latest` jest antywzorcem w CI/CD — nie pozwala jednoznacznie powiązać obrazu z konkretnym commitem i uniemożliwia wymuszenie nowego rolloutu w Kubernetes.

---

## Krok 4 — Deployment aplikacji do AKS (ręczny)

### 4.1 Manifest Kubernetes

Należy przygotować plik `k8s/deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app
spec:
  replicas: 1
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
          image: <nazwa-acr>.azurecr.io/app:<TAG>
          ports:
            - containerPort: 8080
---
apiVersion: v1
kind: Service
metadata:
  name: app-svc
spec:
  type: LoadBalancer
  selector:
    app: app
  ports:
    - port: 80
      targetPort: 8080
```

### 4.2 Pierwsze wdrożenie

```bash
kubectl apply -f k8s/deployment.yaml
kubectl get pods
kubectl get svc app-svc
```

### 4.3 Aktualizacja obrazu po każdym nowym buildzie

Po zakończeniu pipeline należy ręcznie zaktualizować obraz w klastrze, podając tag odpowiadający SHA commita z pipeline:

```bash
kubectl set image deployment/app \
  app=<nazwa-acr>.azurecr.io/app:<git-sha>
```

Należy obserwować rollout:

```bash
kubectl rollout status deployment/app
```


