# Sprawozdanie - Lab 4
**Autor:** 420132  
**Data:** 2026-04-10  
**Repozytorium:** `git@github.com:Tomzonkal/DevOps2026.git`

---

## Cel laboratorium

Celem laboratorium było zapoznanie się z podstawami Dockera i Docker Compose poprzez diagnozę i naprawę celowo zepsutej aplikacji wieloserwisowej składającej się z frontendu (nginx), backendu (Python/Flask) i bazy danych (PostgreSQL).

---

## Kroki wykonane przed diagnozą

### Aktualizacja repo i stworzenie brancha

```bash
git fetch --all
git checkout main
git pull
git switch -c lab_4/new_branch_420132
git push --set-upstream origin lab_4/new_branch_420132
```

### Skopiowanie folderu aplikacji i pliku .env

```bash
cp -r Lab_4/app_0000 Lab_4/app_420132
cp Lab_4/app_420132/.env.example Lab_4/app_420132/.env
```

### Pierwsze uruchomienie aplikacji (z błędami)

```bash
cd Lab_4/app_420132
docker compose up --build
```

Aplikacja nie uruchomiła się poprawnie. Backend nie mógł połączyć się z bazą danych.

**Zaobserwowane logi błędów (backend):**
```
[INFO] Connecting to database...
[INFO] Database not ready, retrying (1/10)...
[INFO] Database not ready, retrying (2/10)...
...
[INFO] Database not ready, retrying (10/10)...
Error: Could not connect to database after 10 attempts
backend-1 exited with code 1
```

![Błędy backendu](bledy_backend.png)

---

## Diagnoza i naprawa błędów

Po analizie logów oraz zawartości pliku `docker-compose.yml` zidentyfikowano 4 błędy.

### Błąd 1 - Zła nazwa hosta bazy danych w DATABASE_URL

**Fragment przed naprawą:**
```yaml
DATABASE_URL: postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@database:5432/${POSTGRES_DB}
```

**Diagnoza:**  
Backend próbował połączyć się z hostem o nazwie `database`, który nie istnieje w sieci Docker Compose. W pliku `docker-compose.yml` serwis bazy danych nosi nazwę `db`, a Docker rozwiązuje nazwy serwisów na adresy IP właśnie po tej nazwie.

**Fragment po naprawie:**
```yaml
DATABASE_URL: postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@db:5432/${POSTGRES_DB}
```

**Dlaczego naprawa działa:**  
Docker Compose tworzy wewnętrzną sieć DNS, w której każdy serwis jest dostępny pod swoją nazwą zdefiniowaną w pliku `docker-compose.yml`. Nazwa `db` odpowiada serwisowi bazy danych, więc backend może go znaleźć w sieci.

---

### Błąd 2 - Backend nie czeka na gotowość bazy danych

**Fragment przed naprawą:**
```yaml
backend:
  build: ./backend
  environment:
    ...
  ports:
    - "5000:5000"
  networks:
    - app_network
```

**Diagnoza:**  
Backend startował jednocześnie z bazą danych, nie czekając aż baza będzie gotowa na przyjęcie połączeń. Baza potrzebuje kilku sekund na inicjalizację, przez co backend zawsze trafiał na niedziałającą bazę.

**Fragment po naprawie:**
```yaml
backend:
  build: ./backend
  depends_on:
    db:
      condition: service_healthy
```

**Dlaczego naprawa działa:**  
Dyrektywa `depends_on` z `condition: service_healthy` powoduje, że Docker Compose czeka z uruchomieniem backendu aż healthcheck serwisu `db` zwróci status `healthy`. Healthcheck dla `db` był już poprawnie skonfigurowany (`pg_isready`), więc backend startuje dopiero gdy baza jest naprawdę gotowa.

---

### Błąd 3 - Backend nie należy do sieci db_network

**Fragment przed naprawą:**
```yaml
backend:
  networks:
    - app_network
```

**Diagnoza:**  
Backend znajdował się tylko w sieci `app_network`, natomiast baza danych (`db`) była w sieci `db_network`. Serwisy w różnych sieciach nie mogą się ze sobą komunikować w Docker Compose.

**Fragment po naprawie:**
```yaml
backend:
  networks:
    - app_network
    - db_network
```

**Dlaczego naprawa działa:**  
Dodanie backendu do sieci `db_network` umożliwia mu komunikację z serwisem `db`. Backend musi być w obu sieciach: `app_network` (żeby frontend mógł się z nim komunikować) i `db_network` (żeby mógł komunikować się z bazą danych).

---

### Błąd 4 - Zła ścieżka wolumenu dla PostgreSQL

**Fragment przed naprawą:**
```yaml
db:
  volumes:
    - postgres_data:/var/lib/postgresql
```

**Diagnoza:**  
PostgreSQL przechowuje dane w katalogu `/var/lib/postgresql/data`, a nie w `/var/lib/postgresql`. Montowanie wolumenu w złym miejscu powodowało, że baza próbowała inicjalizować się w katalogu, który już istniał (i nie był pusty), co kończyło się błędem.

**Zaobserwowany błąd:**
```
initdb: error: directory "/var/lib/postgresql/data" exists but is not empty
db-1 exited with code 1
```

**Fragment po naprawie:**
```yaml
db:
  volumes:
    - postgres_data:/var/lib/postgresql/data
```

**Dlaczego naprawa działa:**  
Wskazanie poprawnej ścieżki `/var/lib/postgresql/data` powoduje, że wolumen jest montowany dokładnie tam gdzie PostgreSQL przechowuje dane. Przy pierwszym uruchomieniu PostgreSQL inicjalizuje pusty katalog, a przy kolejnych uruchomieniach znajduje już istniejące dane i je wczytuje.

---

## Naprawiony plik docker-compose.yml

```yaml
services:
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: ${POSTGRES_DB}
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - db_network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB}"]
      interval: 5s
      timeout: 5s
      retries: 5
  backend:
    build: ./backend
    environment:
      DATABASE_URL: postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@db:5432/${POSTGRES_DB}
    ports:
      - "5000:5000"
    depends_on:
      db:
        condition: service_healthy
    networks:
      - app_network
      - db_network
  frontend:
    build: ./frontend
    ports:
      - "80:80"
    depends_on:
      - backend
    networks:
      - app_network
networks:
  app_network:
    driver: bridge
  db_network:
    driver: bridge
volumes:
  postgres_data:
```

---

## Weryfikacja działania

### Uruchomienie naprawionej aplikacji

```bash
docker compose up --build
```

![Aplikacja uruchomiona](docker_uruchomiony.png)

Wszystkie serwisy uruchomione poprawnie: `db` - Healthy, `backend` - Listening at 0.0.0.0:5000, `frontend` - nginx running.

### Sprawdzenie endpointu /health

```bash
curl http://localhost:5000/health
```

**Wynik:**
```
{"status":"ok"}
```

![curl /health](curl_health.png)

### Sprawdzenie frontendu

```bash
curl http://localhost:80
```

**Wynik:** Strona HTML aplikacji DevOps2026 Lab 4 (StatusCode 200 OK).

![curl frontend](curl_frontend.png)

### Sprawdzenie endpointu /items

```bash
curl http://localhost:5000/items
```

**Wynik:**
```
[]
```

![curl /items](curl_items.png)

---

## Weryfikacja persystencji danych

### Dodanie elementu

```bash
curl -Method POST http://localhost:5000/items -ContentType "application/json" -Body '{"name": "element testowy"}'
```

**Wynik:**
```json
{"created_at":"2026-04-10 08:26:08.474377","id":1,"name":"element testowy"}
```

![curl POST](curl_post.png)

### Weryfikacja że element jest na liście

```bash
curl http://localhost:5000/items
```

**Wynik:**
```json
[{"created_at":"2026-04-10 08:26:08.474377","id":1,"name":"element testowy"}]
```

![curl items po dodaniu](curl_items_po_dodaniu.png)

### Restart aplikacji i weryfikacja że dane przetrwały

```bash
docker compose down
docker compose up
curl http://localhost:5000/items
```

**Wynik po restarcie:**
```json
[{"created_at":"2026-04-10 08:26:08.474377","id":1,"name":"element testowy"}]
```

Dane przetrwały restart - wolumen działa poprawnie.

![curl items po restarcie](curl_items_po_restarcie.png)

### Usunięcie wolumenu i weryfikacja czystego stanu

```bash
docker compose down -v
docker compose up
curl http://localhost:5000/items
```

**Wynik po usunięciu wolumenu:**
```
[]
```

Baza danych jest pusta po usunięciu wolumenu - potwierdzenie poprawnego działania persystencji.

![curl items po down -v](curl_items_po_down_v.png)

---

## Tematy dodatkowe

### Docker network bridge vs host

**Bridge** (domyślny w Docker Compose) tworzy izolowaną wirtualną sieć wewnątrz hosta. Kontenery w tej samej sieci bridge mogą się ze sobą komunikować przez nazwy serwisów, ale są odizolowane od sieci hosta. Porty muszą być explicite mapowane (`ports: "5000:5000"`), żeby były dostępne z zewnątrz. Używa się go gdy chcemy izolacji między serwisami i kontroli nad tym co jest dostępne na zewnątrz - czyli w praktycznie każdej normalnej aplikacji wieloserwisowej.

**Host** usuwa izolację sieciową - kontener współdzieli stos sieciowy bezpośrednio z hostem. Kontener widzi wszystkie interfejsy hosta i nie potrzebuje mapowania portów. Używa się go gdy potrzebna jest maksymalna wydajność sieciowa (np. monitoring sieci, aplikacje wymagające bardzo niskich opóźnień) lub gdy kontener musi widzieć ruch sieciowy hosta. Wadą jest brak izolacji i ryzyko konfliktów portów. Tryb `host` nie działa na Docker Desktop (Windows/Mac) - tylko na natywnym Dockerze na Linuksie.

---

### Named volume vs bind mount

**Named volume** (`postgres_data:/var/lib/postgresql/data`) to wolumin zarządzany przez Dockera, przechowywany w wewnętrznym katalogu Dockera na hoście (`/var/lib/docker/volumes/`). Docker sam zarządza jego lokalizacją. Używa się go do persystencji danych aplikacji (bazy danych, pliki użytkowników) gdy nie potrzebujemy znać dokładnej lokalizacji na hoście. Jest przenośny, działa tak samo na wszystkich platformach.

**Bind mount** (`./data:/app/data`) montuje konkretny katalog lub plik z hosta do kontenera. Programista kontroluje dokładną lokalizację. Używa się go głównie podczas developmentu - np. montowanie kodu źródłowego do kontenera (`./src:/app/src`) żeby zmiany w kodzie były od razu widoczne bez przebudowywania obrazu. W produkcji preferuje się named volumes bo są bardziej przenośne i zarządzane przez Dockera.

---

### HEALTHCHECK i depends_on condition: service_healthy

`HEALTHCHECK` w Dockerfile definiuje komendę, którą Docker periodycznie uruchamia żeby sprawdzić czy kontener działa poprawnie. Przykład dla PostgreSQL:

```yaml
healthcheck:
  test: ["CMD-SHELL", "pg_isready -U postgres"]
  interval: 5s
  timeout: 5s
  retries: 5
```

Docker uruchamia tę komendę co `interval` sekund. Jeśli komenda zwróci kod 0 - kontener jest `healthy`. Jeśli nie - po `retries` nieudanych próbach kontener staje się `unhealthy`.

`depends_on` z `condition: service_healthy` w Docker Compose powoduje, że dany serwis (np. backend) nie zostanie uruchomiony dopóki serwis od którego zależy (np. db) nie osiągnie stanu `healthy`. Bez tego warunku `depends_on` sprawdza tylko czy kontener został uruchomiony, a nie czy aplikacja wewnątrz kontenera jest gotowa na połączenia. To jest właśnie ten błąd który naprawiliśmy - baza była uruchomiona, ale jeszcze nie gotowa gdy backend próbował się połączyć.