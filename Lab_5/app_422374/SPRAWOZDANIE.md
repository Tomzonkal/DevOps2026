# Sprawozdanie z laboratoriów — DevOps 2026

## Laboratorium 5: Docker Security — diagnoza i naprawa problemów bezpieczeństwa w obrazach i Compose

| | |
|---|---|
| **Autor** | Grzegorz Paszek |
| **Nr indeksu** | 422374 |
| **Gałąź** | `lab_5/new_branch_422374` |
| **Repozytorium** | `Tomzonkal/DevOps2026` |

---

## Spis treści

1. [Cel laboratorium](#1-cel-laboratorium)
2. [Środowisko i narzędzia](#2-środowisko-i-narzędzia)
3. [Wstęp teoretyczny](#3-wstęp-teoretyczny)
4. [Przebieg laboratorium](#4-przebieg-laboratorium)
5. [Diagnoza i naprawa 4 błędów](#5-diagnoza-i-naprawa-4-błędów)
6. [Weryfikacja działania (curl)](#6-weryfikacja-działania-curl)
7. [Weryfikacja persystencji danych](#7-weryfikacja-persystencji-danych)
8. [Tematy dodatkowe](#8-tematy-dodatkowe)
9. [Napotkane problemy i wnioski](#9-napotkane-problemy-i-wnioski)

---

## 1. Cel laboratorium

W odróżnieniu od Lab 4 — gdzie aplikacja po prostu *nie działała* — w Lab 5 aplikacja **działa poprawnie**, ale jej konfiguracja zawiera poważne problemy bezpieczeństwa. Zadanie polegało na:

- przejrzeniu plików `Dockerfile` (backend, frontend) i `docker-compose.yml`,
- zidentyfikowaniu **czterech** zdefiniowanych w README błędów bezpieczeństwa (z pomocą LLM jako narzędzia do security review),
- wdrożeniu poprawek zgodnych z dobrymi praktykami Dockera (pinowanie wersji, sekrety poza obrazem, użytkownik nie-root),
- udokumentowaniu *dlaczego* każda z luk była groźna i jak została naprawiona.

---

## 2. Środowisko i narzędzia

| Narzędzie | Wersja | Rola |
|---|---|---|
| Docker Engine | 29.4.0 | runtime kontenerów |
| Docker Compose | v2.39.1 | orkiestracja wieloserwisowa |
| PostgreSQL (image) | `postgres:15` (po naprawie) | baza danych |
| Python (image) | `python:3.11-slim` (po naprawie) | runtime backendu |
| Nginx (image) | `nginx:1.25-alpine` (po naprawie) | frontend |
| Flask | 3.0.3 | framework REST API |
| psycopg2-binary | 2.9.9 | klient PostgreSQL |
| gunicorn | 22.0.0 | serwer WSGI |
| `curl` | 8.x | weryfikacja endpointów |
| LLM (Claude) | — | pomocnik do security review |

---

## 3. Wstęp teoretyczny

### Dlaczego bezpieczeństwo kontenerów ma znaczenie

Mit „kontener jest izolowany, więc jest bezpieczny" jest niebezpiecznie błędny. Kontener współdzieli kernel z hostem; ucieczka z kontenera zwykle prowadzi prosto do hosta. Najczęstsze klasy błędów:

- **Wycieki sekretów w warstwach obrazu.** Każda dyrektywa `ENV`, `ARG`, `COPY` i `RUN` w `Dockerfile` tworzy warstwę. Warstwy są publicznie odczytywalne dla każdego, kto ma obraz: `docker history`, `docker inspect`, `docker save | tar -xvf`. Sekret raz wpisany w `Dockerfile` zostaje w obrazie *na zawsze* — usunięcie go w późniejszej warstwie *nie* czyści warstwy z którą wszedł.
- **Eskalacja uprawnień przez `root` w kontenerze.** Bez dyrektywy `USER` aplikacja działa jako uid 0. Jeśli atakujący uzyska RCE w aplikacji, ma od razu rootowy proces wewnątrz kontenera — co dramatycznie ułatwia wykorzystanie podatności kernela, kradzież montowanych woluminów lub sieci.
- **Niespięte tagi wersji.** `image:latest` w produkcji to sabotaż. Obraz pod tym tagiem zmienia się w czasie — *ten sam* `docker compose up --build` w środę i w piątek może przynieść inną wersję bazy lub runtime'u.
- **Hasła w plikach repo.** `docker-compose.yml` trafia do gita razem z całym kodem. Hasło wpisane jawnym tekstem zostaje w *historii* commits — jego usunięcie w nowszym commicie nie usuwa go z `git log -p`. Nawet jeśli repo jest prywatne, to atakujący po wycieku tokenów CI/CD ma natychmiastowy dostęp do hasła.

### LLM jako narzędzie do security review

W tym laboratorium świadomie użyto LLM (Claude) do analizy plików `Dockerfile` i `docker-compose.yml`. Procedura wyglądała następująco:

1. Wklejenie zawartości plików do modelu z pytaniem: *„wskaż problemy bezpieczeństwa w tej konfiguracji Dockera"*.
2. Otrzymanie listy hipotez, np. „obraz `python:latest` — niespięta wersja", „`ENV API_KEY=...` — sekret w warstwie obrazu", „`POSTGRES_PASSWORD: password123` — hasło hardkodowane w pliku do repo", „brak `USER` w Dockerfile — kontener uruchamia się jako root".
3. Każdą hipotezę zweryfikowano komendą lub ręcznie: `docker history` faktycznie pokazał wartości sekretów w warstwach; `docker compose exec backend whoami` zwracał `root`; `git log` na pliku `docker-compose.yml` pokazałby hasło w historii; `docker inspect` zwraca kompletną listę zmiennych.

Praktyczna obserwacja: **LLM nie zastępuje audytu — przyspiesza wstępne wykrycie**. Każdą sugestię trzeba zweryfikować, bo model bywa pewny rzeczy, których w pliku nie ma. Z drugiej strony przy oczywistych klasach problemów (sekrety w `ENV`, brak `USER`, `latest`) Claude trafia praktycznie zawsze.

---

## 4. Przebieg laboratorium

### Krok 1 — Aktualizacja repo

```bash
git fetch --all
git checkout main
git pull
```

### Krok 2 — Utworzenie gałęzi

```bash
git switch lab_5/new_branch_422374
```

(Branch o tej nazwie istniał już zdalnie — przełączyłem się na niego, zamiast tworzyć kolejny.)

### Krok 3 — Przygotowanie środowiska

```bash
cp -r Lab_5/app_0000 Lab_5/app_422374
cp Lab_5/app_422374/.env.example Lab_5/app_422374/.env
```

Plik `.env`:

```env
POSTGRES_DB=devops_db
POSTGRES_USER=devops
POSTGRES_PASSWORD=devops123
API_KEY=change-me-in-production
SECRET_KEY=change-me-in-production
```

### Krok 4 — Pierwsze uruchomienie i wstępna inspekcja (przed naprawą)

```bash
cd Lab_5/app_422374
docker compose up --build
```

**Pierwsze uruchomienie skończyło się błędem buildu backendu:**

```text
#18 6.690       error: command '/usr/bin/gcc' failed with exit code 1
#18 6.691   ERROR: Failed building wheel for psycopg2-binary
target backend: failed to solve: process "/bin/sh -c pip install --no-cache-dir -r
   requirements.txt" did not complete successfully: exit code: 1
```

Diagnoza: tag `python:latest` pociąga obecnie Pythona **3.14**, w którym `psycopg2-binary==2.9.9` (wersja z `requirements.txt`) nie ma jeszcze prebuilt wheela i próbuje skompilować źródła z C, używając `_PyInterpreterState_Get()` — funkcji prywatnej, usuniętej z publicznego API w 3.13/3.14. **To w praktyce manifestacja BŁĘDU 1** — niespiętej wersji.

Dla zebrania dowodów `docker history` (sekrety w warstwach) i `docker compose exec backend whoami` (root) musiałem mieć działający build. Tymczasowo zmieniłem **tylko** `FROM python:latest` → `FROM python:3.11-slim` i `image: postgres:latest` → `image: postgres:15` (drugi tag również się popsuł — `postgres:latest` to dziś PG 18+, który wymaga innego layoutu wolumenu i odmawia startu na starym mountpointcie). Pozostałe trzy błędy (`ENV` z sekretami, hasło w compose, brak `USER`) zostały **niepoprawione** w tej fazie demonstracyjnej.

Po tym minimalnym workaroundzie aplikacja wystartowała:

```text
NAME                   STATUS
app_422374-db-1        Up (healthy)
app_422374-backend-1   Up
```

**Inspekcja warstw obrazu (przed naprawą BŁĘDU 2):**

```bash
$ docker history app_422374-backend --no-trunc | grep -E "API_KEY|SECRET_KEY"
<missing>  2 days ago   ENV SECRET_KEY=my-secret-key-do-not-share-2026   0B   buildkit.dockerfile.v0
<missing>  2 days ago   ENV API_KEY=super-secret-api-key-abc123          0B   buildkit.dockerfile.v0
```

Obie wartości sekretów są jawnie widoczne w historii warstw obrazu — każdy, kto pobierze obraz `app_422374-backend`, zobaczy je `docker history`em.

**Sprawdzenie użytkownika kontenera (przed naprawą BŁĘDU 4):**

```bash
$ docker compose exec backend whoami
root
```

Backend uruchamia się jako `root`. Po tej obserwacji zatrzymałem aplikację i przystąpiłem do realnej naprawy.

```bash
docker compose down -v
```

---

## 5. Diagnoza i naprawa 4 błędów

### BŁĄD 1 — Niespięte wersje obrazów bazowych (`latest`)

**Co było błędem (przed):**

```dockerfile
# backend/Dockerfile
FROM python:latest
```
```dockerfile
# frontend/Dockerfile
FROM nginx:latest
```
```yaml
# docker-compose.yml
db:
  image: postgres:latest
```

**Zagrożenie bezpieczeństwa:**

Tag `latest` jest *aliasem mutowalnym*. Wskazuje on na obraz, który Docker Hub uznaje aktualnie za „najnowszy stabilny", ale ten alias zmienia się każdorazowo, gdy pojawia się nowe wydanie. Konsekwencje produkcyjne:

- **Nieprzewidywalność wdrożeń.** Ten sam `docker compose up --build` w środę pociągnie Pythona 3.13, a w piątek 3.14 — co realnie zaobserwowałem w tym labie (`psycopg2-binary 2.9.9` nie buduje się na 3.14). To samo dotknęło Postgresa: `latest` to dziś PG 18, który zmienił layout `PGDATA` i odmawia startu na starym wolumenie.
- **Atak supply-chain.** Jeżeli ktoś przejmie konto upstream i wypuści złośliwą wersję pod tagiem `latest`, twój kolejny build wciąga ją bez ostrzeżenia.
- **Brak reprodukowalności.** Build z marca i build z lipca dadzą różne obrazy — debugowanie staje się eksperymentalne.

**Po naprawie:**

```dockerfile
# backend/Dockerfile
FROM python:3.11-slim
```
```dockerfile
# frontend/Dockerfile
FROM nginx:1.25-alpine
```
```yaml
# docker-compose.yml
db:
  image: postgres:15
```

**Weryfikacja:**

```bash
$ docker compose up --build -d
[+] Running 4/4
 ✔ Network app_422374_app_network  Created
 ✔ Volume "app_422374_postgres_data"  Created
 ✔ Container app_422374-db-1        Healthy
 ✔ Container app_422374-backend-1   Started
```

Build kończy się powodzeniem powtarzalnie. `docker compose ps` pokazuje wybrane konkretne wersje — `postgres:15`, a obraz backendu jest zbudowany z `python:3.11-slim` (widoczne w `docker history`).

---

### BŁĄD 2 — Hardkodowane sekrety w Dockerfile (`ENV`)

**Co było błędem (przed):**

```dockerfile
# backend/Dockerfile
FROM python:latest

WORKDIR /app

ENV API_KEY=super-secret-api-key-abc123
ENV SECRET_KEY=my-secret-key-do-not-share-2026
```

**Zagrożenie bezpieczeństwa:**

Dyrektywa `ENV` w `Dockerfile` zapisuje wartość **trwale w warstwie obrazu**. To nie jest „runtime environment variable" w klasycznym sensie — to instrukcja zapisywana w manifeście obrazu. Konsekwencje:

- **Każdy, kto ma obraz, ma sekret.** `docker history --no-trunc` rzuca wszystkie warstwy z dyrektywami; `docker inspect` zwraca pełną listę `Env`. Pokazałem to w sekcji 4 — `API_KEY=super-secret-api-key-abc123` i `SECRET_KEY=my-secret-key-do-not-share-2026` są dosłownie widoczne na wyjściu komendy.
- **Sekret zostaje w *każdej* warstwie zbudowanej *po* niej.** Nie da się go usunąć przez „zmianę `ENV` na pustą wartość później" — usuwasz go z aktualnej wartości runtime, ale warstwa, w której zapisałeś sekret, pozostaje w łańcuchu obrazu.
- **Sekret wycieka razem z obrazem.** Push do prywatnego registry, który ma niefortunny IP allowlist; lub klon repo z `Dockerfile` przez stażystę, który wpadł w phishing — i sekret jest na zewnątrz.

**Po naprawie:**

Linie `ENV API_KEY=...` i `ENV SECRET_KEY=...` zostały **usunięte** z `backend/Dockerfile`. Wartości przekazywane są z pliku `.env` przez sekcję `environment:` w `docker-compose.yml`:

```dockerfile
# backend/Dockerfile (po naprawie)
FROM python:3.11-slim

RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

RUN python -c "import flask; import psycopg2; import gunicorn"

RUN chown -R appuser:appgroup /app

USER appuser

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--preload", "app:app"]
```

```yaml
# docker-compose.yml (fragment)
backend:
  environment:
    DATABASE_URL: postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@db:5432/${POSTGRES_DB}
    API_KEY: ${API_KEY}
    SECRET_KEY: ${SECRET_KEY}
```

Plik `.env` (lokalny, **nie** trafia do gita — patrz `.gitignore`):

```env
API_KEY=change-me-in-production
SECRET_KEY=change-me-in-production
```

**Dlaczego to różnica:** `environment:` w Compose ustawia zmienne na poziomie *runtime kontenera*, nie wpisuje ich do warstw obrazu. Ten sam obraz może być uruchamiany w dev / staging / prod z innym zestawem sekretów — sekrety są zewnętrzne wobec artefaktu obrazu.

**Weryfikacja:**

```bash
$ docker history app_422374-backend --no-trunc | grep -E "API_KEY|SECRET_KEY|my-secret-key|super-secret"
(brak wystapien sekretow w historii warstw)
```

W warstwach obrazu **nie ma już** żadnych śladów `API_KEY` ani `SECRET_KEY`. Aplikacja ma do nich dostęp tylko przez środowisko procesu, ustawione przy `docker compose up`.

---

### BŁĄD 3 — Hardkodowane hasło w `docker-compose.yml`

**Co było błędem (przed):**

```yaml
db:
  image: postgres:latest
  environment:
    POSTGRES_DB: devops_db
    POSTGRES_USER: devops
    POSTGRES_PASSWORD: "password123"

backend:
  environment:
    DATABASE_URL: postgresql://devops:password123@db:5432/devops_db
```

**Zagrożenie bezpieczeństwa:**

`docker-compose.yml` jest plikiem repo — trafia do gita w pierwszym `git add .`. Hasło wpisane jawnie:

- **Zostaje w historii commitów.** `git log -p docker-compose.yml` pokazuje je nawet jeśli „naprawisz" hasło późniejszym commitem. Jedyny sposób na realne usunięcie to przepisanie historii (`git filter-repo`) i wymuszenie pushu — czego w zespole nie chcesz robić.
- **Jest widoczne dla każdego z dostępem do repo.** W większości firm to dziesiątki–setki osób, w tym kontraktorzy z czasowymi tokenami.
- **Lakuje też do CI/CD logów i mirrorów.** Każdy pipeline, który robi `cat docker-compose.yml` lub `docker compose config`, propaguje sekret dalej.

Dodatkowo to *konkretnie to samo hasło* zapisano w dwóch miejscach (`POSTGRES_PASSWORD` i w stringu `DATABASE_URL`) — rotacja jest podatna na desynchronizację, bo łatwo zmienić jedną z dwóch wartości i zepsuć aplikację.

**Po naprawie:**

```yaml
db:
  image: postgres:15
  environment:
    POSTGRES_DB: ${POSTGRES_DB}
    POSTGRES_USER: ${POSTGRES_USER}
    POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}

backend:
  environment:
    DATABASE_URL: postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@db:5432/${POSTGRES_DB}
```

Wartości pochodzą z pliku `.env`, a `.env` został dodany do `.gitignore`:

```gitignore
.env
```

**Dlaczego to różnica:** plik `.env` istnieje *tylko lokalnie*; w repozytorium jest jego szablon `.env.example` z placeholder-ami (`change-me-in-production`). Każda instancja (dev, staging, prod) ma własny `.env` z własnym hasłem, dostarczany kanałem out-of-band (vault, sealed-secrets, ręcznie). Repo nie ma żadnej referencji do realnych haseł.

**Weryfikacja:**

```bash
$ grep -RE "password123" Lab_5/app_422374/
(brak wystapien)

$ docker compose config | grep -E "PASSWORD|password"
      POSTGRES_PASSWORD: devops123
      DATABASE_URL: postgresql://devops:devops123@db:5432/devops_db
```

W samych plikach repozytorium hasła nie ma. `docker compose config` rozwija je z `.env` *tylko w runtime*, na potrzeby uruchomienia.

---

### BŁĄD 4 — Kontener uruchomiony jako root

**Co było błędem (przed):**

`backend/Dockerfile` nie zawierał ani dyrektywy `RUN adduser ...`, ani `USER`. W efekcie domyślny user obrazu `python:latest`/`python:3.11-slim` to uid 0.

```bash
$ docker compose exec backend whoami
root
```

**Zagrożenie bezpieczeństwa:**

Procesy wewnątrz kontenera mają uprawnienia tożsame z użytkownikiem, którego nadano. Jeśli backend Flask ma podatność RCE (np. niezabezpieczony `eval()`, deserializacja niezaufanego `pickle`, SSRF zwracający lokalny endpoint admin), atakujący wykonuje swój kod jako root *wewnątrz kontenera*. Co to ułatwia:

- **Modyfikację plików aplikacji w runtime** — wstrzyknięcie backdoora w kod, który restartuje się przy następnym scalaniu.
- **Zainstalowanie narzędzi pomocniczych** — `apt-get install nmap netcat` z pełnymi uprawnieniami.
- **Eksploatację podatności kernela / capability** — wszystkie CVE typu „local privesc" są dla atakującego dostępne, bo zaczyna jako root i ma w kontenerze pełen zestaw default capabilities.
- **Łatwiejszą ucieczkę z kontenera** — cap `SYS_ADMIN`, `DAC_OVERRIDE` (a w starszych konfiguracjach `--privileged`/montowane sock-i Dockera) prowadzą prosto do hosta.

Brak `USER` jest pojedynczą najbardziej kosztowną pomijaną „best practice" w obrazach pisanych ad hoc.

**Po naprawie:**

```dockerfile
# backend/Dockerfile (fragmenty)
FROM python:3.11-slim

RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

RUN python -c "import flask; import psycopg2; import gunicorn"

RUN chown -R appuser:appgroup /app

USER appuser
```

Kluczowe decyzje:

1. Użytkownik systemowy (`--system`) — bez katalogu domowego, bez hasła, bez powłoki interaktywnej, z uid w zakresie systemowym (<1000).
2. `chown -R appuser:appgroup /app` po `pip install`, by `appuser` mógł czytać `app.py` i pliki Pythona.
3. `USER appuser` *przed* `CMD`, co przełącza domyślnego usera procesów uruchamianych w kontenerze.
4. Gunicorn binduje port **5000** (≥ 1024) — nieuprzywilejowany, więc nie potrzebuje roota.

**Weryfikacja:**

```bash
$ docker compose exec backend whoami
appuser
```

Backend wewnątrz kontenera działa jako `appuser`. Atak RCE zaczyna w nieuprzywilejowanym procesie — pole manewru atakującego radykalnie maleje.

---

## 6. Weryfikacja działania (curl)

Po wszystkich czterech naprawach:

```bash
$ docker compose up --build -d
[+] Running 4/4
 ✔ Network app_422374_app_network  Created
 ✔ Volume "app_422374_postgres_data"  Created
 ✔ Container app_422374-db-1        Healthy
 ✔ Container app_422374-backend-1   Started
```

`docker compose ps`:

```text
NAME                   IMAGE                COMMAND                  STATUS
app_422374-db-1        postgres:15          "docker-entrypoint.s…"   Up (healthy)
app_422374-backend-1   app_422374-backend   "gunicorn --bind 0.0…"   Up
```

### 6.2 — `/health`

```bash
$ curl -s http://localhost:5000/health
{"status":"ok"}
```

### 6.3 — Backend nie jest rootem

```bash
$ docker compose exec backend whoami
appuser
```

### 6.4 — Brak sekretów w historii warstw

```bash
$ docker history app_422374-backend --no-trunc | grep -E "API_KEY|SECRET_KEY|my-secret-key|super-secret"
(brak wystapien sekretow w historii warstw)
```

### 6.5 — `/items` (pusta lista)

```bash
$ curl -s http://localhost:5000/items
[]
```

---

## 7. Weryfikacja persystencji danych

### 7.1 — POST /items

```bash
$ curl -s -X POST http://localhost:5000/items \
    -H "Content-Type: application/json" \
    -d '{"name": "element testowy"}'
{"created_at":"2026-05-07 18:06:09.621993","id":1,"name":"element testowy"}
```

### 7.2 — Restart bez `-v`

```bash
docker compose down
docker compose up -d
```

### 7.3 — GET /items po restarcie

```bash
$ curl -s http://localhost:5000/items
[{"created_at":"2026-05-07 18:06:09.621993","id":1,"name":"element testowy"}]
```

✅ Element przetrwał restart — wolumen `app_422374_postgres_data` poprawnie zachował dane bazy mimo zniszczenia i ponownego utworzenia kontenera.

---

## 8. Tematy dodatkowe

### 8.1 Docker Content Trust (DCT)

**Czym jest:** DCT to mechanizm cyfrowego podpisywania i weryfikacji obrazów Dockera, oparty o protokół **The Update Framework (TUF)** i implementację Notary. Idea: każdy `image:tag` w registry można podpisać kluczem prywatnym (wydawca), a klient (Docker daemon, BuildKit, CI) odmawia pobrania obrazu, który nie ma ważnego podpisu pod aktualnym `tag`.

**Jak włączyć:**

```bash
export DOCKER_CONTENT_TRUST=1
```

Po ustawieniu zmiennej:

- `docker pull image:tag` zatrzymuje się błędem, jeśli `tag` nie ma podpisu;
- `docker push image:tag` wymaga klucza podpisującego (`DOCKER_CONTENT_TRUST_REPOSITORY_PASSPHRASE`) i tworzy/aktualizuje wpis w Notary;
- `docker build` i `docker run` korzystają z tej samej weryfikacji przy pobieraniu obrazu bazowego.

**Co konkretnie zmienia w praktyce:**

1. **Atak na rejestr nie wystarczy.** Jeśli atakujący przejmie rejestr, ale nie ma klucza wydawcy, nie może podmienić podpisanego obrazu — klient odrzuci niepodpisany lub obcego-podpisu wariant.
2. **Pinowanie staje się kryptograficzne, nie tylko nominalne.** Zwykły `image:1.25-alpine` to ufanie, że nikt nie nadpisał tego konkretnego tagu w rejestrze. Z DCT dodatkowo weryfikujesz, że digest dopasowany do tego tagu został podpisany przez właściciela.
3. **Bramki w pipeline stają się bardziej deklaratywne.** Możesz wymóc politykę „builduj tylko z obrazów `org/*` z aktualnym podpisem", co odsiewa „stary obraz, którego klucz wygasł".

**Ograniczenia:** ekosystem nie wszędzie używa DCT — Docker Hub historycznie miał jego fragmentaryczne wsparcie, ekosystem Kubernetes preferuje **Sigstore/cosign** jako konkurencyjny stos; dla obrazów public-domain (`python`, `nginx`) podpisy oficjalne są dostępne, ale aktualnie standardem branżowym staje się cosign + OIDC keyless.

---

### 8.2 Multi-stage builds — zmniejszenie powierzchni ataku

**Czym jest:** w jednym `Dockerfile` deklarujemy *kilka* stage'y (`FROM ... AS builder`, `FROM ... AS runtime`) i kopiujemy do końcowego obrazu **tylko artefakty** wybrane explicite (`COPY --from=builder /artifact /target`). Wszystko, co nie zostało skopiowane — kompilatory, pakiety dev, źródła, narzędzia testowe — *nie trafia* do końcowego obrazu.

**Przykład dla naszego backendu:**

```dockerfile
# Stage 1: build (gcc do psycopg2-binary, jeśli kiedykolwiek by trzeba kompilować)
FROM python:3.11-slim AS builder
WORKDIR /build
RUN apt-get update && apt-get install -y --no-install-recommends gcc libpq-dev
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Stage 2: runtime (slim — bez gcc, bez nagłówków, bez apt cache)
FROM python:3.11-slim AS runtime
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser
WORKDIR /app
COPY --from=builder /root/.local /home/appuser/.local
ENV PATH=/home/appuser/.local/bin:$PATH
COPY app.py .
RUN chown -R appuser:appgroup /app /home/appuser/.local
USER appuser
EXPOSE 5000
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--preload", "app:app"]
```

**Co zyskujemy:**

- **Mniejszy obraz końcowy.** `gcc`, `libpq-dev`, `apt`, cache pip dev — nic z tego nie wjeżdża do runtime; obraz spada o ~150–300 MB w typowym przypadku Python+native deps.
- **Mniejsza powierzchnia CVE.** Każdy pakiet w obrazie to potencjalne CVE, które trzeba patchować; im mniej pakietów, tym mniej alertów ze skanera. Brak `gcc` w obrazie produkcyjnym oznacza, że atakujący po RCE nie skompiluje sobie własnych narzędzi w kontenerze.
- **Wyraźna granica trust.** „To, co potrzebne tylko do buildu" zostaje w stage `builder` i jest odrzucane na końcu — nie da się jej przypadkowo wyciec do produkcji.
- **Reproducibility.** `COPY --from=builder /artifact ...` to deklaratywny manifest *czego* runtime potrzebuje — łatwiej audytować niż „wszystko, co `apt` wlało w pierwszym `RUN`".

W tym laboratorium nie wprowadziłem multi-stage do `app_422374` — zostawiłem prostszy single-stage zgodnie z duchem README — ale w produkcyjnym workflow byłaby to naturalna następna iteracja po naprawieniu czterech błędów z laboratorium.

---

### 8.3 Docker Secrets w Docker Swarm — różnica względem `environment`

**Czym są Docker Secrets:** mechanizm **Docker Swarm** (i częściowo Kubernetes ma analog) do przechowywania i dostarczania sekretów do kontenerów. Sekret tworzy się raz na poziomie klastra:

```bash
echo -n 'devops123' | docker secret create db_password -
```

Sekret jest przechowywany **zaszyfrowany** w wewnętrznym storage klastra (Raft log) i dostarczany do kontenera **jako plik tmpfs** w `/run/secrets/<name>`:

```yaml
# docker-compose.yml dla Swarm
services:
  db:
    image: postgres:15
    secrets:
      - db_password
    environment:
      POSTGRES_PASSWORD_FILE: /run/secrets/db_password

secrets:
  db_password:
    external: true
```

Postgres umie czytać hasło z pliku przez konwencję `*_FILE` — i tak samo robi większość dobrze napisanych obrazów (Mongo, Redis z odpowiednim entrypoint-em, własne aplikacje, jeśli zaprojektujesz je tak).

**Czym różni się od `environment` (czyli sposobu, którego użyłem w tym labie):**

| Aspekt | `environment` z `.env` | Docker Secrets w Swarm |
|---|---|---|
| Lokalizacja sekretu w runtime | zmienna środowiskowa procesu | plik w tmpfs `/run/secrets/<name>` |
| Widoczność w `docker inspect` | tak — pełna lista `Env` | nie — `inspect` pokazuje tylko fakt zamontowania, nie wartość |
| Widoczność dla innych procesów w kontenerze | tak — `cat /proc/<pid>/environ` | nie — plik czytany tylko przez właściciela (chmod 400) |
| Widoczność w logach | wysokie ryzyko — `printenv`, `dump environ` na crash, biblioteki logujące „all env vars" | niskie — sekret nie przechodzi przez argv ani environ |
| Szyfrowanie at-rest | brak (plik `.env` jawnym tekstem na hoście) | tak — Raft store w Swarm szyfruje sekrety symetrycznie |
| Szyfrowanie in-transit | n/a | tak — TLS między managerami Swarm |
| Rotacja | wymaga restartu kontenera + edycji `.env` na każdym hoście | jeden `docker secret update`, kontenery dostają nowy plik bez odbudowy obrazu |
| Wymóg infrastruktury | brak — działa lokalnie | wymaga Swarm mode (lub Kubernetes z Secrets) |
| Granularność uprawnień | wszystko-albo-nic (cały kontener widzi `.env`) | per-secret — kontener dostaje tylko sekrety wymienione w `secrets:` |

**Praktycznie kiedy:**

- **Środowisko dev / lokalne projekty:** `environment` + `.env` (jak w tym labie) — wystarczające, proste, działa wszędzie.
- **Produkcja w Swarm:** **zawsze** Docker Secrets — eliminuje całą klasę wycieków przez `inspect`, `environ`, logi.
- **Produkcja w Kubernetes:** odpowiednik to **Kubernetes Secrets**, najlepiej z dodatkową warstwą (sealed-secrets, External Secrets Operator, Vault) — bo same K8s Secrets są tylko zakodowane base64, nie zaszyfrowane bez konfiguracji `EncryptionConfiguration` w API serverze.

W skrócie: zmienne środowiskowe to *funkcjonalny* kanał dla sekretów, ale *niebezpieczny* w produkcji, bo sekret „przecieka" przez wiele warstw obserwowalności (env, inspect, logi, dump). Docker Secrets / K8s Secrets / Vault to dedykowany kanał z mniejszą powierzchnią wycieku.

---

## 9. Napotkane problemy i wnioski

### Napotkane problemy

1. **Build padał na pierwszym `docker compose up --build` (przed jakąkolwiek naprawą).**
   Tag `python:latest` pociągał Pythona 3.14, gdzie `psycopg2-binary 2.9.9` nie ma prebuilt wheel-i i kompilacja źródeł padała na deprecated `_PyInterpreterState_Get()`. Identyczny problem dotknął `postgres:latest` — to dziś PG 18+ z innym layoutem `PGDATA`. Oba przypadki są dosłownymi manifestacjami BŁĘDU 1: tag `latest` zmienia się w czasie i psuje deterministyczne buildy.
2. **Zbieranie dowodu dla BŁĘDU 2 i BŁĘDU 4 wymagało jednoczesnego workaroundu BŁĘDU 1.**
   Żeby `docker history` w ogóle pokazał warstwy backendu, trzeba było obraz zbudować — a build padał z powodu `python:latest`. Tymczasowo zmieniłem `FROM python:latest` → `FROM python:3.11-slim` i `image: postgres:latest` → `image: postgres:15` *bez* dotykania pozostałych trzech błędów. Po zebraniu dowodów (`whoami=root`, `ENV API_KEY=…` w warstwach) zatrzymałem aplikację i wprowadziłem realne naprawy.
3. **Konflikt na porcie 80 z lokalnym Apache.** Frontend `nginx` próbował zbindować `0.0.0.0:80`, co kończyło się `address already in use`. Nie zatrzymywałem Apache (nie chciałem ruszać systemowych usług użytkownika); README weryfikuje aplikację curl-em na porcie 5000 (backend), więc niedziałający frontend nie blokuje walidacji laboratorium. Alternatywą byłoby zmapowanie frontu na np. `8080:80` lub `sudo systemctl stop apache2`.
4. **Pozostałości w wolumenie po pierwszym, zepsutym starcie.** Po pierwszej próbie `docker compose up` z `postgres:latest` (PG 18) wolumen został zainicjalizowany w niezgodnym layoutcie. Po pinowaniu na `postgres:15` Postgres nie chciał startować nad starym wolumenem. Naprawa: jednorazowe `docker compose down -v`.

### Wnioski

- **`latest` jest wrogiem.** Repeatable build wymaga pinowania *każdego* tagu. To nie jest tylko higiena ekosystemu — to konkretne, mierzalne źródło incydentów (build, który dziś działa, jutro nie).
- **`ENV` w `Dockerfile` to nie jest miejsce na sekret.** Wszystko, co `ENV` zapisze, idzie do warstwy obrazu i jest *publiczne* dla każdego, kto ma obraz. Sekrety dostarczamy w runtime przez `environment:` w Compose (z `.env` lokalnym + `.gitignore`) lub przez Docker Secrets / vault w produkcji.
- **`docker-compose.yml` to plik repo — traktuj go jak publiczny.** Wszystko, co tam wpiszesz, wejdzie do `git log` i pozostanie tam. Hasła, tokeny, klucze prywatne — przez `${VAR}` i out-of-band-dostarczany `.env`, nigdy bezpośrednio.
- **Brak `USER` to nie kosmetyka — to klasa CVE.** Od momentu, gdy dodajesz `USER nieuprzywilejowany` w Dockerfile, łańcuch eksploitacji „RCE → root w kontenerze → ucieczka do hosta" rozpoczyna się o krok dalej, w mniej swobodnym kontekście. Bezkosztowa zmiana, bezpośredni zysk obronny.
- **LLM jako pomocnik do security review działa dobrze przy klasycznych klasach problemów** (`latest`, `ENV` z sekretami, hardkodowane hasła w compose, brak `USER`). Każdą sugestię i tak weryfikujemy komendą — `docker history`, `docker compose exec whoami`, `git log -p`, `docker inspect` — bo model nie ma dostępu do *aktualnego* runtime'u i czasami sugeruje rzeczy, których w pliku już nie ma.
