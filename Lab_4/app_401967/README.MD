# Sprawozdanie – Lab 4

> **Autor:** 401967  
> **Data:** 2026-05-04  
> **Repozytorium:** git@github.com:Tomzonkal/DevOps2026.git

---

## Weryfikacja działania

Poniżej screenshoty potwierdzające że zadanie zostało wykonane poprawnie.

### Screenshot 1 – Błędy w logach po pierwszym uruchomieniu

![Logi terminala z komunikatami błędów po uruchomieniu docker compose up --build](screenshots/screen_1.png)

Widoczne komunikaty błędów backendu przy próbie połączenia z bazą danych — posłużyły do diagnozy problemów w `docker-compose.yml`.

### Screenshot 2 – Działająca aplikacja po naprawach

![Terminal z wynikami komend curl potwierdzającymi działanie endpointów /health, / i /items](screenshots/screen_2.png)
![](screenshots/screen_3.png)
![](screenshots/screen_4.png)

Wszystkie trzy endpointy odpowiadają poprawnie po wprowadzeniu poprawek.

### Screenshot 3 – Persystencja danych

![Terminal pokazujący dane po restarcie kontenerów i pusty stan po docker compose down -v](screenshots/screen_5.png)
![](screenshots/screen_6.png)

Dane przetrwały restart (`docker compose down` + `docker compose up`), a po usunięciu wolumenu (`docker compose down -v`) baza wróciła do pustego stanu.

---

## Opis kroków i naprawionych błędów

Poniżej opisałam każdy krok wykonany podczas laboratorium — od pobrania kodu, przez diagnozę błędów, po weryfikację działania.

---

### Krok 1 – Aktualizacja repozytorium i stworzenie gałęzi

```bash
git fetch --all
git checkout main
git pull
git switch -c lab_4/new_branch_401967
git push
```

`git fetch --all` pobiera metadane wszystkich zdalnych gałęzi bez scalania zmian. Po przełączeniu się na `main` i pobraniu najnowszego kodu (`git pull`) tworzymy nową gałąź roboczą i od razu wysyłamy ją na GitHuba.

---

### Krok 2 – Przygotowanie środowiska pracy

```bash
xcopy Lab_4\app_0000 Lab_4\app_123456 /E /I
copy Lab_4\app_123456\.env.example Lab_4\app_123456\.env
cd Lab_4/app_401967
```

Kopiujemy folder szablonu `app_0000` do `app_401967`. Plik `.env` jest tworzony na podstawie `.env.example` — zawiera zmienne środowiskowe (hasła, nazwy baz danych) które Docker Compose wstrzykuje do kontenerów w czasie uruchomienia. Oryginału `app_0000` nie modyfikujemy.

---

### Krok 3 – Pierwsze uruchomienie i obserwacja błędów
 
```bash
docker compose up --build
```
 
Aplikacja nie startuje poprawnie. Backend wielokrotnie próbował połączyć się z bazą danych i zakończył działanie po wyczerpaniu limitu prób:
 
```
backend-1   | [INFO]  Connecting to database...
backend-1   | [INFO]  Database pool initialized
backend-1   | [INFO]  Database not ready, retrying (1/10)...
backend-1   | [INFO]  Database not ready, retrying (2/10)...
backend-1   | [INFO]  Database not ready, retrying (3/10)...
backend-1   | [INFO]  Database not ready, retrying (4/10)...
backend-1   | [INFO]  Database not ready, retrying (5/10)...
backend-1   | [INFO]  Database not ready, retrying (6/10)...
backend-1 exited with code 1
backend-1   | [INFO]  Database not ready, retrying (7/10)...
backend-1   | [INFO]  Database not ready, retrying (8/10)...
backend-1   | [INFO]  Database not ready, retrying (9/10)...
backend-1   | [INFO]  Database not ready, retrying (10/10)...
backend-1   | Error: Could not connect to database after 10 attempts
```
 
Weryfikacja stanu kontenerów:
 
```bash
docker compose ps
```
 
```
NAME                      IMAGE                STATUS
app_401967-db-1           postgres:15          Up 3 hours (healthy)
app_401967-frontend-1     app_401967-frontend  Up 3 hours
```

![](screenshots/screen_7.png)

Backend nie pojawia się na liście — zakończył działanie z błędem. Zawartość pliku `docker-compose.yml` oraz powyższe logi posłużyły do diagnozy problemów.
 
---
 
### Krok 4 – Diagnoza i naprawa błędów
 
Na podstawie analizy logów i pliku `docker-compose.yml` zidentyfikowano cztery błędy.
 
---
 
#### Błąd 1 – Nieprawidłowa nazwa hosta bazy danych w DATABASE_URL
 
**Log wskazujący problem:**
```
backend-1   | [INFO]  Database not ready, retrying (1/10)...
...
backend-1   | Error: Could not connect to database after 10 attempts
```
 
**Przed naprawą (`docker-compose.yml`):**
```yaml
backend:
  environment:
    DATABASE_URL: postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@database:5432/${POSTGRES_DB}
```
 
**Po naprawie:**
```yaml
backend:
  environment:
    DATABASE_URL: postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@db:5432/${POSTGRES_DB}
```
 
**Wyjaśnienie:** W Docker Compose serwisy komunikują się ze sobą przez nazwy zdefiniowane jako klucze w sekcji `services`. Serwis bazy danych nosi nazwę `db`, a nie `database`. Wpisanie `@database:5432` w connection stringu powodowało że Docker nie mógł rozwiązać tej nazwy na adres IP żadnego kontenera — backend próbował 10 razy połączyć się z nieistniejącym hostem i kończył działanie błędem.
 
---
 
#### Błąd 2 – Nieprawidłowa ścieżka wolumenu PostgreSQL
 
**Diagnoza:** Analiza `docker-compose.yml` — PostgreSQL przechowuje dane w `/var/lib/postgresql/data`, a wolumen był montowany poziom wyżej.
 
**Przed naprawą:**
```yaml
db:
  volumes:
    - postgres_data:/var/lib/postgresql
```
 
**Po naprawie:**
```yaml
db:
  volumes:
    - postgres_data:/var/lib/postgresql/data
```
 
**Wyjaśnienie:** PostgreSQL tworzy strukturę danych dokładnie w katalogu `/var/lib/postgresql/data`. Montowanie wolumenu na `/var/lib/postgresql` powodowało że kontener widział pusty katalog nadrzędny zamiast właściwego katalogu z danymi — baza danych nie mogła poprawnie zapisywać ani odczytywać danych po restarcie kontenera. Po usunięciu wolumenu i ponownym uruchomieniu z poprawną ścieżką PostgreSQL inicjalizował się poprawnie.
 
---
 
#### Błąd 3 – Backend i baza danych w różnych sieciach
 
**Diagnoza:** Analiza `docker-compose.yml` — backend jest przypisany do `app_network`, baza danych wyłącznie do `db_network`. Serwisy w różnych sieciach nie mogą się ze sobą komunikować.
 
**Przed naprawą:**
```yaml
db:
  networks:
    - db_network
 
backend:
  networks:
    - app_network
```
 
**Po naprawie:**
```yaml
db:
  networks:
    - db_network
 
backend:
  networks:
    - app_network
    - db_network
```
 
**Wyjaśnienie:** Docker izoluje ruch sieciowy między sieciami — kontener widzi tylko inne kontenery w tej samej sieci. Backend musi być w `db_network` żeby dotrzeć do bazy danych, ale jednocześnie musi pozostać w `app_network` żeby był dostępny dla frontendu. Przypisanie serwisu do obu sieci rozwiązuje oba wymagania. Serwis `db` pozostaje wyłącznie w `db_network`, co poprawia bezpieczeństwo — frontend nie ma do niego bezpośredniego dostępu.
 
---
 
#### Błąd 4 – Brak zależności backendu od gotowości bazy danych
 
**Diagnoza:** Backend startował równocześnie z bazą danych i próbował się połączyć zanim PostgreSQL zdążył się zainicjalizować. Baza danych ma skonfigurowany `healthcheck`, ale backend nie czekał na jego pozytywny wynik.
 
**Przed naprawą:**
```yaml
backend:
  build: ./backend
  # brak depends_on
```
 
**Po naprawie:**
```yaml
backend:
  build: ./backend
  depends_on:
    db:
      condition: service_healthy
```
 
**Wyjaśnienie techniczne:** `depends_on` z `condition: service_healthy` powoduje że Docker Compose wstrzymuje start backendu do momentu aż healthcheck serwisu `db` zwróci status `healthy`. Healthcheck bazy danych potwierdza że PostgreSQL jest gotowy na przyjmowanie połączeń. Bez tej zależności backend startował zbyt wcześnie i wyczerpywał limit prób połączenia zanim baza była gotowa — nawet po naprawieniu pozostałych błędów sieciowych i adresowania.
 
---
 
### Krok 5 – Weryfikacja działania po naprawach
 
```bash
docker compose up --build
```
 
#### Endpoint `/health`
 
```bash
curl http://localhost:5000/health
```
 
Wynik:
```json
{"status": "ok"}
```
 
#### Frontend
 
```bash
curl http://localhost:80
```
 
Wynik: strona HTML aplikacji.
 
#### Endpoint `/items`
 
```bash
curl http://localhost:5000/items
```
 
Wynik:
```json
[]
```
 
Wszystkie trzy endpointy odpowiadają poprawnie.
 
---
 
### Krok 6 – Weryfikacja persystencji danych
 
#### Dodanie elementu
 
```bash
curl -X POST http://localhost:5000/items -H "Content-Type: application/json" -d "{\"name\": \"element testowy\"}"
```
 
Wynik:
```json
{"id": 1, "name": "element testowy"}
```
 
#### Potwierdzenie że element jest na liście
 
```bash
curl http://localhost:5000/items
```
 
Wynik:
```json
[{"id": 1, "name": "element testowy"}]
```
 
#### Restart kontenerów
 
```bash
docker compose down
docker compose up
curl http://localhost:5000/items
```
 
Wynik:
```json
[{"id": 1, "name": "element testowy"}]
```
 
Dane przetrwały restart — wolumen działa poprawnie.
 
#### Usunięcie wolumenu i weryfikacja czystego stanu
 
```bash
docker compose down -v
docker compose up
curl http://localhost:5000/items
```
 
Wynik:
```json
[]
```
 
Po usunięciu wolumenu baza danych jest pusta — zachowanie zgodne z oczekiwaniami.
 
---
 
### Krok 7 – Commit i push
 
```bash
git add Lab_4/app_401967/
git commit -m "lab_4: naprawiono docker-compose"
git push
```
 
Następnie na GitHubie utworzono pull request z gałęzi `lab_4/new_branch_401967` do gałęzi `TEST`.
 
---
 
## Podsumowanie
 
W tym laboratorium zdiagnozowałam i naprawiłam cztery błędy w pliku `docker-compose.yml` aplikacji wieloserwisowej (frontend + backend + baza danych PostgreSQL):
 
1. **Błędna nazwa hosta bazy danych** – `DATABASE_URL` zawierało `@database:5432`, a serwis nosi nazwę `db`; Docker nie mógł rozwiązać tej nazwy na żaden adres IP w sieci.
2. **Nieprawidłowa ścieżka wolumenu** – wolumen był montowany na `/var/lib/postgresql` zamiast na `/var/lib/postgresql/data`, gdzie PostgreSQL faktycznie przechowuje dane.
3. **Izolacja sieci** – backend i baza danych były w różnych sieciach (`app_network` vs `db_network`) i nie mogły się ze sobą komunikować; dodanie backendu do `db_network` rozwiązało problem.
4. **Brak `depends_on` z warunkiem `service_healthy`** – backend startował za wcześnie i wyczerpywał limit prób połączenia zanim PostgreSQL zdążył się zainicjalizować.
Laboratorium pokazało jak kluczowe jest rozumienie modelu sieciowego Dockera oraz mechanizmów zależności między serwisami — konteneryzowane aplikacje wymagają świadomego zarządzania siecią, wolumenami i kolejnością uruchamiania komponentów.