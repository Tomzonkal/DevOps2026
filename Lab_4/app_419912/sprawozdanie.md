# DevOps2026 Lab 4 - Docker

## Cel laboratorium

Celem ćwiczenia było przeanalizowanie i naprawienie celowo zepsutej aplikacji wieloserwisowej uruchamianej przez Docker Compose. Aplikacja składa się z trzech usług:

- `db` - PostgreSQL
- `backend` - API we Flask uruchamiane na porcie `5000`
- `frontend` - serwer WWW z aplikacją webową na porcie `80`

W trakcie pracy zdiagnozowałem błędy na podstawie logów kontenerów oraz treści `docker-compose.yml`, a następnie zweryfikowałem poprawność działania aplikacji po naprawie.

## Materiały źródłowe

- Plik konfiguracyjny: [docker-compose.yml](docker-compose.yml)
- Backend: [backend/app.py](backend/app.py)
- Zrzuty ekranu z diagnostyki i weryfikacji: [screeny](screeny)

## Diagnoza błędów

Na podstawie screenów z uruchomienia aplikacji oraz analizy konfiguracji zidentyfikowałem 4 błędy w pliku `docker-compose.yml`.

### 1. Backend nie mógł połączyć się z bazą danych przez zły host

**Błąd przed naprawą**

```yaml
environment:
  DATABASE_URL: postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@database:5432/${POSTGRES_DB}
```

**Jak został zdiagnozowany**

Na screenie z logów backendu widać komunikat:

> `Error: Could not connect to database after 10 attempts`

oraz wielokrotne próby:

> `Database not ready, retrying (1/10)...`

To wskazywało, że backend nie potrafił nawiązać połączenia z PostgreSQL. Po porównaniu z nazwą usługi w Compose okazało się, że w konfiguracji użyto hosta `database`, mimo że usługa nazywa się `db`.

**Naprawa**

```yaml
environment:
  DATABASE_URL: postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@db/${POSTGRES_DB}
```

**Dlaczego naprawa działa**

Docker Compose rozwiązuje nazwy usług przez wewnętrzny DNS. Backend powinien łączyć się z bazą przez nazwę serwisu `db`, a nie przez nieistniejący host `database`. Po poprawce backend mógł znaleźć kontener PostgreSQL i utworzyć tabelę `items`.

### 2. Backend był podłączony tylko do jednej sieci

**Błąd przed naprawą**

```yaml
backend:
  networks:
    - app_network
```

**Jak został zdiagnozowany**

W pliku `docker-compose.yml` baza danych była przypisana do `db_network`, a backend tylko do `app_network`. Oznaczało to, że backend i baza nie znajdowały się w tej samej sieci, więc backend nie miał poprawnej trasy do kontenera PostgreSQL.

**Naprawa**

```yaml
backend:
  networks:
    - app_network
    - db_network
```

**Dlaczego naprawa działa**

Aby kontenery mogły się komunikować, muszą być w tej samej sieci Docker. Dodanie `db_network` do backendu umożliwiło mu komunikację z bazą danych przez nazwę `db`.

### 3. Frontend był podłączony do niewłaściwych sieci i zależności

**Błąd przed naprawą**

```yaml
frontend:
  depends_on:
    - db
  networks:
    - app_network
    - db_network
```

**Jak został zdiagnozowany**

Na screenie konfiguracji widać, że frontend był zależny bezpośrednio od bazy danych, mimo że w architekturze aplikacji frontend powinien komunikować się tylko z backendem. Dodatkowo przypisanie frontendu do `db_network` było zbędne i niezgodne z logiką aplikacji.

**Naprawa**

```yaml
frontend:
  depends_on:
    - backend
  networks:
    - app_network
```

**Dlaczego naprawa działa**

Frontend nie powinien łączyć się bezpośrednio z bazą danych. Jego rolą jest korzystanie z backendu, który wykonuje logikę biznesową i obsługuje komunikację z PostgreSQL. Po poprawce zależność i sieć zostały dopasowane do rzeczywistej architektury aplikacji.

### 4. Wolumen bazy danych był zamontowany w złym katalogu

**Błąd przed naprawą**

```yaml
volumes:
  - postgres_data:/var/lib/postgresql
```

**Jak został zdiagnozowany**

W `docker-compose.yml` PostgreSQL korzysta z obrazu `postgres:15`, który zapisuje dane domyślnie w katalogu `/var/lib/postgresql/data`. Montowanie wolumenu do nadrzędnego katalogu mogło powodować, że dane nie były zapisywane tam, gdzie oczekuje ich PostgreSQL, a persystencja po restarcie nie działała poprawnie.

**Naprawa**

```yaml
volumes:
  - postgres_data:/var/lib/postgresql/data
```

**Dlaczego naprawa działa**

Po poprawnym zamontowaniu wolumenu do katalogu danych PostgreSQL baza zapisuje pliki w trwałym wolumenie Dockera. Dzięki temu dane pozostają po restarcie kontenerów i znikają dopiero po użyciu `docker compose down -v`.

## Finalna konfiguracja

Po poprawkach fragmenty `docker-compose.yml` wyglądały następująco:

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
      DATABASE_URL: postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@db/${POSTGRES_DB}
    ports:
      - "5000:5000"
    networks:
      - app_network
      - db_network
    depends_on:
      db:
        condition: service_healthy

  frontend:
    build: ./frontend
    ports:
      - "80:80"
    depends_on:
      - backend
    networks:
      - app_network
```

## Weryfikacja działania po naprawie

### Uruchomienie aplikacji

Po wykonaniu poprawki uruchomiłem aplikację poleceniem:

```bash
docker compose up --build
```

Screen z poprawnym startem kontenerów pokazuje, że:

- baza danych osiągnęła stan `Healthy`
- backend wystartował poprawnie
- frontend uruchomił nginx bez błędów krytycznych

Zrzut ekranu: [uruchomienie kontenerów](screeny/Zrzut%20ekranu%202026-04-21%20111904.png)

### Sprawdzenie endpointu health

Polecenie:

```bash
curl http://localhost:5000/health
```

Wynik:

```json
{"status":"ok"}
```

Zrzut ekranu: [health](screeny/Zrzut%20ekranu%202026-04-21%20112008.png)

### Sprawdzenie endpointu items

Polecenie:

```bash
curl http://localhost:5000/items
```

Wynik początkowy:

```json
[]
```

Zrzut ekranu: [items - stan początkowy](screeny/Zrzut%20ekranu%202026-04-21%20112021.png)

### Sprawdzenie działania frontendu

Polecenie:

```bash
curl http://localhost:80
```

Frontend był dostępny pod adresem `http://localhost:80` i zwracał stronę HTML aplikacji zgodnie z wymaganiami zadania.

## Weryfikacja persystencji danych

### Dodanie elementu przez API

Polecenie:

```bash
curl -X POST http://localhost:5000/items \
  -H "Content-Type: application/json" \
  -d '{"name":"test"}'
```

Wynik:

```text
created_at              id name
2026-04-21 09:21:09.473756  1 test
```

Następnie dodałem drugi rekord:

```bash
curl -X POST http://localhost:5000/items \
  -H "Content-Type: application/json" \
  -d '{"name":"Kacper"}'
```

Wynik:

```text
created_at              id name
2026-04-21 09:22:16.371790  2 Kacper
```

Zrzut ekranu: [dodawanie rekordów](screeny/Zrzut%20ekranu%202026-04-21%20112116.png)

### Odczyt danych po dodaniu

Polecenie:

```bash
curl http://localhost:5000/items
```

Wynik:

```json
[{"created_at":"2026-04-21 09:21:09.473756","id":1,"name":"test"},{"created_at":"2026-04-21 09:22:16.371790","id":2,"name":"Kacper"}]
```

Zrzut ekranu: [lista elementów](screeny/Zrzut%20ekranu%202026-04-21%20112229.png)

### Restart aplikacji i sprawdzenie trwałości danych

Po wykonaniu:

```bash
docker compose down
docker compose up
```

lista `items` nadal zawierała wcześniej dodane rekordy, co potwierdziło poprawne działanie wolumenu. Dowód znajduje się na screenie z uruchomieniem kontenerów i późniejszym odczytem listy:

- [uruchomienie kontenerów](screeny/Zrzut%20ekranu%202026-04-21%20111904.png)
- [lista po restarcie](screeny/Zrzut%20ekranu%202026-04-21%20112229.png)

### Usunięcie wolumenu i stan czysty

Po wykonaniu:

```bash
docker compose down -v
docker compose up
```

endpoint:

```bash
curl http://localhost:5000/items
```

zwracał pustą listę:

```json
[]
```

To potwierdza, że po usunięciu wolumenu baza startuje od czystego stanu.

## Podsumowanie

W ramach zadania zdiagnozowałem i naprawiłem 4 błędy konfiguracyjne w `docker-compose.yml`:

1. niepoprawny host bazy danych w `DATABASE_URL`
2. brak backendu w sieci `db_network`
3. błędna zależność frontendu od bazy danych i niepotrzebne podłączenie do `db_network`
4. zły punkt montowania wolumenu PostgreSQL

Po poprawkach aplikacja działa poprawnie, backend odpowiada na `/health`, frontend jest dostępny na porcie `80`, endpoint `/items` działa, a dane są zachowywane po restarcie kontenerów dzięki wolumenowi Docker.