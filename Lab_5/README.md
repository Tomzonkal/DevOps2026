# DevOps2026
## ZADANIE 5 DOCKER SECURITY

Cel laboratoriów.
Celem laboratoriów jest zapoznanie się z typowymi problemami bezpieczeństwa w konfiguracji Dockera i Docker Compose. Studenci nauczą się identyfikować i naprawiać luki bezpieczeństwa w Dockerfile oraz pliku `docker-compose.yml`, rozumieć konsekwencje każdego z błędów oraz stosować dobre praktyki w budowaniu bezpiecznych obrazów kontenerów.

W odróżnieniu od Lab 4 — **aplikacja działa poprawnie**, ale zawiera poważne problemy bezpieczeństwa. Zadaniem studenta jest ich znalezienie i naprawienie.


## WSTĘP TEORETYCZNY ##

[Docker Security — oficjalna dokumentacja](https://docs.docker.com/engine/security/)

[Dockerfile best practices — bezpieczeństwo obrazów](https://docs.docker.com/build/building/best-practices/)

[OWASP Docker Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Docker_Security_Cheat_Sheet.html)

[Docker Secrets — zarządzanie sekretami](https://docs.docker.com/compose/how-tos/use-secrets/)

#### DLACZEGO BEZPIECZEŃSTWO KONTENERÓW MA ZNACZENIE ####

Kontenery Docker są powszechnie stosowane w środowiskach produkcyjnych. Błędy konfiguracyjne mogą prowadzić do:
- **wycieku sekretów** — hasła i klucze API zapisane w obrazie są dostępne dla każdego, kto obraz pobierze lub skompiluje
- **eskalacji uprawnień** — kontener uruchomiony jako root może przejąć kontrolę nad hostem przy odpowiednim błędzie aplikacji
- **kompromitacji hosta** — podmontowanie gniazda Docker (`/var/run/docker.sock`) daje kontenerowi pełną kontrolę nad hostem
- **nieprzewidywalności wdrożeń** — niespięte wersje obrazów mogą zmienić się bez ostrzeżenia i zepsuć środowisko produkcyjne

#### LLM JAKO NARZĘDZIE DO SECURITY REVIEW ####

W tym laboratorium korzystamy z modeli językowych (LLM, np. Claude) jako narzędzia do przeglądu bezpieczeństwa konfiguracji. Jest to akceptowana praktyka w nowoczesnym DevOpsie. Zadanie polega na:
1. Wklejeniu zawartości plików `Dockerfile` i `docker-compose.yml` do LLM
2. Poproszeniu o wskazanie problemów bezpieczeństwa
3. Zrozumieniu każdego wskazanego problemu — dlaczego jest niebezpieczny
4. Samodzielnym wprowadzeniu poprawki
5. Udokumentowaniu *dlaczego* dany błąd stanowi zagrożenie — to jest najważniejszy element oceny


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
git switch -c lab_5/new_branch_nrIndeksu
git push
```

### 3 Przygotowanie środowiska pracy

- 3.1 Skopiować folder `app_0000` do `app_nrIndeksu`

```bash
cp -r Lab_5/app_0000 Lab_5/app_123456
```

- 3.2 W skopiowanym folderze stworzyć plik `.env` na podstawie `.env.example`

```bash
cp Lab_5/app_123456/.env.example Lab_5/app_123456/.env
```

Cała dalsza praca odbywa się wewnątrz folderu `app_nrIndeksu`. Nie modyfikuj `app_0000`.

### 4 Uruchomienie aplikacji i wstępna inspekcja

- 4.1 Przejść do swojego folderu i uruchomić aplikację

```bash
cd Lab_5/app_123456
docker compose up --build
```

- 4.2 Zweryfikować, że aplikacja działa (w osobnym terminalu)

```bash
curl http://localhost:5000/health
curl http://localhost:5000/items
```

Oczekiwane odpowiedzi: `{"status": "ok"}` oraz `[]`. Aplikacja działa — to nie są błędy runtime, lecz **problemy bezpieczeństwa ukryte w konfiguracji**.

- 4.3 Przeprowadzić inspekcję warstw zbudowanego obrazu backendu

```bash
docker history lab5_app_123456_backend --no-trunc
```

Zaobserwować, co jest widoczne w historii warstw. Zanotować obserwacje do sprawozdania.

- 4.4 Sprawdzić, z jakim użytkownikiem działa proces w kontenerze

```bash
docker compose exec backend whoami
```

Zanotować wynik do sprawozdania.

- 4.5 Zatrzymać aplikację

```bash
docker compose down
```

### 5 Identyfikacja i naprawa problemów bezpieczeństwa

Przejrzyj pliki `backend/Dockerfile`, `frontend/Dockerfile` oraz `docker-compose.yml` w poszukiwaniu 4 problemów bezpieczeństwa. Możesz skorzystać z LLM (np. Claude) — wklej zawartość plików z prośbą o security review.

Każdy z poniższych problemów musi zostać znaleziony i naprawiony:

---

**BŁĄD 1 — Niespięte wersje obrazów bazowych (`latest`)**

Wszystkie trzy serwisy używają tagu `latest`. W środowisku produkcyjnym jest to niedopuszczalne.

Symptom do znalezienia: `FROM python:latest`, `FROM nginx:latest`, `image: postgres:latest`

Naprawa: użyj konkretnych, sprawdzonych wersji, np.:
- `python:3.11-slim`
- `nginx:1.25-alpine`
- `postgres:15`

---

**BŁĄD 2 — Hardkodowane sekrety w Dockerfile (`ENV`)**

Dyrektywa `ENV` w Dockerfile zapisuje wartość na stałe w warstwie obrazu. Każdy, kto posiada obraz (np. po `docker pull` z prywatnego rejestru lub po `git clone` repozytorium), może odczytać te wartości przez `docker history` lub `docker inspect`.

Symptom do znalezienia: `ENV API_KEY=...` i `ENV SECRET_KEY=...` w `backend/Dockerfile`

Naprawa: usuń linie `ENV` z Dockerfile. Sekrety przekazuj przez sekcję `environment` w `docker-compose.yml` z odwołaniem do pliku `.env`:
```yaml
environment:
  API_KEY: ${API_KEY}
  SECRET_KEY: ${SECRET_KEY}
```

---

**BŁĄD 3 — Hardkodowane hasło w `docker-compose.yml`**

Hasło do bazy danych jest zapisane jawnym tekstem bezpośrednio w pliku `docker-compose.yml`. Ten plik trafia do repozytorium git — hasło staje się częścią historii commits, widoczną dla wszystkich z dostępem do repo.

Symptom do znalezienia: `POSTGRES_PASSWORD: "password123"` oraz `DATABASE_URL: ...password123...` w `docker-compose.yml`

Naprawa: użyj zmiennych środowiskowych z pliku `.env`:
```yaml
POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
DATABASE_URL: postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@db:5432/${POSTGRES_DB}
```
Plik `.env` **nie powinien** trafiać do repozytorium (dodaj go do `.gitignore`).

---

**BŁĄD 4 — Kontener uruchomiony jako root**

Brak dyrektywy `USER` w Dockerfile powoduje, że aplikacja działa z uprawnieniami roota wewnątrz kontenera. Przy podatności w aplikacji (np. RCE) atakujący uzyskuje uprawnienia roota — co znacznie ułatwia eskalację uprawnień na host.

Symptom do znalezienia: brak `USER` w `backend/Dockerfile`; `docker compose exec backend whoami` zwraca `root`

Naprawa: utwórz dedykowanego użytkownika systemowego i przełącz na niego przed uruchomieniem aplikacji:
```dockerfile
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser
USER appuser
```

---

- 5.1 Dla każdego błędu zapisać w sprawozdaniu:
  - Co było błędem (fragment kodu przed naprawą)
  - Jakie jest zagrożenie bezpieczeństwa (wyjaśnienie techniczne)
  - Jak został naprawiony (fragment kodu po naprawie)
  - Jak można zweryfikować, że poprawka działa

### 6 Weryfikacja po naprawie

- 6.1 Uruchomić naprawioną aplikację

```bash
docker compose up --build
```

- 6.2 Zweryfikować, że aplikacja nadal działa poprawnie

```bash
curl http://localhost:5000/health
```

Oczekiwana odpowiedź: `{"status": "ok"}`

```bash
curl http://localhost:5000/items
```

Oczekiwana odpowiedź: `[]`

- 6.3 Zweryfikować, że kontener NIE działa już jako root

```bash
docker compose exec backend whoami
```

Oczekiwana odpowiedź: `appuser` (lub nazwa wybranego użytkownika — nie `root`)

- 6.4 Zweryfikować, że sekrety NIE są widoczne w historii warstw obrazu

```bash
docker history lab5_app_123456_backend --no-trunc
```

Oczekiwane: brak wartości `API_KEY` i `SECRET_KEY` w historii warstw.

- 6.5 Dodać przykładowy element i zweryfikować persystencję

```bash
curl -X POST http://localhost:5000/items \
  -H "Content-Type: application/json" \
  -d '{"name": "element testowy"}'

docker compose down
docker compose up -d

curl http://localhost:5000/items
```

Oczekiwana odpowiedź po restarcie: lista zawierająca wcześniej dodany element.

### 7 Sprawozdanie

- 7.1 Sprawozdanie ma być dokumentacją pracy, tj. opisem wykonanych kroków wraz z logami, zrzutami ekranu i opisem procesu diagnostycznego. Ma ono pozwolić na odtworzenie zadania z wykorzystaniem instrukcji ze sprawozdania.

- 7.2 Ma być ono zapisane za pomocą Markdown w nowo stworzonym folderze `app_nrIndeksu/`.

- 7.3 Sprawozdanie musi zawierać:
  - Opis każdego z 4 znalezionych problemów bezpieczeństwa (przed/po naprawie)
  - Wyjaśnienie zagrożenia — co konkretnie może pójść źle, gdyby błąd pozostał
  - Odpowiedź LLM lub własną analizę wskazującą problem
  - Wyniki komendy `docker history` przed i po naprawie (BŁĄD 2)
  - Wyniki komendy `whoami` przed i po naprawie (BŁĄD 4)
  - Wyniki komend `curl` z kroku 6 potwierdzające poprawne działanie

- 7.4 Wykonać commit i wypchnąć zmiany

```bash
git add Lab_5/app_123456/
git commit -m "lab_5: naprawiono problemy bezpieczenstwa i dodano sprawozdanie"
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

- czym jest **Docker Content Trust (DCT)** i jak weryfikuje autentyczność obrazów — jak włączyć i co to zmienia w praktyce
- co to są **multi-stage builds** w Dockerfile i jak pomagają zmniejszyć powierzchnię ataku końcowego obrazu
- jak działa mechanizm **Docker Secrets** (`docker secret`) w Docker Swarm i czym różni się od przekazywania sekretów przez zmienne środowiskowe
