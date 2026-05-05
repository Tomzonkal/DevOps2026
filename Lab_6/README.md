# DevOps2026
## ZADANIE 6 DOCKER

Cel laboratoriów.
Celem laboratoriów jest zapoznanie się z technikami optymalizacji obrazów Docker — zmniejszanie rozmiaru finalnego obrazu, przyspieszanie buildów przez właściwe wykorzystanie cache warstw, multi-stage builds oraz dobór odpowiedniego obrazu bazowego.


## WSTĘP TEORETYCZNY ##

[Docker — budowanie obrazów (dokumentacja)](https://docs.docker.com/build/building/best-practices/)

[Multi-stage builds](https://docs.docker.com/build/building/multi-stage/)

[.dockerignore — dokumentacja](https://docs.docker.com/build/concepts/context/#dockerignore-files)

[Docker image layers — jak działają warstwy](https://docs.docker.com/storage/storagedriver/)

#### KAŻDY RUN, COPY, ADD TWORZY NOWĄ WARSTWĘ ####

Obraz Docker składa się z warstw — każda dyrektywa `RUN`, `COPY` i `ADD` w Dockerfile tworzy nową, niezmienną warstwę. Warstwy są **cache'owane** — jeżeli dana warstwa nie zmieniła się od ostatniego buildu, Docker użyje wersji z cache zamiast ją przebudowywać.

Kluczowa zasada: **instrukcje zmieniające się rzadko powinny stać wyżej, instrukcje zmieniające się często — niżej.** Jeżeli `COPY . .` stoi przed `pip install`, każda zmiana w kodzie (nawet literówka w komentarzu) unieważnia warstwę z zainstalowanymi zależnościami i zmusza Dockera do ponownego pobierania wszystkich pakietów.

#### OBRAZ PRODUKCYJNY TO NIE ŚRODOWISKO DEVELOPERSKIE ####

Finalny obraz powinien zawierać **tylko to, co jest potrzebne do uruchomienia aplikacji** — nie narzędzia do budowania, nie testy, nie zależności developerskie. Multi-stage build pozwala użyć jednego, dużego obrazu do instalacji zależności, a drugiego, minimalnego obrazu do uruchamiania aplikacji.

Porównanie popularnych obrazów bazowych Python:

| Obraz | Rozmiar | Kiedy używać |
|-------|---------|--------------|
| `python:3.11` | ~1,0 GB | Tylko do developmentu / budowania |
| `python:3.11-slim` | ~130 MB | Produkcja z bibliotekami C (numpy, psycopg2) |
| `python:3.11-alpine` | ~55 MB | Produkcja — czyste aplikacje Python bez rozszerzeń C |


## Aby zaliczyć laboratoria, należy wykonać następujące kroki: ##

### 1 Zaktualizować repo

- 1.1 Zaktualizować wszystkie metadane projektu
```bash
git fetch --all
```

- 1.2 Przełączyć się na branch main
```bash
git checkout main
```

- 1.3 Pobrać zmiany w kodzie
```bash
git pull
```

### 2 Stworzyć nowy branch

- 2.1 Stworzenie brancha z rozwiązaniem laboratorium

```bash
git switch -c lab_6/new_branch_nrIndeksu
git push
```

### 3 Przygotowanie środowiska pracy

- 3.1 Skopiować folder `app_0000` do `app_nrIndeksu`

```bash
cp -r Lab_6/app_0000 Lab_6/app_123456
```

Cała dalsza praca odbywa się wewnątrz folderu `app_nrIndeksu`. Nie modyfikuj `app_0000`.

### 4 Pomiar stanu bazowego (baseline)

Przed jakąkolwiek optymalizacją należy zmierzyć punkty odniesienia, aby mieć dowód na poprawę.

- 4.1 Przejść do swojego folderu i zbudować obraz "as-is"

```bash
cd Lab_6/app_123456
time docker build -t kalkulator-baseline .
```

Komenda `time` zmierzy całkowity czas buildu.

- 4.2 Sprawdzić rozmiar obrazu

```bash
docker images kalkulator-baseline
```

- 4.3 Zapisać w sprawozdaniu: czas buildu i rozmiar obrazu w MB — to jest Twój **baseline**.

- 4.4 Upewnić się, że aplikacja działa

```bash
docker run -d --name kalkulator-test -p 5000:5000 kalkulator-baseline
curl -X POST http://localhost:5000/calculate \
  -H "Content-Type: application/json" \
  -d '{"a": 10, "op": "+", "b": 5}'
docker stop kalkulator-test && docker rm kalkulator-test
```

Oczekiwana odpowiedź: `{"result": 15}` (operacje +, -, * zwracają liczbę całkowitą; dzielenie zwraca float, np. `{"result": 5.0}`)

### 5 Optymalizacja 1 — kolejność warstw (cache)

Otwórz `Dockerfile` i przeanalizuj kolejność instrukcji.

- 5.1 Zidentyfikuj problem: `COPY . .` stoi przed `pip install`. Oznacza to, że **każda zmiana w kodzie** (nawet jednej linii `app.py`) powoduje ponowne instalowanie wszystkich pakietów.

- 5.2 Napraw kolejność warstw i dodaj flagę `--no-cache-dir` (usuwa cache pip z warstwy, zmniejsza rozmiar obrazu). Najpierw skopiuj plik z zależnościami, zainstaluj pakiety, dopiero potem skopiuj kod aplikacji:

```dockerfile
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py .
```

- 5.3 Przetestuj działanie cache w trzech krokach:
  1. Usuń stary obraz i zbuduj nowy: `docker rmi kalkulator-baseline && docker build -t kalkulator-cache .`
  2. Zbuduj ponownie bez zmian: `docker build -t kalkulator-cache .` — warstwa `pip install` powinna być `CACHED`
  3. Wprowadź drobną zmianę w `app.py` (np. dodaj spację) i zbuduj ponownie — `pip install` nadal `CACHED`, tylko `COPY app.py` jest przebudowane

- 5.4 Zapisz obserwacje w sprawozdaniu: jak zmieniło się zachowanie cache po naprawieniu kolejności?

### 6 Optymalizacja 2 — .dockerignore

Bez pliku `.dockerignore` Docker wysyła **cały katalog** jako kontekst budowania — włącznie z `__pycache__/`, plikami testów, folderami wirtualnych środowisk itp. Rozmiar kontekstu widoczny jest w pierwszej linii outputu `docker build`.

W tym projekcie kontekst jest mały (kilka KB), więc różnica liczbowa będzie niewielka. W realnych projektach z folderem `.git/`, `node_modules/` lub dużymi plikami danych redukcja kontekstu może wynosić setki MB — a mniejszy kontekst to szybszy build i mniejsze ryzyko przypadkowego skopiowania sekretów do obrazu.

- 6.1 Sprawdzić aktualny rozmiar kontekstu budowania i zapisać go w sprawozdaniu.

- 6.2 Stworzyć plik `.dockerignore` w folderze `app_nrIndeksu/`

```
__pycache__
*.pyc
*.pyo
*.pyd
.pytest_cache
tests/
.git
.gitignore
*.md
```

- 6.3 Zbudować obraz ponownie i porównać rozmiar kontekstu

```bash
docker build -t kalkulator-ignorefile .
```

- 6.4 Zapisać w sprawozdaniu: jaki był rozmiar kontekstu przed i po dodaniu `.dockerignore`?

### 7 Optymalizacja 3 — zmiana obrazu bazowego

- 7.1 Zmienić obraz bazowy z `python:3.11` na `python:3.11-slim`

```dockerfile
FROM python:3.11-slim
```

- 7.2 Zbudować obraz i sprawdzić nowy rozmiar

```bash
docker build -t kalkulator-slim .
docker images | grep kalkulator
```

- 7.3 Sprawdzić czy aplikacja nadal działa poprawnie

```bash
docker run -d --name kalkulator-slim -p 5000:5000 kalkulator-slim
curl -X POST http://localhost:5000/calculate \
  -H "Content-Type: application/json" \
  -d '{"a": 7, "op": "*", "b": 6}'
docker stop kalkulator-slim && docker rm kalkulator-slim
```

Oczekiwana odpowiedź: `{"result": 42}`

- 7.4 (Opcjonalnie) Spróbować `python:3.11-alpine` i sprawdzić czy aplikacja się buduje. Wkleić wynik do sprawozdania.

- 7.5 Zapisać w sprawozdaniu: różnice rozmiarów między `python:3.11`, `python:3.11-slim` oraz ewentualnie `python:3.11-alpine`.

### 8 Optymalizacja 4 — multi-stage build

Obecny Dockerfile instaluje zarówno zależności produkcyjne (`requirements.txt`) jak i developerskie (`requirements-dev.txt`) w jednym obrazie. Finalny kontener nie potrzebuje narzędzi do testowania.

- 8.1 Przepisać `Dockerfile` na multi-stage build

```dockerfile
FROM python:3.11-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY app.py .
ENV PATH=/root/.local/bin:$PATH
EXPOSE 5000
CMD ["python", "app.py"]
```

Flaga `--user` w `pip install` powoduje że pakiety trafiają do `/root/.local` zamiast do systemowego `/usr/lib/python3`. Dzięki temu w drugim stage wystarczy skopiować jeden folder (`COPY --from=builder /root/.local`) zamiast przenosić całe środowisko systemowe.

- 8.2 Zbudować finalny obraz i zmierzyć rozmiar

```bash
time docker build -t kalkulator-final .
docker images kalkulator-final
```

- 8.3 Zweryfikować, że wszystkie operacje kalkulatora działają poprawnie

```bash
docker run -d --name kalkulator-final -p 5000:5000 kalkulator-final

curl http://localhost:5000/health

curl -X POST http://localhost:5000/calculate \
  -H "Content-Type: application/json" \
  -d '{"a": 10, "op": "+", "b": 5}'

curl -X POST http://localhost:5000/calculate \
  -H "Content-Type: application/json" \
  -d '{"a": 10, "op": "/", "b": 0}'

docker stop kalkulator-final && docker rm kalkulator-final
```

Endpoint `/health` powinien zwrócić `{"status": "ok"}`. Dzielenie przez zero powinno zwrócić HTTP 400.

### 9 Weryfikacja końcowa i commit

- 9.1 Upewnić się, że finalny `Dockerfile` w `app_nrIndeksu/` zawiera wszystkie 4 optymalizacje:
  - Poprawna kolejność warstw (requirements przed kodem aplikacji)
  - Plik `.dockerignore`
  - Slim jako obraz bazowy (zamiast `python:3.11`)
  - Multi-stage build (zależności developerskie nie trafiają do finalnego obrazu)

- 9.2 Wykonać commit i wypchnąć zmiany

```bash
git add Lab_6/app_123456/
git commit -m "lab_6: zoptymalizowano Dockerfile kalkulatora"
git push
```

### 10 Sprawozdanie

- 10.1 Sprawozdanie ma być dokumentacją pracy, tj. opisem wykonanych kroków wraz ze zrzutami ekranu/logami i technicznym uzasadnieniem każdej zmiany. Ma ono pozwolić na odtworzenie zadania z wykorzystaniem instrukcji ze sprawozdania.

- 10.2 Ma być ono zapisane za pomocą Markdown w nowo stworzonym folderze `app_nrIndeksu/`.

- 10.3 Sprawozdanie musi zawierać tabelę podsumowującą optymalizacje:

| Etap | Obraz bazowy | Rozmiar [MB] | Co zmieniono |
|------|-------------|--------------|--------------|
| Baseline | python:3.11 | ? | — |
| Po opt. 1 | python:3.11 | ? | Kolejność warstw |
| Po opt. 2 | python:3.11 | ? | .dockerignore |
| Po opt. 3 | python:3.11-slim | ? | Zmiana obrazu bazowego |
| Po opt. 4 | python:3.11-slim | ? | Multi-stage build |

- 10.4 Dla każdej optymalizacji napisać:
  - Co było problemem (fragment Dockerfile przed zmianą)
  - Jak został naprawiony (fragment po zmianie)
  - Dlaczego ta zmiana poprawia obraz (wyjaśnienie techniczne)


### Zaliczenie laboratoriów
- Sprawozdanie w docelowej lokalizacji
- Gotowa do oddania praca i sprawozdanie w postaci pull requesta (można dodać commita do brancha z już utworzonym pull requestem, aby dodać sprawozdanie)
- Wszelkie edycje skryptów testowych i automatyzujących workflow są zabronione (czyli plików niewymienionych w instrukcji)
- Pushe mają być wykonywane WYŁĄCZNIE Z NASZYCH KONT GITHUB

### Tematy do rozwinięcia w sprawozdaniu w celu podniesienia oceny

Ocena jest podwyższona o ile wcześniejsze kroki instrukcji zostały wykonane. Nie ma możliwości zaliczenia laboratoriów samym tematem dodatkowym.

Tematy te proszę zamieścić w osobnym rozdziale:

- Czym jest Distroless i kiedy go używać zamiast Alpine?
- Co to `ARG` a co `ENV` w Dockerfile — czym się różnią i co trafia do finalnego obrazu?
- Narzędzie `dive` do analizy warstw obrazu — jak czytać wynik i co optymalizować?
- Czym różni się `COPY --chown` od `RUN chown` — dlaczego jedno jest lepsze od drugiego?
