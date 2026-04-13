# Sprawozdanie — Lab 5: Docker Security

**Autor:** Student 888888  
**Data:** 2026-04-13  
**Repozytorium:** DevOps2026 / branch: lab5-test-v2

---

## Cel zadania

Celem laboratorium było zidentyfikowanie i naprawienie 4 problemów bezpieczeństwa w konfiguracji Dockera. Aplikacja działała poprawnie, jednak zawierała poważne luki bezpieczeństwa w plikach `backend/Dockerfile`, `frontend/Dockerfile` oraz `docker-compose.yml`.

---

## BŁĄD 1 — Niespięte wersje obrazów bazowych (`latest`)

### Kod przed naprawą

`backend/Dockerfile`:
```dockerfile
FROM python:latest
```

`frontend/Dockerfile`:
```dockerfile
FROM nginx:latest
```

`docker-compose.yml`:
```yaml
db:
  image: postgres:latest
```

### Zagrożenie bezpieczeństwa

Użycie tagu `latest` oznacza, że przy każdym `docker pull` lub `docker compose build` może zostać pobrany inny obraz — nowsza wersja bazy lub interpretera, która może zawierać przełomowe zmiany (breaking changes), nowe luki CVE lub zmienione zachowanie. W środowisku produkcyjnym brak kontroli nad wersją obrazu prowadzi do nieprzewidywalnych wdrożeń. Dodatkowo audyt bezpieczeństwa wymaga konkretnych wersji, aby móc sprawdzić znane podatności (CVE) dla danej wersji.

### Kod po naprawie

`backend/Dockerfile`:
```dockerfile
FROM python:3.11-slim
```

`frontend/Dockerfile`:
```dockerfile
FROM nginx:1.25-alpine
```

`docker-compose.yml`:
```yaml
db:
  image: postgres:15
```

### Weryfikacja

Sprawdzenie, że używane są konkretne wersje:
```bash
docker images | grep -E "python|nginx|postgres"
# Oczekiwane: python:3.11-slim, nginx:1.25-alpine, postgres:15
```

---

## BŁĄD 2 — Hardkodowane sekrety w Dockerfile (`ENV`)

### Kod przed naprawą

`backend/Dockerfile`:
```dockerfile
ENV API_KEY=super-secret-api-key-abc123
ENV SECRET_KEY=my-secret-key-do-not-share-2026
```

### Zagrożenie bezpieczeństwa

Dyrektywa `ENV` zapisuje wartość w warstwie obrazu Docker. Każdy, kto posiada obraz (po `docker pull` z prywatnego rejestru lub po `git clone` repozytorium), może odczytać te wartości za pomocą:
```bash
docker history <image_name> --no-trunc
docker inspect <image_name>
```
Sekrety w historii warstw są trwale widoczne nawet po ich "usunięciu" w kolejnej warstwie (`RUN unset`). Jest to jedno z najpoważniejszych naruszeń bezpieczeństwa kontenerów.

**Weryfikacja przed naprawą — `docker history` (symulacja):**
```
IMAGE          CREATED BY
<id>           ENV API_KEY=super-secret-api-key-abc123
<id>           ENV SECRET_KEY=my-secret-key-do-not-share-2026
```

### Kod po naprawie

Usunięto linie `ENV` z `backend/Dockerfile`. Sekrety przekazywane są przez `docker-compose.yml` z odwołaniem do pliku `.env`:

`docker-compose.yml`:
```yaml
backend:
  environment:
    API_KEY: ${API_KEY}
    SECRET_KEY: ${SECRET_KEY}
```

`.env` (nie trafia do repozytorium):
```
API_KEY=change-me-in-production
SECRET_KEY=change-me-in-production
```

### Weryfikacja

```bash
docker history lab5_app_888888_backend --no-trunc
# Oczekiwane: brak wartości API_KEY i SECRET_KEY w historii warstw
```

---

## BŁĄD 3 — Hardkodowane hasło w `docker-compose.yml`

### Kod przed naprawą

`docker-compose.yml`:
```yaml
db:
  environment:
    POSTGRES_PASSWORD: "password123"

backend:
  environment:
    DATABASE_URL: postgresql://devops:password123@db:5432/devops_db
```

### Zagrożenie bezpieczeństwa

Hasło zapisane jawnym tekstem w `docker-compose.yml` trafia do repozytorium git. Historia commitów jest trwała — nawet jeśli hasło zostanie usunięte w kolejnym commicie, pozostaje widoczne w historii dla każdego z dostępem do repo (`git log -p`). W przypadku publicznego repozytorium hasło jest dostępne dla wszystkich. W przypadku prywatnego — dla wszystkich współpracowników i potencjalnych atakujących, którzy uzyskają dostęp do repo.

### Kod po naprawie

`docker-compose.yml`:
```yaml
db:
  environment:
    POSTGRES_DB: ${POSTGRES_DB}
    POSTGRES_USER: ${POSTGRES_USER}
    POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}

backend:
  environment:
    DATABASE_URL: postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@db:5432/${POSTGRES_DB}
```

`.env` (dodany do `.gitignore`):
```
POSTGRES_DB=devops_db
POSTGRES_USER=devops
POSTGRES_PASSWORD=devops123
```

`.gitignore`:
```
.env
```

### Weryfikacja

```bash
# Sprawdzenie, że .env nie jest śledzony przez git:
git status
# .env powinien być ignorowany (nie widoczny jako untracked)

# Sprawdzenie, że aplikacja startuje z hasłem z .env:
docker compose up --build
curl http://localhost:5000/health
# Oczekiwane: {"status": "ok"}
```

---

## BŁĄD 4 — Kontener uruchomiony jako root

### Kod przed naprawą

`backend/Dockerfile` — brak dyrektywy `USER`:
```dockerfile
FROM python:latest
WORKDIR /app
# ... brak USER ...
CMD ["gunicorn", "--bind", "0.0.0.0:5000", ...]
```

**Weryfikacja przed naprawą:**
```bash
docker compose exec backend whoami
# Wynik: root
```

### Zagrożenie bezpieczeństwa

Brak dyrektywy `USER` powoduje, że aplikacja wewnątrz kontenera działa z uprawnieniami roota (UID 0). Przy podatności w aplikacji (np. Remote Code Execution — RCE, path traversal) atakujący uzyskuje uprawnienia roota w kontenerze. W połączeniu z błędami konfiguracji hosta (np. podmontowany `/var/run/docker.sock`, `--privileged`, shared namespaces) może to prowadzić do eskalacji uprawnień na host Docker. Zasada najmniejszych uprawnień (Principle of Least Privilege) wymaga, aby procesy działały z minimalnym niezbędnym zestawem uprawnień.

### Kod po naprawie

`backend/Dockerfile`:
```dockerfile
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser
USER appuser
```

Pełny plik po naprawie:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

RUN python -c "import flask; import psycopg2; import gunicorn"

RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser
USER appuser

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--preload", "app:app"]
```

### Weryfikacja

```bash
docker compose exec backend whoami
# Oczekiwane: appuser (nie root)
```

---

## Weryfikacja po naprawie wszystkich błędów

```bash
# Uruchomienie naprawionej aplikacji
docker compose up --build

# Weryfikacja działania API
curl http://localhost:5000/health
# Oczekiwane: {"status": "ok"}

curl http://localhost:5000/items
# Oczekiwane: []

# Weryfikacja użytkownika
docker compose exec backend whoami
# Oczekiwane: appuser

# Weryfikacja historii warstw
docker history lab5_app_888888_backend --no-trunc
# Oczekiwane: brak API_KEY i SECRET_KEY w historii

# Test persystencji
curl -X POST http://localhost:5000/items \
  -H "Content-Type: application/json" \
  -d '{"name": "element testowy"}'

docker compose down
docker compose up -d
curl http://localhost:5000/items
# Oczekiwane: lista z wcześniej dodanym elementem
```

---

## Podsumowanie znalezionych błędów

| Nr | Typ błędu | Plik | Naprawiono |
|----|-----------|------|-----------|
| 1 | Niespięte wersje obrazów (`latest`) | backend/Dockerfile, frontend/Dockerfile, docker-compose.yml | Tak — użyto `python:3.11-slim`, `nginx:1.25-alpine`, `postgres:15` |
| 2 | Hardkodowane sekrety przez `ENV` w Dockerfile | backend/Dockerfile | Tak — usunięto `ENV`, sekrety przekazywane przez `.env` i `docker-compose.yml` |
| 3 | Hardkodowane hasło w `docker-compose.yml` | docker-compose.yml | Tak — użyto zmiennych `${POSTGRES_PASSWORD}` z pliku `.env` |
| 4 | Kontener działa jako root (brak `USER`) | backend/Dockerfile | Tak — dodano użytkownika `appuser` i dyrektywę `USER appuser` |

---

## Tematy dodatkowe

### Docker Content Trust (DCT)

Docker Content Trust to mechanizm weryfikacji autentyczności i integralności obrazów Docker oparty na kryptografii (The Update Framework — TUF). Gdy DCT jest włączony, Docker weryfikuje podpis cyfrowy obrazu przed jego pobraniem.

**Włączenie DCT:**
```bash
export DOCKER_CONTENT_TRUST=1
docker pull python:3.11-slim  # pobierze tylko jeśli obraz jest podpisany
```

W praktyce DCT gwarantuje, że pobierany obraz pochodzi od zaufanego wydawcy i nie został podmieniony (atak man-in-the-middle lub kompromitacja rejestru). Bez DCT atakujący może podmienić obraz w rejestrze na złośliwą wersję — Docker pobierze go bez ostrzeżenia.

### Multi-stage builds

Multi-stage builds pozwalają na zdefiniowanie kilku etapów budowania w jednym Dockerfile. Końcowy obraz zawiera tylko artefakty z ostatniego etapu — bez narzędzi buildowych, kompilatorów i plików tymczasowych.

```dockerfile
# Etap 1: budowanie
FROM python:3.11 AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user -r requirements.txt

# Etap 2: obraz produkcyjny
FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY app.py .
CMD ["python", "app.py"]
```

Zmniejszenie powierzchni ataku polega na tym, że końcowy obraz nie zawiera `pip`, `gcc`, ani innych narzędzi, które mogłyby być wykorzystane przez atakującego do instalacji złośliwego oprogramowania po przejęciu kontenera.

### Docker Secrets vs zmienne środowiskowe

Docker Secrets (`docker secret`) to mechanizm dostępny w Docker Swarm do bezpiecznego przekazywania wrażliwych danych do kontenerów. Sekrety są przechowywane zaszyfrowane w Raft log klastra Swarm i montowane w kontenerze jako pliki w `/run/secrets/`.

```bash
echo "my_secure_password" | docker secret create db_password -
```

W odróżnieniu od zmiennych środowiskowych (które są widoczne w `docker inspect`, logach procesów i mogą wycieknąć przez `/proc/[pid]/environ`), sekrety Swarm:
- nie są widoczne w `docker inspect`
- są dostępne tylko dla kontenerów, które mają do nich przypisany dostęp
- są usuwane z kontenera po jego zatrzymaniu
- są przesyłane do węzłów szyfrowanym kanałem TLS

W środowiskach bez Swarm alternatywą jest HashiCorp Vault lub Kubernetes Secrets.

