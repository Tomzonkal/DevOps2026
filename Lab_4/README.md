# DevOps2026
## ZADANIE 4 DOCKER

Cel laboratoriów.
Celem laboratoriów jest zapoznanie się z podstawami Dockera i Docker Compose poprzez diagnozę i naprawę celowo zepsutej aplikacji wieloserwisowej. Studenci nauczą się analizować logi kontenerów, rozumieć konfigurację sieci, wolumenów i zależności między serwisami.


## WSTĘP TEORETYCZNY ##

[Docker Compose — dokumentacja oficjalna](https://docs.docker.com/compose/)

[Docker Networking — sieci w Docker Compose](https://docs.docker.com/compose/networking/)

[Docker Volumes — wolumeny i persystencja danych](https://docs.docker.com/storage/volumes/)

#### APLIKACJA TO NIE JEDEN KONTENER ####

Nowoczesne aplikacje składają się z wielu współpracujących serwisów: frontendu, backendu, bazy danych, kolejek wiadomości itp. Docker Compose pozwala zdefiniować całą architekturę w jednym pliku `docker-compose.yml` i uruchamiać ją jedną komendą.

Kluczową zasadą jest to, że **serwisy komunikują się przez nazwy** zdefiniowane w `docker-compose.yml`, a nie przez adresy IP. Serwis `backend` może połączyć się z bazą danych pisząc po prostu `db:5432` — Docker wewnętrznie rozwiązuje te nazwy na odpowiednie adresy IP kontenerów.

Aby serwisy mogły się ze sobą komunikować, muszą znajdować się w **tej samej sieci**. Docker Compose tworzy domyślną sieć, ale przy ręcznym definiowaniu sieci programista musi zadbać o to, że każdy serwis jest przypisany do odpowiedniej sieci.

#### LLM JAKO NARZĘDZIE DIAGNOSTYCZNE ####

W tym laboratorium świadomie korzystamy z modeli językowych (LLM, np. Claude) jako narzędzia do diagnozy błędów. Jest to akceptowana i promowana praktyka w nowoczesnym DevOpsie. Zadanie polega na:
1. Wklejeniu logów błędów do LLM
2. Przeanalizowaniu odpowiedzi i zrozumieniu wskazanego problemu
3. Samodzielnym wprowadzeniu poprawki w pliku konfiguracyjnym
4. Zrozumieniu *dlaczego* poprawka działa — to jest najważniejszy element oceny


## Aby zaliczyć laboratoria, należy wykonać następujące kroki: ##

### 1 Zaktualizować repo w kilku krokach

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
git switch -c lab_4/new_branch_nrIndeksu
git push
```

### 3 Przygotowanie środowiska pracy

- 3.1 Skopiować folder `app_0000` do `app_nrIndeksu`

```bash
cp -r Lab_4/app_0000 Lab_4/app_123456
```

- 3.2 W skopiowanym folderze stworzyć plik `.env` na podstawie `.env.example`

```bash
cp Lab_4/app_123456/.env.example Lab_4/app_123456/.env
```

Cała dalsza praca odbywa się wewnątrz folderu `app_nrIndeksu`. Nie modyfikuj `app_0000`.

### 4 Uruchomienie aplikacji i obserwacja błędów

- 4.1 Przejść do swojego folderu i uruchomić aplikację

```bash
cd Lab_4/app_123456
docker compose up --build
```

- 4.2 Obserwować logi w terminalu. Aplikacja zawiera celowe błędy — backend nie połączy się z bazą danych. Zanotować treść komunikatów błędów (będą potrzebne w sprawozdaniu).

- 4.3 W celu sprawdzenia stanu serwisów (w osobnym terminalu):

```bash
docker compose ps
```

- 4.4 Zatrzymać aplikację

```bash
docker compose down
```

### 5 Diagnoza i naprawa błędów

- 5.1 Otworzyć plik `docker-compose.yml` w swoim folderze i przeanalizować jego zawartość.

- 5.2 Skorzystać z LLM (np. Claude) lub samodzielnie zdiagnozować problemy. Wkleić do LLM komunikaty błędów z logów oraz treść pliku `docker-compose.yml` z prośbą o wskazanie problemów.

- 5.3 Znajdź i napraw wszystkie błędy w pliku `docker-compose.yml` korzystając z logów i analizy konfiguracji.

  Na podstawie komunikatów błędów z logów oraz treści pliku `docker-compose.yml` zidentyfikuj nieprawidłowości i wprowadź odpowiednie poprawki. Każdą zmianę udokumentuj w sprawozdaniu zgodnie z punktem 5.4.

- 5.4 Dla każdego błędu zapisać w sprawozdaniu:
  - Co było błędem (fragment kodu przed naprawą)
  - Jak został zdiagnozowany (co powiedział LLM / jaki log wskazał problem)
  - Jak został naprawiony (fragment kodu po naprawie)
  - Dlaczego naprawa działa (wyjaśnienie techniczne)

### 6 Weryfikacja podstawowego działania

- 6.1 Uruchomić naprawioną aplikację

```bash
docker compose up --build
```

- 6.2 Zweryfikować, że backend odpowiada na `/health`

```bash
curl http://localhost:5000/health
```

Oczekiwana odpowiedź: `{"status": "ok"}`

- 6.3 Zweryfikować, że frontend jest dostępny

```bash
curl http://localhost:80
```

Oczekiwana odpowiedź: strona HTML aplikacji

- 6.4 Zweryfikować, że endpoint `/items` działa

```bash
curl http://localhost:5000/items
```

Oczekiwana odpowiedź: `[]` (pusta lista)

### 7 Weryfikacja persystencji danych

- 7.1 Dodać przykładowy element przez API

```bash
curl -X POST http://localhost:5000/items \
  -H "Content-Type: application/json" \
  -d '{"name": "element testowy"}'
```

- 7.2 Zweryfikować, że element pojawił się na liście

```bash
curl http://localhost:5000/items
```

- 7.3 Zatrzymać i ponownie uruchomić aplikację

```bash
docker compose down
docker compose up
```

- 7.4 Sprawdzić, czy dane przetrwały restart

```bash
curl http://localhost:5000/items
```

Oczekiwana odpowiedź: lista zawierająca wcześniej dodany element — potwierdza poprawne działanie wolumenu.

- 7.5 Usunąć wolumen i zweryfikować czysty stan

```bash
docker compose down -v
docker compose up
curl http://localhost:5000/items
```

Oczekiwana odpowiedź: `[]` — baza danych jest pusta po usunięciu wolumenu.

### 8 Sprawozdanie

- 8.1 Sprawozdanie ma być dokumentacją pracy, tj. opisem wykonanych kroków wraz z logami, zrzutami ekranu i opisem procesu diagnostycznego. Ma ono pozwolić na odtworzenie zadania z wykorzystaniem instrukcji ze sprawozdania.

- 8.2 Ma być ono zapisane za pomocą Markdown w nowo stworzonym folderze `app_nrIndeksu/`.

- 8.3 Sprawozdanie musi zawierać:
  - Opis każdego z 4 znalezionych błędów (przed/po naprawie)
  - Logi błędów, które doprowadziły do diagnozy
  - Odpowiedź LLM lub własną analizę wskazującą błąd
  - Wyjaśnienie techniczne każdej naprawy
  - Wyniki komend `curl` z kroku 6 i 7 potwierdzające poprawne działanie

- 8.4 Wykonać commit i wypchnąć zmiany

```bash
git add Lab_4/app_123456/
git commit -m "lab_4: naprawiono docker-compose i dodano sprawozdanie"
git push
```


### Zaliczenie laboratoriów
- Sprawozdanie w docelowej lokalizacji
- Gotowe do oddania praca i sprawozdanie w postaci pull requesta (można dodać commita do brancha z już utworzonym pull requestem, aby dodać sprawozdanie)
- Wszelkie edycje skryptów testowych i automatyzujących workflow są zabronione (czyli plików niewymienionych w instrukcji)
- Pushe mają być wykonywane WYŁĄCZNIE Z NASZYCH KONT GITHUB

### Tematy do rozwinięcia w sprawozdaniu w celu podniesienia oceny

Ocena jest podwyższona o ile wcześniejsze kroki instrukcji zostały wykonane. Nie ma możliwości zaliczenia laboratoriów samym tematem dodatkowym.

Tematy te proszę zamieścić w osobnym rozdziale:

- czym różni się Docker network `bridge` od `host` — kiedy użyć każdego z nich
- co to named volume vs bind mount — czym się różnią i w jakich sytuacjach stosuje się każde rozwiązanie
- co robi dyrektywa `HEALTHCHECK` w Dockerfile i jak to integruje się z `depends_on: condition: service_healthy` w Docker Compose
