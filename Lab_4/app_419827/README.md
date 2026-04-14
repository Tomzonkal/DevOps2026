# Sprawozdanie - Lab 4
**Autor:** 419827  
**Data:** 2026-04-07  
**Repozytorium:** `git@github.com:Tomzonkal/DevOps2026.git`

---

## Cel laboratorium

Celem laboratorium było zapoznanie się z podstawami `Docker` i `Docker Compose` poprzez diagnozę oraz naprawę błędów w aplikacji wieloserwisowej. W trakcie zadania przeanalizowano logi, zidentyfikowano problemy konfiguracyjne oraz zweryfikowano poprawność działania aplikacji i komunikacji między serwisami.

Umiejętności, które powinny zostać nabyte po realizacji laboratorium:

- analiza logów i diagnozowanie błędów,
- konfiguracja aplikacji w `Docker Compose`,
- zarządzanie sieciami i wolumenami,
- testowanie działania aplikacji przy użyciu `curl`.

## Przebieg ćwiczenia
### Krok 1 - aktualizacja repozytorium 
Pierwszym krokiem było zaktualizowanie lokalnego repozytorium do najnowszej wersji. W tym celu pobrano wszystkie zmiany z repozytorium zdalnego oraz przełączono się na główną gałąź projektu:

```bash
git fetch --all
git checkout main
git pull
```
### Krok 2 - stworzenie nowego brancha 
Kolejno, stworzono nowego brancha przeznaczonego do rozwiązania laboratorium:

```bash
git switch -c lab_4/new_branch_419827
git push
```
![Utworzenie nowego brancha](screenshots/s1.png)

### Krok 3 - przygotowanie środowiska pracy 
W następnym kroku przygotowano środowisko pracy poprzez skopiowanie przykładowej aplikacji oraz utworzenie pliku konfiguracyjnego `.env`.

Najpierw skopiowano folder aplikacji:

```bash
cp -r Lab_4/app_0000 Lab_4/app_419827
```
Następnie utworzono plik `.env` na podstawie pliku przykładowego:
```bash
cp Lab_4/app_419827/.env.example Lab_4/app_419827/.env
```
![Przygotowanie środowiska](screenshots/s2.png)

Na końcu, sprawdzono dostępną wersję `Dockera`: 

![Wersja dockera](screenshots/s3.png)

### Krok 4 - uruchomienie aplikacji i obserwacja błędów 

W kolejnym kroku uruchomiono aplikację za pomocą `Docker Compose` w celu analizy jej działania oraz identyfikacji błędów oraz dodatkowo zmieniono mapowanie portu backendu z 5000 na 5001 ze względu na konflikt portu w lokalnym środowisku (zmiana ta nie była związana z błędami w zadaniu).

```bash
docker compose up --build
```

![Błedy po uruchomieniu aplikacji](screenshots/s4.png)

Po uruchomieniu aplikacji zaobserwowano, że backend nie był w stanie połączyć się z bazą danych. W celu sprawdzenia stanu kontenerów użyto polecenia:

```bash
docker compose ps
```
![Stan kontenerów](screenshots/s5.png)

Na podstawie logów można było stwierdzić, że baza danych działa poprawnie, jednak backend nie może nawiązać z nią połączenia, co wskazuje na błędy konfiguracyjne w pliku `docker-compose.yml`.

### Krok 5 - diagnoza i naprawa błędów

**Błąd 1 – niepoprawny adres hosta bazy danych w DATABASE_URL**

**Przed naprawą:**
```bash
DATABASE_URL: postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@database:5432/${POSTGRES_DB}
```
**Diagnoza:**

Na podstawie logów backendu zauważono, że aplikacja wielokrotnie próbowała połączyć się z bazą danych, jednak kończyła działanie błędem:
```bash
Error: Could not connect to database after 10 attempts
```
Analiza pliku `docker-compose.yml` wykazała, że backend odwołuje się do hosta `database`, podczas gdy nazwa usługi bazy danych to `db`.

**Po naprawie**:
```bash
DATABASE_URL: postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@db:5432/${POSTGRES_DB}
```

**Dlaczego działa**:
W `Docker Compose` nazwa usługi pełni rolę hosta w sieci wewnętrznej. Backend musi używać nazwy `db`, aby poprawnie połączyć się z kontenerem `PostgreSQL`

**Błąd 2 – brak wspólnej sieci między backendem a bazą danych**

**Przed naprawą**:

```bash
db:
networks:
    - db_network
 ...

backend:
  networks:
    - app_network
```
**Diagnoza:**

Pomimo uruchomienia bazy danych, backend nie był w stanie się z nią połączyć. Wynikało to z faktu, że oba serwisy znajdowały się w różnych sieciach `Dockera` i nie miały możliwości komunikacji.

**Po naprawie:**

```bash
backend:
  networks:
    - app_network
    - db_network
```
**Dlaczego działa:**

Kontenery w `Dockerze` mogą komunikować się tylko wtedy, gdy znajdują się w tej samej sieci. Dodanie backendu do `db_network` umożliwiło połączenie z bazą danych.

**Błąd 3 – niepoprawna ścieżka wolumenu PostgreSQL**

**Przed naprawą:**
```bash
- postgres_data:/var/lib/postgresql
```
**Diagnoza:**

Analiza konfiguracji wykazała, że wolumen został zamontowany do niepoprawnej ścieżki `/var/lib/postgresql`, która nie jest domyślnym katalogiem przechowywania danych przez `PostgreSQL`.

Może to prowadzić do problemów z inicjalizacją bazy danych lub brakiem trwałości danych - nieprawidłowa ścieżka wolumenu powoduje, że dane nie są zapisywane we właściwym miejscu.

**Po naprawie:**
```bash
- postgres_data:/var/lib/postgresql/data
```
**Dlaczego działa:**

PostgreSQL zapisuje dane w katalogu `/var/lib/postgresql/data`. Poprawna ścieżka zapewnia trwałość danych oraz prawidłowe działanie bazy.

**Błąd 4 – brak zależności między backendem a bazą danych**

**Przed naprawą:**
```bash
backend:
  build: ./backend
```
**Diagnoza:**

Backend próbował połączyć się z bazą danych zanim ta była gotowa do przyjmowania połączeń, co powodowało błędy i zakończenie działania aplikacji.

**Po naprawie:**
```bash
backend:
  build: ./backend
  depends_on:
    db:
      condition: service_healthy
```
**Dlaczego działa:**

Mechanizm `depends_on` z warunkiem `service_healthy` powoduje, że backend uruchamia się dopiero wtedy, gdy baza danych jest w pełni gotowa, co eliminuje problem z przedwczesnym połączeniem.

### Krok 6 - weryfikacja podstawowego działania
Po wprowadzeniu poprawek uruchomiono ponownie aplikację i zweryfikowano jej poprawne działanie.

W logach kontenerów nie pojawiały się już błędy, a wszystkie serwisy uruchomiły się prawidłowo:

![Działające kontenery](screenshots/s6.png)

Następnie sprawdzono dostępność `backendu`:

![Sprawdzenie backendu](screenshots/s7.png)

Sprawdzono również działanie `frontendu`:

![Sprawdzenie frontendu](screenshots/s8.png)

Odpowiedź zawierała poprawną stronę HTML aplikacji.

Na koniec zweryfikowano endpoint `/items`:

![Zweryfikowanie items](screenshots/s9.png)

Na podstawie powyższych testów można stwierdzić, że aplikacja działa poprawnie, a komunikacja pomiędzy frontendem, backendem oraz bazą danych została prawidłowo skonfigurowana.

### Krok 7 - weryfikacja persystencji danych
W ostatnim kroku sprawdzono, czy dane zapisane w bazie danych są trwałe po ponownym uruchomieniu aplikacji.

Najpierw dodano przykładowy element za pomocą:

```bash
curl -X POST http://localhost:5001/items \
  -H "Content-Type: application/json" \
  -d '{"name": "element testowy"}'
```

Następnie sprawdzono listę elementów i uzyskano wynik: 

![Dodanie elementu](screenshots/s10.png)

Kolejno, zatrzymano i ponownie uruchomiono aplikację:
```bash
docker compose down
docker compose up
```
![Zatrzymanie i uruchomienie](screenshots/s11.png)

Po restarcie ponownie sprawdzono dane:

![Sprawdzenie danych](screenshots/s12.png)

Zauważono, że dane zostały zachowane po restarcie aplikacji, co oznacza, że wolumen `Docker` działa poprawnie i zapewnia trwałość danych.

Następnie usunięto kontenery wraz z wolumenami:

![Usuniecie kontenerów i wolumerów](screenshots/s13.png)

Po ponownym uruchomieniu sprawdzono dane:

![Sprawdzenie danych po usunieciu wolumerów](screenshots/s14.png)

Po usunięciu wolumenu dane zostały utracone, co potwierdza, że były one przechowywane w wolumenie `Docker`, a nie w kontenerze.

## Podsumowanie

W ramach laboratorium przeprowadzono proces diagnozy i naprawy aplikacji wieloserwisowej działającej w środowisku `Docker` z wykorzystaniem `Docker Compose`:

- **Analiza logów** – umożliwiła identyfikację problemów związanych z brakiem połączenia backendu z bazą danych.
- **Poprawa konfiguracji** – wprowadzenie zmian w pliku `docker-compose.yml` pozwoliło usunąć błędy i zapewnić poprawną komunikację między serwisami.
- **Konfiguracja sieci i zależności** – poprawne ustawienie sieci oraz dyrektywy `depends_on` umożliwiło prawidłową współpracę kontenerów.
- **Zarządzanie danymi** – wykorzystanie wolumenów `Docker` zapewniło trwałość danych po ponownym uruchomieniu aplikacji.
- **Testowanie aplikacji** – użycie narzędzia `curl` pozwoliło zweryfikować poprawność działania endpointów oraz integrację wszystkich komponentów systemu.

## Tematy dodatkowe

### Docker network: bridge vs host

Tryb `bridge` tworzy izolowaną sieć dla kontenerów i umożliwia komunikację między nimi poprzez nazwy serwisów. Jest to tryb domyślny i najczęściej używany w aplikacjach wieloserwisowych.

Tryb `host` powoduje, że kontener korzysta bezpośrednio z sieci hosta, bez izolacji. Zapewnia to lepszą wydajność, ale ogranicza bezpieczeństwo i może prowadzić do konfliktów portów.

**Zastosowanie:**
- `bridge` – aplikacje wieloserwisowe (np. backend + baza danych),
- `host` – gdy potrzebna jest maksymalna wydajność lub bezpośredni dostęp do portów.

---

### Named volume vs bind mount

`Named volume` to wolumen zarządzany przez Dockera, przechowywany w jego wewnętrznej strukturze. Zapewnia większe bezpieczeństwo i łatwiejsze zarządzanie danymi.

`Bind mount` to bezpośrednie mapowanie katalogu z systemu hosta do kontenera. Umożliwia łatwy dostęp do plików z poziomu systemu, ale jest bardziej zależny od struktury systemu operacyjnego.

**Zastosowanie:**
- `named volume` – dane aplikacyjne (np. baza danych),
- `bind mount` – praca developerska (np. kod źródłowy).

---

### HEALTHCHECK i depends_on

Dyrektywa `HEALTHCHECK` w Dockerfile lub docker-compose pozwala określić, czy kontener działa poprawnie (np. czy baza przyjmuje połączenia).

W połączeniu z `depends_on: condition: service_healthy` umożliwia uruchomienie jednego serwisu dopiero wtedy, gdy drugi jest w pełni gotowy.

Dzięki temu można uniknąć problemów z uruchamianiem aplikacji zanim zależne usługi (np. baza danych) będą dostępne.
