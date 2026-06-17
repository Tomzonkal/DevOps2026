# Sprawozdanie z laboratorium 5 (DevOps2026)

Repozytorium robocze: `Lab_5/app_419912`

## 1. Cel laboratorium

Celem zadania bylo wykrycie i naprawa 4 bledow bezpieczenstwa w konfiguracji kontenerow Docker oraz potwierdzenie, ze aplikacja nadal dziala poprawnie po hardeningu. W trakcie laboratorium samodzielnie przeprowadzilem analize, wdrozylem poprawki i zweryfikowalem ich dzialanie.

## 2. Przebieg prac

### 2.1 Aktualizacja repozytorium i przygotowanie brancha

Wykonalem nastepujace kroki:

```bash
git fetch --all
git checkout main
git pull
git switch -c lab_5/new_branch_419912
git push
```

### 2.2 Przygotowanie katalogu aplikacji

Wykonalem nastepujace kroki:

```bash
cp -r Lab_5/app_0000 Lab_5/app_419912
cp Lab_5/app_419912/.env.example Lab_5/app_419912/.env
```

Dalsza prace wykonywalem tylko w `app_419912`.

### 2.3 Uruchomienie i wstepna inspekcja

```bash
cd Lab_5/app_419912
docker compose up --build
curl http://localhost:5000/health
curl http://localhost:5000/items
```

Otrzymane odpowiedzi:

```text
/health -> 200 OK
{"status":"ok"}

/items -> 200 OK
[]
```

Dowody:
- [Uruchomione kontenery i logi docker compose](../screeny/Zrzut%20ekranu%202026-04-21%20120817.png)
- [Wstepna weryfikacja endpointow /health i /items](../screeny/Zrzut%20ekranu%202026-04-21%20120042.png)
- [Wynik komendy docker history](../screeny/Zrzut%20ekranu%202026-04-21%20115955.png)
- [Plik docker-compose.yml po zmianach sekcji environment](../screeny/Zrzut%20ekranu%202026-04-21%20120606.png)
- [Weryfikacja endpointow po uruchomieniu aplikacji](../screeny/Zrzut%20ekranu%202026-04-21%20120900.png)
- [Dodanie elementu przez POST i odczyt listy](../screeny/Zrzut%20ekranu%202026-04-21%20120512.png)
- [Lista /items z zapisanymi rekordami](../screeny/Zrzut%20ekranu%202026-04-21%20120129.png)

## 3. Security review (LLM/wlasna analiza)

Przeanalizowalem pliki:
- `backend/Dockerfile`
- `frontend/Dockerfile`
- `docker-compose.yml`

Wnioski z analizy:
1. Uzycie tagow `latest` dla obrazow bazowych (brak pinowania wersji).
2. Sekrety wpisane bezposrednio przez `ENV` w obrazie backendu.
3. Haslo do bazy oraz URL z haslem zapisane jawnie w `docker-compose.yml`.
4. Backend uruchamial sie jako `root` (brak `USER`).

## 4. Opis 4 bledow i napraw

### BLAD 1: Niespiete wersje obrazow bazowych (`latest`)

**Przed naprawa (fragmenty):**

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
image: postgres:latest
```

**Zagrozenie:**
- brak powtarzalnosci buildow,
- ryzyko niekontrolowanej zmiany obrazu po stronie rejestru,
- mozliwosc pojawienia sie regresji lub podatnosci po tej samej komendzie build.

**Po naprawie (fragmenty):**

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
image: postgres:15
```

**Weryfikacja:**

```bash
docker compose build --no-cache
```

oraz sprawdzenie Dockerfile/compose (brak `latest`).

---

### BLAD 2: Hardkodowane sekrety w Dockerfile (`ENV`)

**Przed naprawa (fragment):**

```dockerfile
ENV API_KEY=super-secret-api-key-abc123
ENV SECRET_KEY=my-secret-key-do-not-share-2026
```

**Zagrozenie:**
- wartosci sekretow trafiaja do warstw obrazu,
- mozna je odczytac przez `docker history`/`docker inspect`,
- wyciek sekretow przy udostepnieniu obrazu lub repo.

**Po naprawie (fragmenty):**

```dockerfile
# backend/Dockerfile
# linie ENV usuniete
```

```yaml
# docker-compose.yml
backend:
  environment:
    API_KEY: ${API_KEY}
    SECRET_KEY: ${SECRET_KEY}
```

**Weryfikacja `docker history`:**

Przed (stan podatny):
```bash
docker history lab5_app_419912_backend --no-trunc
```
Przed naprawa w warstwach obrazu widoczne byly wpisy z `ENV API_KEY=...` i `ENV SECRET_KEY=...`.

Po (stan po naprawie):
```bash
docker history app_419912-backend --no-trunc
```
Po przebudowaniu obrazu warstwy zawieraja m.in. `CMD`, `EXPOSE`, `RUN`, `COPY`, bez jawnosci wartosci `API_KEY` i `SECRET_KEY`.

Dowod (screen):
- [Wynik komendy docker history](../screeny/Zrzut%20ekranu%202026-04-21%20115955.png)

---

### BLAD 3: Hardkodowane haslo w `docker-compose.yml`

**Przed naprawa (fragmenty):**

```yaml
POSTGRES_PASSWORD: "password123"
DATABASE_URL: postgresql://devops:password123@db:5432/devops_db
```

**Zagrozenie:**
- haslo trafia do repozytorium i historii commitow,
- kazda osoba z dostepem do kodu zna haslo do bazy,
- utrudniona rotacja sekretow i ryzyko wykorzystania danych dostepowych w innych srodowiskach.

**Po naprawie (fragmenty):**

```yaml
POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
DATABASE_URL: postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@db:5432/${POSTGRES_DB}
```

oraz dodano ignorowanie pliku z sekretami:

```gitignore
.env
```

Dowod (screen):
- [Plik docker-compose.yml po zmianach sekcji environment](../screeny/Zrzut%20ekranu%202026-04-21%20120606.png)

**Weryfikacja:**
- brak jawnego hasla w `docker-compose.yml`,
- sekret znajduje sie w `.env`,
- `.env` nie powinien byc trackowany przez git (`git status`, `git check-ignore .env`).

---

### BLAD 4: Kontener backend uruchomiony jako root

**Przed naprawa:**
- brak dyrektywy `USER` w `backend/Dockerfile`.

**Zagrozenie:**
- przy podatnosci typu RCE atakujacy uzyskuje uprawnienia roota w kontenerze,
- wieksze ryzyko eskalacji uprawnien i skutkow ubocznych ataku.

**Po naprawie (fragment):**

```dockerfile
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser
USER appuser
```

**Weryfikacja `whoami`:**

Przed:
```bash
docker compose exec backend whoami
# root
```

Po:
```bash
docker compose exec backend whoami
# appuser
```

## 5. Weryfikacja po naprawie

### 5.1 Aplikacja dziala poprawnie

Komendy:

```bash
curl http://localhost:5000/health
curl http://localhost:5000/items
```

Otrzymane odpowiedzi:

```text
/health -> 200 OK
{"status":"ok"}

/items -> 200 OK
[]
```

Dowod (screen):
- [Weryfikacja endpointow po uruchomieniu aplikacji](../screeny/Zrzut%20ekranu%202026-04-21%20120900.png)

### 5.2 Dodanie elementu i persystencja danych

Komendy:

```bash
curl -X POST http://localhost:5000/items \
  -H "Content-Type: application/json" \
  -d '{"name": "test"}'

curl http://localhost:5000/items
```

Po wykonaniu testu lista zawiera dodane rekordy `test` z polami `id` i `created_at`, co potwierdza zapis do bazy.

Dowody (screeny):
- [Dodanie elementu przez POST i odczyt listy](../screeny/Zrzut%20ekranu%202026-04-21%20120512.png)
- [Lista /items z zapisanymi rekordami](../screeny/Zrzut%20ekranu%202026-04-21%20120129.png)

Test po restarcie wykonalem identycznie:

```bash
docker compose down
docker compose up -d
curl http://localhost:5000/items
```

Po restarcie rekord dodany przed restartem nadal znajdowal sie na liscie.

## 6. Podsumowanie

Zidentyfikowalem i naprawilem 4 krytyczne problemy konfiguracyjne:
1. Brak pinowania wersji obrazow.
2. Sekrety zapisane w warstwach obrazu.
3. Jawne hasla w pliku compose.
4. Uruchamianie backendu jako root.

Po zmianach aplikacja zachowala funkcjonalnosc (`/health`, `/items`), a konfiguracja zostala przeze mnie utwardzona zgodnie z wymaganiami laboratorium.

## 7. Commit i push

```bash
git add Lab_5/app_419912/
git commit -m "lab_5: naprawiono problemy bezpieczenstwa i dodano sprawozdanie"
git push
```
