# Sprawozdanie z Laboratorium DevOps nr 4
 
**Autor:** Jakub Kukiełka (Kokoszka2004)  
**Data:** 13 kwietnia 2026 r.
 
---
 
## 1. Cel i zakres laboratorium
 
Czwarte zajęcia z przedmiotu DevOps poświęcone były zapoznaniu się z podstawami Dockera i Docker Compose poprzez diagnozę i naprawę celowo zepsutej aplikacji wieloserwisowej. Zakres prac obejmował:
 
* Aktualizację lokalnego środowiska i przełączenie na branch main.
* Tworzenie nowego brancha i skopiowanie folderu aplikacji.
* Uruchomienie aplikacji i obserwację błędów w logach kontenerów.
* Diagnozę czterech celowych błędów w pliku `docker-compose.yml`.
* Naprawę błędów i weryfikację poprawnego działania wszystkich serwisów.
* Weryfikację persystencji danych przy użyciu wolumenów Docker.
 
---
 
## 2. Przygotowanie środowiska i aktualizacja repo
 
Pracę rozpocząłem od aktualizacji lokalnego repozytorium:
 
* **Aktualizacja metadanych projektu:** `git fetch --all`
* **Przełączenie na gałąź główną:** `git checkout main`
* **Pobranie aktualnych zmian w kodzie:** `git pull`
 
Następnie stworzyłem nowy branch roboczy i wypchnąłem go do zdalnego repozytorium:
 
* **Tworzenie gałęzi:** `git switch -c lab_4/new_branch_422385`
* **Wypchnięcie brancha:** `git push -u origin lab_4/new_branch_422385`
 
---
 
## 3. Przygotowanie folderu aplikacji
 
Skopiowałem folder `app_0000` do nowego folderu `app_422385` oraz stworzyłem plik `.env` na podstawie `.env.example`:
 
```bash
cp -r Lab_4/app_0000 Lab_4/app_422385
cp Lab_4/app_422385/.env.example Lab_4/app_422385/.env
cd Lab_4/app_422385
```
 
Struktura folderu po skopiowaniu:
 
```
app_422385/
├── .env
├── .env.example
├── docker-compose.yml
├── backend/
└── frontend/
```
 
---
 
## 4. Uruchomienie aplikacji i obserwacja błędów
 
Uruchomiłem aplikację komendą:
 
```bash
docker compose up --build
```
 
Po uruchomieniu sprawdziłem stan serwisów w osobnym terminalu:
 
```bash
docker compose ps
```
 
Wynik pokazał że kontener `backend` nie pojawił się na liście — tylko `db` i `frontend` działały poprawnie:
 
```
NAME                    IMAGE                 COMMAND     SERVICE    STATUS
app_422385-db-1         postgres:15           ...         db         Up (healthy)
app_422385-frontend-1   app_422385-frontend   ...         frontend   Up
```
 
Sprawdziłem logi backendu:
 
```bash
docker compose logs backend
```
 
Logi wskazały na problem z połączeniem z bazą danych:
 
```
backend-1  | [INFO]  Connecting to database...
backend-1  | [INFO]  Database not ready, retrying (1/10)...
backend-1  | [INFO]  Database not ready, retrying (2/10)...
...
backend-1  | [INFO]  Database not ready, retrying (10/10)...
backend-1  | Error: Could not connect to database after 10 attempts
```
 
---
 
## 5. Diagnoza i naprawa błędów
 
Po przeanalizowaniu pliku `docker-compose.yml` oraz logów zidentyfikowałem cztery błędy.
 
### Błąd 1 - Zła nazwa hosta bazy danych w DATABASE_URL
 
**Przed naprawą:**
```yaml
backend:
  environment:
    DATABASE_URL: postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@database:5432/${POSTGRES_DB}
```
 
**Jak zdiagnozowano:**  
Backend logował `Could not connect to database after 10 attempts`. Analiza pliku `docker-compose.yml` wykazała że serwis bazy danych nazywa się `db`, natomiast w zmiennej `DATABASE_URL` podano hosta `database`, 
który nie istnieje w konfiguracji.
 
**Po naprawie:**
```yaml
backend:
  environment:
    DATABASE_URL: postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@db:5432/${POSTGRES_DB}
```
 
**Wyjaśnienie techniczne:**  
W Docker Compose serwisy komunikują się przez nazwy zdefiniowane w pliku `docker-compose.yml`. Docker wewnętrznie rozwiązuje te nazwy na adresy IP kontenerów (DNS wewnętrzny). Nazwa `database` nie istniała 
w konfiguracji - poprawna nazwa hosta to `db`, zgodna z nazwą serwisu.
 
---
 
### Błąd 2 - Backend przypisany tylko do sieci app_network
 
**Przed naprawą:**
```yaml
backend:
  networks:
    - app_network
```
 
**Jak zdiagnozowano:**  
Baza danych `db` była przypisana wyłącznie do sieci `db_network`, a backend wyłącznie do `app_network`. Kontenery w różnych sieciach nie mogą się ze sobą komunikować, co powodowało błąd połączenia.
 
**Po naprawie:**
```yaml
backend:
  networks:
    - app_network
    - db_network
```
 
**Wyjaśnienie techniczne:**  
Docker izoluje ruch sieciowy między sieciami. Aby backend mógł połączyć się z bazą danych, musi być przypisany do tej samej sieci co `db`, czyli `db_network`. Jednocześnie backend musi 
pozostać w `app_network`, żeby frontend mógł się z nim komunikować.
 
---
 
### Błąd 3 - Brak depends_on w backendzie
 
**Przed naprawą:**
```yaml
backend:
  build: ./backend
  environment:
    DATABASE_URL: ...
  ports:
    - "5000:5000"
  networks:
    - app_network
```
 
**Jak zdiagnozowano:**  
Backend startował zanim baza danych zdążyła być gotowa i natychmiast próbował się połączyć, co kończyło się błędem. Brakował mechanizm oczekiwania na gotowość bazy.
 
**Po naprawie:**
```yaml
backend:
  depends_on:
    db:
      condition: service_healthy
```
 
**Wyjaśnienie techniczne:**  
`depends_on` z `condition: service_healthy` powoduje że Docker Compose czeka aż healthcheck bazy danych zwróci sukces, zanim uruchomi backend. Healthcheck był już zdefiniowany w serwisie `db` - sprawdza 
gotowość PostgreSQL przez komendę `pg_isready`.
 
---
 
### Błąd 4 - Zła ścieżka wolumenu bazy danych
 
**Przed naprawą:**
```yaml
db:
  volumes:
    - postgres_data:/var/lib/postgresql
```
 
**Jak zdiagnozowano:**  
PostgreSQL przechowuje pliki bazy danych w katalogu `/var/lib/postgresql/data`, a nie w `/var/lib/postgresql`. Zamontowanie wolumenu pod złą ścieżką powodowało że dane nie były poprawnie persystowane.
 
**Po naprawie:**
```yaml
db:
  volumes:
    - postgres_data:/var/lib/postgresql/data
```
 
**Wyjaśnienie techniczne:**  
Wolumen musi być zamontowany dokładnie w tym katalogu, gdzie PostgreSQL zapisuje swoje pliki. Zła ścieżka powodowała że dane były zapisywane poza wolumenem i nie przetrwały restartu kontenera.
 
---
 
## 6. Weryfikacja podstawowego działania
 
Po naprawieniu wszystkich błędów ponownie uruchomiłem aplikację:
 
```bash
docker compose down -v
docker compose up --build
```
 
Weryfikacja endpointów:
 
```bash
$ curl http://localhost:5000/health
{"status":"ok"}
 
$ curl http://localhost:80
<!DOCTYPE html>
<html lang="pl">
...
</html>
 
$ curl http://localhost:5000/items
[]
```
 
Wszystkie trzy endpointy odpowiadały poprawnie.
 
---
 
## 7. Weryfikacja danych
 
**Dodanie elementu:**
 
```bash
$ curl -X POST http://localhost:5000/items \
  -H "Content-Type: application/json" \
  -d '{"name": "element testowy"}'
 
{"created_at":"2026-04-13 18:25:43.184673","id":1,"name":"element testowy"}
```
 
**Weryfikacja pojawienia się elementu na liście:**
 
```bash
$ curl http://localhost:5000/items
[{"created_at":"2026-04-13 18:25:43.184673","id":1,"name":"element testowy"}]
```
 
**Restart aplikacji i sprawdzenie persystencji:**
 
```bash
docker compose down
docker compose up
```
 
```bash
$ curl http://localhost:5000/items
[{"created_at":"2026-04-13 18:25:43.184673","id":1,"name":"element testowy"}]
```
 
Dane przetrwały restart - wolumen działa poprawnie.
 
**Usunięcie wolumenu i weryfikacja czystego stanu:**
 
```bash
docker compose down -v
docker compose up
```
 
```bash
$ curl http://localhost:5000/items
[]
```
 
Po usunięciu wolumenu baza danych jest pusta - potwierdzenie poprawnego działania persystencji.
 
---
 
## 8. Wnioski
 
Laboratorium nr 4 pozwoliło mi na praktyczne zapoznanie się z kluczowymi elementami pracy z Dockerem i Docker Compose:
 
* **Sieci Docker:** Zrozumiałem że kontenery komunikują się przez nazwy serwisów zdefiniowane w `docker-compose.yml`, a nie przez adresy IP. Serwisy muszą być w tej samej sieci, żeby mogły się ze sobą komunikować.
* **Zależności między serwisami:** Dyrektywa `depends_on` z `condition: service_healthy` pozwala na kontrolowanie kolejności startowania serwisów i zapewnia że backend nie wystartuje zanim baza danych będzie gotowa.
* **Wolumeny:** Poprawna ścieżka montowania wolumenu jest kluczowa dla persystencji danych. Błędna ścieżka powoduje że dane są zapisywane poza wolumenem i nie przetrwają restartu.
* **Diagnoza błędów:** Logi kontenerów (`docker compose logs`) oraz status serwisów (`docker compose ps`) są podstawowymi narzędziami do diagnozowania problemów w środowisku Docker Compose.