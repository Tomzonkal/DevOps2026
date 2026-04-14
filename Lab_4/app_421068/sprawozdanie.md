# Sprawozdanie - Lab 4 Docker
> **Autor:** 421068  
> **Data:** 2026-04-07  
> **Repozytorium:** git@github.com:Tomzonkal/DevOps2026.git

---

## Cel laboratorium
Laboratorium polegało na praktycznym zapoznaniu się z narzędziami Docker i Docker Compose. Zadanie wymagało uruchomienia celowo uszkodzonej aplikacji wieloserwisowej, zidentyfikowania przyczyn błędów na podstawie logów oraz wprowadzenia odpowiednich poprawek w pliku konfiguracyjnym `docker-compose.yml`.

---

## 1. Przygotowanie środowiska

### 1.1 Aktualizacja repozytorium i stworzenie brancha

```bash
git fetch --all
git checkout main
git pull
git switch -c lab_4/new_branch_421068
git push
```

### 1.2 Skopiowanie folderu aplikacji i pliku .env

```bash
cp -r Lab_4/app_0000 Lab_4/app_421068
cp Lab_4/app_421068/.env.example Lab_4/app_421068/.env
```

---
## 2. Uruchomienie aplikacji i obserwacja błędów

### 2.1 Uruchomienie aplikacji

Po przejściu do folderu projektu uruchomiono aplikację z flagą `--build`,
która wymusza ponowne zbudowanie obrazów:

```bash
cd Lab_4/app_421068
docker compose up --build
```


### 2.2 Obserwacja błędów w logach

W trakcie uruchamiania w logach backendu pojawiły się krytyczne błędy.
Serwis backend nie był w stanie nawiązać połączenia z bazą danych
i po 10 nieudanych próbach zakończył działanie z kodem 1:

![Błąd połączenia backendu z bazą danych](screen_10_backend_error.png)

Zaobserwowane komunikaty błędów:
- `[INFO] Database not ready, retrying (1/10)...` — backend wielokrotnie
  próbował połączyć się z bazą
- `Error: Could not connect to database after 10 attempts` — po wyczerpaniu
  prób backend zakończył działanie
- `backend-1 exited with code 1` — serwis zatrzymał się z błędem

### 2.3 Sprawdzenie stanu serwisów

W osobnym terminalu wykonano polecenie `docker compose ps` w celu weryfikacji
stanu wszystkich serwisów.


### 2.4 Zatrzymanie aplikacji

Po zebraniu informacji o błędach aplikację zatrzymano:

```bash
docker compose down
```

![Stan serwisów - brak backendu na liście](screen_11_docker_ps.png)
---


## 3. Diagnoza i naprawa błędów

Na podstawie logów oraz analizy pliku `docker-compose.yml` przy pomocy LLM (Claude) zidentyfikowano 4 błędy.

---

### Błąd 1 - Nieprawidłowa nazwa hosta w adresie połączenia z bazą danych

**Kod przed naprawą:**
```yaml
DATABASE_URL: postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@database:5432/${POSTGRES_DB}
```

**Zaobserwowany problem:**
W logach backendu widać `Database not ready, retrying (1/10)...` aż do `Could not connect to database after 10 attempts`. Backend próbował połączyć się z hostem `database`, który nie istniał w sieci Docker Compose.

**Analiza z pomocą LLM (Claude):**
W Docker Compose każdy serwis jest rozpoznawalny w sieci wewnętrznej pod nazwą nadaną mu w pliku `docker-compose.yml`. Serwis bazy danych został zdefiniowany pod nazwą `db`, natomiast w zmiennej `DATABASE_URL` podano nieistniejącą nazwę `database`.

**Kod po naprawie:**
```yaml
DATABASE_URL: postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@db:5432/${POSTGRES_DB}
```

**Dlaczego naprawa działa:**
Docker Compose udostępnia wbudowany mechanizm DNS, który tłumaczy nazwy serwisów na adresy IP kontenerów. Po zmianie nazwy hosta z `database` na `db` backend poprawnie lokalizuje kontener bazy danych.

---

### Błąd 2 - Brak mechanizmu oczekiwania na gotowość bazy danych

**Kod przed naprawą:**
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

**Zaobserwowany problem:**
Backend uruchamiał się równolegle z bazą danych i natychmiast próbował się z nią połączyć, zanim ta zdążyła zakończyć inicjalizację.

**Analiza z pomocą LLM (Claude):**
Domyślnie Docker Compose uruchamia wszystkie serwisy niemal jednocześnie, bez gwarancji kolejności. PostgreSQL potrzebuje czasu na inicjalizację klastra i uruchomienie serwera. Brak `depends_on` powodował że backend zawsze trafiał na niedziałającą jeszcze bazę.

**Kod po naprawie:**
```yaml
backend:
  build: ./backend
  depends_on:
    db:
      condition: service_healthy
  environment:
    DATABASE_URL: ...
  ports:
    - "5000:5000"
  networks:
    - app_network
    - db_network
```

**Dlaczego naprawa działa:**
Konfiguracja `depends_on` z warunkiem `service_healthy` wstrzymuje uruchomienie backendu do momentu gdy healthcheck serwisu `db` zwróci pozytywny wynik. Healthcheck był już skonfigurowany przy użyciu `pg_isready`.

---

### Błąd 3 - Backend i baza danych w oddzielnych sieciach

**Kod przed naprawą:**
```yaml
backend:
  networks:
    - app_network
```

**Zaobserwowany problem:**
Nawet po poprawieniu nazwy hosta backend nadal nie mógł skomunikować się z bazą - serwisy były izolowane w różnych sieciach.

**Analiza z pomocą LLM (Claude):**
Serwis `db` był przypisany wyłącznie do sieci `db_network`, a backend tylko do `app_network`. W Docker Compose kontenery mogą komunikować się jedynie wtedy gdy należą do co najmniej jednej wspólnej sieci.

**Kod po naprawie:**
```yaml
backend:
  networks:
    - app_network
    - db_network
```

**Dlaczego naprawa działa:**
Przypisanie backendu do obu sieci rozwiązuje problem izolacji. Sieć `app_network` służy do komunikacji z frontendem, natomiast `db_network` umożliwia dostęp do bazy danych.

---

### Błąd 4 - Wolumen zamontowany pod błędną ścieżką

**Kod przed naprawą:**
```yaml
db:
  volumes:
    - postgres_data:/var/lib/postgresql
```

**Zaobserwowany błąd w logach:**
```
initdb: error: directory "/var/lib/postgresql/data" exists but is not empty
db-1 exited with code 1
```

**Analiza z pomocą LLM (Claude):**
PostgreSQL zapisuje pliki bazy danych w podkatalogu `/var/lib/postgresql/data`, nie bezpośrednio w `/var/lib/postgresql`. Wolumen był montowany o jeden poziom za wysoko — dane nie były persystowane i przy każdym restarcie baza inicjalizowała się od nowa.

**Kod po naprawie:**
```yaml
db:
  volumes:
    - postgres_data:/var/lib/postgresql/data
```

**Dlaczego naprawa działa:**
Wskazanie poprawnej ścieżki powoduje że wolumen jest montowany dokładnie tam gdzie PostgreSQL przechowuje dane. Pierwsze uruchomienie inicjalizuje pusty wolumen, a każde kolejne odczytuje istniejące dane.

---

## 4. Uruchomienie naprawionej aplikacji

Po wprowadzeniu wszystkich poprawek uruchomiono aplikację ponownie:

```bash
docker compose up --build
```

Po wprowadzeniu wszystkich poprawek aplikacja uruchomiła się poprawnie. Widoczne jest że backend czeka na gotowość bazy (`Waiting` -> `Healthy`) zanim wystartuje:

![Poprawne uruchomienie po naprawach - depends_on działa](build_after_fix.png)

---

## 5. Weryfikacja podstawowego działania


### 5.2 GET /health - sprawdzenie stanu backendu

Wykonano zapytanie do endpointu `/health`. Backend odpowiedział kodem 200 i zwrócił `{"status":"ok"}`, co potwierdza poprawne działanie serwisu i połączenie z bazą danych.

![Wynik curl /health - status 200 OK](curl_health.png)

### 5.3 GET localhost:80 - sprawdzenie frontendu

Wykonano zapytanie do frontendu. Nginx zwrócił kod 200 i stronę HTML aplikacji DevOps2026 - Lab 4, co potwierdza poprawne działanie serwisu frontendowego.

![Wynik curl localhost:80 - strona HTML](curl_frontend.png)

### 5.4 GET /items - sprawdzenie endpointu listy

Wykonano zapytanie do endpointu `/items`. Backend zwrócił kod 200 i pustą listę `[]`, co potwierdza że API działa i baza danych jest dostępna.

![Wynik curl /items - pusta lista](curl_items_empty.png)

---

## 6. Weryfikacja persystencji danych

### 6.1 Dodanie elementu testowego (POST /items)

```
curl -X POST http://localhost:5000/items \
  -H "Content-Type: application/json" \
  -d '{"name": "element testowy"}'
```

### 6.2 Sprawdzenie listy po dodaniu elementu

```
curl http://localhost:5000/items
```

![GET /items — element widoczny na liście](items_after_post.png)

### 6.3 Sprawdzenie po restarcie bez usuwania wolumenu

```bash
docker compose down
docker compose up
curl http://localhost:5000/items
```

Po wykonaniu `docker compose down` i `docker compose up` element testowy nadal był widoczny na liście - wolumen działa poprawnie i dane przetrwały restart.

![element widoczny na liście po restarcie](items_after_restart.png)

### 6.4 Sprawdzenie po usunięciu wolumenu (docker compose down -v)

```bash
docker compose down -v
docker compose up
curl http://localhost:5000/items
```

![GET /items po down -v — pusta lista](items_after_restart_empty.png)

Lista jest pusta - wolumen został usunięty, baza zainicjalizowana od nowa. Potwierdza to poprawne działanie mechanizmu persystencji.

## 7. Tematy dodatkowe

### 7.1 Docker network: bridge vs host

**Bridge** to domyślny tryb sieciowy w Docker Compose. Każdy kontener otrzymuje
własny wirtualny interfejs sieciowy i jest izolowany od hosta oraz innych sieci.
Kontenery w tej samej sieci bridge komunikują się przez wewnętrzny DNS Dockera
(po nazwie serwisu), natomiast dostęp z zewnątrz wymaga jawnego mapowania portów
(`ports: "8080:80"`). W tym laboratorium użyto właśnie trybu bridge - sieci
`app_network` i `db_network` były od siebie odizolowane, co było jednym z celowo
wprowadzonych błędów.

**Host** eliminuje warstwę wirtualizacji sieci - kontener współdzieli stos sieciowy
bezpośrednio z hostem. Nie ma izolacji portów ani potrzeby ich mapowania.
Tryb host działa wyłącznie na Linuksie i jest stosowany gdy liczy się minimalne
opóźnienia sieciowe (np. aplikacje wysokiej przepustowości, monitoring sieci,
narzędzia typu sniffer).

**Kiedy używać:**
- `bridge` - zdecydowana większość zastosowań: aplikacje wieloserwisowe,
  środowiska deweloperskie, sytuacje gdzie izolacja sieciowa jest pożądana
- `host` - gdy potrzebna jest maksymalna wydajność sieciowa lub narzędzie
  musi mieć bezpośredni dostęp do interfejsów sieciowych hosta

**Wniosek:** W środowiskach produkcyjnych i deweloperskich należy domyślnie
stosować tryb `bridge`. Zapewnia on izolację, przewidywalność i bezpieczeństwo.
Tryb `host` to narzędzie dla specyficznych przypadków, gdzie izolacja jest
świadomie poświęcana na rzecz wydajności.

---

### 7.2 Named volume vs bind mount

**Named volume** to wolumin zarządzany przez Dockera. Docker sam tworzy i przechowuje
dane w swojej wewnętrznej lokalizacji (na Linuksie `/var/lib/docker/volumes/`).
Programista odwołuje się do niego tylko po nazwie:

```yaml
volumes:
  - postgres_data:/var/lib/postgresql/data
```

Dane istnieją niezależnie od cyklu życia kontenerów i są przenośne między środowiskami.
W tym laboratorium użyto named volume dla bazy PostgreSQL - jeden z błędów polegał
właśnie na podaniu złej ścieżki montowania wolumenu.

**Bind mount** to bezpośrednie zamontowanie konkretnego katalogu z systemu plików hosta:

```yaml
volumes:
  - ./backend:/app
```

Zmiany w plikach na hoście są natychmiast widoczne w kontenerze i odwrotnie.
Bind mount jest ściśle powiązany ze strukturą katalogów maszyny, na której uruchamiany
jest kontener.

**Kiedy używać:**
- `named volume` - dane produkcyjne, bazy danych, pliki które mają przetrwać
  restart kontenera bez zależności od struktury katalogów hosta
- `bind mount` - development (hot reload kodu), współdzielenie plików
  konfiguracyjnych między hostem a kontenerem, sytuacje gdzie potrzebny jest
  bezpośredni dostęp do plików z poziomu hosta

**Wniosek:** Named volumes są bezpieczniejsze i bardziej przenośne - Docker
zarządza ich lokalizacją i cyklem życia. Bind mounty są wygodne podczas
developmentu, ale wprowadzają zależność od struktury katalogów konkretnej maszyny,
co utrudnia przenoszenie aplikacji między środowiskami.

---

### 7.3 HEALTHCHECK w Dockerfile a depends_on w Docker Compose

**HEALTHCHECK** to dyrektywa Dockerfile definiująca komendę, którą Docker
cyklicznie wykonuje wewnątrz kontenera aby sprawdzić czy serwis działa poprawnie.
Kontener może mieć jeden z trzech stanów: `starting`, `healthy` lub `unhealthy`.

W tym laboratorium healthcheck dla bazy danych był zdefiniowany w `docker-compose.yml`:

```yaml
healthcheck:
  test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB}"]
  interval: 5s
  timeout: 5s
  retries: 5
```

Komenda `pg_isready` sprawdza czy PostgreSQL jest gotowy na przyjęcie połączeń.
Docker wykonuje ją co 5 sekund, maksymalnie 5 razy zanim uzna kontener za `unhealthy`.

**Integracja z depends_on:**

```yaml
backend:
  depends_on:
    db:
      condition: service_healthy
```

Dyrektywa `depends_on` z warunkiem `service_healthy` powoduje że Docker Compose
wstrzymuje uruchomienie backendu do momentu gdy kontener `db` osiągnie stan `healthy`.
Bez tego warunku Docker Compose gwarantuje jedynie kolejność *startu* kontenerów,
nie ich *gotowość* — co było jednym z błędów w tym laboratorium. Backend startował
równolegle z bazą i próbował się połączyć zanim PostgreSQL zdążył się zainicjalizować.

**Wniosek:** Sam `depends_on` bez `condition: service_healthy` to pułapka —
kontener może być uruchomiony, ale serwis wewnątrz jeszcze nie gotowy.
Połączenie HEALTHCHECK z `condition: service_healthy` to jedyny niezawodny
sposób na zagwarantowanie właściwej kolejności inicjalizacji serwisów
w aplikacjach wielokontenerowych.

#
## 9. Wnioski końcowe

Laboratorium pozwoliło na praktyczne zrozumienie kluczowych mechanizmów Docker
Compose - sieci, wolumenów i zależności między serwisami. Praca z celowo zepsutą
aplikacją pokazała że błędy konfiguracyjne mogą być nieoczywiste i dawać podobne
objawy mimo różnych przyczyn. Diagnoza logów przy pomocy LLM okazała się skutecznym
podejściem, które przyspieszyło identyfikację problemów i zrozumienie ich przyczyn.
Największą lekcją jest to że poprawna konfiguracja Docker Compose wymaga dokładności -  drobne błędy jak zła ścieżka wolumenu czy brak wspólnej sieci potrafią całkowicie
uniemożliwić działanie aplikacji.
