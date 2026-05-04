# DevOps2026
## ZADANIE 8 DOCKER I CI/CD PIPELINE

Cel laboratoriów.
Celem laboratoriów jest zbudowanie kompletnego pipeline'u CI/CD z użyciem GitHub Actions i Docker. Studenci otrzymują działającą aplikację Python oraz gotowy Dockerfile, piszą testy z pomocą AI, a następnie samodzielnie tworzą workflow GitHub Actions **od podstaw** — bez gotowego szablonu. Workflow musi budować obraz Docker, uruchamiać testy i wysyłać obraz do rejestru kontenerów (ghcr.io) tylko po pomyślnym przejściu testów.


## WSTĘP TEORETYCZNY ##

[Docker — oficjalna dokumentacja](https://docs.docker.com/)

[GitHub Actions — dokumentacja](https://docs.github.com/en/actions)

[GitHub Container Registry (ghcr.io)](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry)

[docker/build-push-action](https://github.com/docker/build-push-action)

#### CZYM JEST DOCKER ####

Docker to platforma konteneryzacji, która pakuje aplikację razem z jej zależnościami w izolowany, przenośny kontener. Kontener działa identycznie niezależnie od środowiska — lokalnie, w CI/CD, czy na serwerze produkcyjnym.

Kluczowe pojęcia:
- `Dockerfile` — przepis na zbudowanie obrazu (image): lista instrukcji instalacyjnych i konfiguracyjnych
- `docker build` — tworzenie obrazu z Dockerfile
- `docker run` — uruchomienie kontenera z gotowego obrazu
- `docker push` — wysłanie obrazu do zdalnego rejestru
- **Image tag** — unikalna nazwa obrazu, np. `ghcr.io/użytkownik/app:latest`

#### REJESTR KONTENERÓW — GITHUB CONTAINER REGISTRY ####

GitHub Container Registry (`ghcr.io`) to rejestr obrazów Docker zintegrowany bezpośrednio z GitHub. Każdy workflow ma automatycznie dostępny token `GITHUB_TOKEN`, który umożliwia logowanie do `ghcr.io` — **nie trzeba konfigurować żadnych dodatkowych sekretów**.

Format nazwy obrazu:
```
ghcr.io/<owner>/<image-name>:<tag>
```
Przykład: `ghcr.io/tomzonkal/lab8-app-123456:latest`

#### CI/CD PIPELINE Z DOCKEREM ####

Typowy pipeline Docker w GitHub Actions:
1. **Build** — zbuduj obraz Docker (`docker build`)
2. **Test** — uruchom testy (przed lub równolegle z budowaniem)
3. **Push** — wyślij gotowy obraz do rejestru (`docker push`) — **tylko jeśli testy przeszły**

Ta kolejność jest fundamentalna: nie wysyłamy do rejestru obrazu, który nie przeszedł testów.

#### DLACZEGO PISANIE WORKFLOW OD PODSTAW ####

W Lab 7 naprawiałeś istniejący, błędny workflow. W tym laboratorium piszesz workflow samodzielnie na podstawie specyfikacji — tak jak w prawdziwej pracy inżyniera DevOps, który dostaje zadanie "skonfiguruj CI/CD dla tej aplikacji" i musi dobrać narzędzia, kolejność kroków i konfigurację samodzielnie.


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
git switch -c lab_8/new_branch_nrIndeksu
git push -u origin lab_8/new_branch_nrIndeksu
```

### 3 Przygotowanie środowiska pracy

- 3.1 Skopiować folder `app_0000` do `app_nrIndeksu`

```bash
cp -r Lab_8/app_0000 Lab_8/app_nrIndeksu
```

Cała dalsza praca odbywa się wewnątrz folderu `app_nrIndeksu`. Nie modyfikuj `app_0000`.

### 4 Zapoznanie się z kodem aplikacji

- 4.1 Przeczytać plik `app.py` w swoim folderze

Aplikacja udostępnia REST API z trzema operacjami na tekście. Każdy endpoint przyjmuje JSON z polem `text` i zwraca wynik:

| Endpoint | Metoda | Przykładowe wejście | Przykładowe wyjście |
|----------|--------|---------------------|---------------------|
| `/uppercase` | POST | `{"text": "hello"}` | `{"result": "HELLO"}` |
| `/reverse` | POST | `{"text": "abcde"}` | `{"result": "edcba"}` |
| `/word-count` | POST | `{"text": "raz dwa"}` | `{"count": 2}` |
| `/health` | GET | — | `{"status": "ok"}` |

- 4.2 Uruchomić aplikację lokalnie i sprawdzić czy działa

```bash
cd Lab_8/app_nrIndeksu
pip install -r requirements.txt
python app.py
```

W osobnym terminalu przetestuj wszystkie endpointy:

```bash
curl -X POST http://localhost:5000/uppercase \
  -H "Content-Type: application/json" \
  -d '{"text": "hello world"}'
```
Oczekiwana odpowiedź: `{"result": "HELLO WORLD"}`

```bash
curl -X POST http://localhost:5000/reverse \
  -H "Content-Type: application/json" \
  -d '{"text": "abcde"}'
```
Oczekiwana odpowiedź: `{"result": "edcba"}`

```bash
curl -X POST http://localhost:5000/word-count \
  -H "Content-Type: application/json" \
  -d '{"text": "raz dwa trzy"}'
```
Oczekiwana odpowiedź: `{"count": 3}`

```bash
curl http://localhost:5000/health
```
Oczekiwana odpowiedź: `{"status": "ok"}`

- 4.3 Przerwać działanie aplikacji (`Ctrl+C`)

- 4.4 Przeczytać plik `Dockerfile` i zrozumieć każdą instrukcję

Dockerfile jest już napisany i gotowy do użycia. Przeanalizuj każdą linię — będziesz musiał opisać ją w sprawozdaniu.

### 5 Uruchomienie aplikacji w kontenerze Docker

- 5.1 Zbudować obraz Docker lokalnie (z katalogu `Lab_8/`)

```bash
docker build -t lab8-app-nrIndeksu:local app_nrIndeksu/
```

- 5.2 Uruchomić kontener i przetestować aplikację

```bash
docker run -p 5000:5000 lab8-app-nrIndeksu:local
```

Przetestuj te same endpointy co w kroku 4.2 — aplikacja działa teraz wewnątrz kontenera Docker.

- 5.3 Zatrzymać kontener (`Ctrl+C`)

### 6 Napisanie testów z pomocą AI

- 6.1 Wkleić zawartość pliku `app.py` do LLM (np. Claude) z następującą prośbą:

> *"Napisz testy pytest dla tej aplikacji Flask. Testy powinny używać biblioteki `requests` do wykonywania żądań HTTP do działającego serwera na localhost:5000. Pokryj wszystkie endpointy (/uppercase, /reverse, /word-count, /health), przypadki brzegowe (pusty tekst, tekst z wieloma spacjami, tekst z cyframi) oraz przypadki błędów (brakujące pole 'text', nieprawidłowy typ danych zamiast stringa)."*

- 6.2 Zapisać wygenerowany kod jako `test_app.py` w folderze `app_nrIndeksu/`

- 6.3 Uruchomić testy lokalnie — najpierw uruchomić aplikację w tle, następnie testy:

```bash
cd Lab_8/app_nrIndeksu
python app.py &
python -m pytest test_app.py -v
```

- 6.4 Jeżeli testy nie przechodzą — poprawić je. Może być konieczna kilkukrotna iteracja z AI. Udokumentować każdą iterację w sprawozdaniu.

- 6.5 Zatrzymać aplikację uruchomioną w tle:

```bash
kill %1
```

### 7 Napisanie workflow GitHub Actions od podstaw

**W tym laboratorium NIE ma gotowego szablonu workflow.** Musisz napisać kompletny plik YAML samodzielnie na podstawie poniższej specyfikacji.

- 7.1 Stworzyć plik `.github/workflows/lab_8_nrIndeksu.yml`

```bash
touch .github/workflows/lab_8_nrIndeksu.yml
```

- 7.2 Workflow musi spełniać następującą specyfikację:

**Trigger:** Uruchamia się na zdarzenie `push` tylko na Twoim feature branchu (`lab_8/new_branch_nrIndeksu`), **nie** na `main`.

**Permissions:** Wymaga uprawnień `packages: write` na poziomie joba (niezbędne do push obrazu do ghcr.io).

**Kroki (w tej kolejności):**
1. Checkout kodu repozytorium
2. Konfiguracja Python 3.11
3. Instalacja zależności: `pip install -r Lab_8/app_nrIndeksu/requirements.txt`
4. Uruchomienie testów: `python -m pytest Lab_8/app_nrIndeksu/test_app.py -v`
5. Logowanie do GitHub Container Registry (`ghcr.io`) przy użyciu `docker/login-action@v3`
6. Budowanie i wysyłanie obrazu Docker przy użyciu `docker/build-push-action@v6`

**Uwaga:** Kroki 5 i 6 wykonają się tylko jeśli testy (krok 4) przeszły — domyślne sekwencyjne zachowanie GitHub Actions zapewnia to automatycznie.

- 7.3 Przydatne akcje GitHub:

| Akcja | Wersja | Zastosowanie |
|-------|--------|--------------|
| `actions/checkout` | `v4` | Pobieranie kodu repozytorium |
| `actions/setup-python` | `v5` | Konfiguracja środowiska Python |
| `docker/login-action` | `v3` | Logowanie do rejestru Docker |
| `docker/build-push-action` | `v6` | Budowanie i wysyłanie obrazu |

- 7.4 Konfiguracja logowania do ghcr.io:

```yaml
- name: Log in to GitHub Container Registry
  uses: docker/login-action@v3
  with:
    registry: ghcr.io
    username: ${{ github.actor }}
    password: ${{ secrets.GITHUB_TOKEN }}
```

- 7.5 Tag obrazu Docker musi mieć format:

```
ghcr.io/${{ github.repository_owner }}/lab8-app-nrIndeksu:latest
```

Zastąp `nrIndeksu` swoim numerem indeksu. Kontekst `context:` w `build-push-action` powinien wskazywać na folder z Dockerfile, czyli `Lab_8/app_nrIndeksu`.

### 8 Weryfikacja działania workflow

- 8.1 Wypchnąć zmiany na swój branch:

```bash
git add Lab_8/app_nrIndeksu/ .github/workflows/lab_8_nrIndeksu.yml
git commit -m "lab_8: dodano testy i workflow Docker CI/CD"
git push
```

- 8.2 W zakładce **Actions** na GitHub sprawdzić, czy workflow `CI` uruchomił się na Twoim branchu i przeszedł (zielony checkmark).

- 8.3 Zweryfikować, że obraz Docker pojawił się w GitHub Container Registry:
  - Wejdź na stronę swojego profilu GitHub lub repozytorium
  - Zakładka **Packages** — powinien pojawić się obraz `lab8-app-nrIndeksu`

### 9 Pull Request

- 9.1 Stworzyć Pull Request z brancha `lab_8/new_branch_nrIndeksu` do `main` w repozytorium kursowym (DevOps2026).

- 9.2 Zweryfikować, że workflow oceniający `lab_8_github_actions` uruchomił się i przeszedł.

### 10 Sprawozdanie

- 10.1 Sprawozdanie umieścić w repozytorium [Devops_2026_sprawka](https://github.com/Tomzonkal/Devops_2026_sprawka) w folderze `Lab_8/nrIndeksu/`

```bash
git clone https://github.com/Tomzonkal/Devops_2026_sprawka.git
cd Devops_2026_sprawka
mkdir -p Lab_8/123456
# stwórz plik sprawozdania Lab_8/123456/sprawozdanie.md
git add Lab_8/123456/
git commit -m "lab_8: sprawozdanie 123456"
git push
```

- 10.2 Sprawozdanie musi zawierać:
  - Pełną zawartość napisanego pliku `lab_8_nrIndeksu.yml` z wyjaśnieniem każdego kroku
  - Opis co robi każda instrukcja w Dockerfile (FROM, WORKDIR, COPY, RUN, EXPOSE, CMD)
  - Opis procesu pisania testów z AI (ile iteracji, co poprawiałeś i dlaczego)
  - Zrzut ekranu zielonego workflow na feature branchu
  - Zrzut ekranu obrazu Docker widocznego w zakładce Packages na GitHub
  - Odpowiedź (3–5 zdań) na pytanie: **Dlaczego push obrazu Docker do rejestru powinien nastąpić dopiero po pomyślnym przejściu testów? Jakie konsekwencje miałoby odwrócenie tej kolejności?**

- 10.3 Upewnij się, że w repozytorium kursowym (DevOps2026) na swoim branchu znajdują się:
  - `Lab_8/app_nrIndeksu/test_app.py`
  - `Lab_8/app_nrIndeksu/` (wszystkie pliki: app.py, Dockerfile, requirements.txt, test_app.py)
  - `.github/workflows/lab_8_nrIndeksu.yml` (workflow napisany samodzielnie)


### Wskazówki

- Dokumentacja `docker/build-push-action`: https://github.com/docker/build-push-action
- `GITHUB_TOKEN` jest automatycznie dostępny w każdym workflow — nie musisz go konfigurować w Settings
- Jeśli workflow buduje obraz ale nie wysyła — sprawdź czy masz `push: true` w `build-push-action` i czy job ma `permissions: packages: write`
- Jeśli testy przechodzą lokalnie ale nie w CI — sprawdź ścieżki do plików (`Lab_8/app_nrIndeksu/` vs `./`)
- `docker/build-push-action` z `push: false` jest przydatne do testowania samego build bez wysyłania


### Zaliczenie laboratoriów

- Sprawozdanie w repozytorium [Devops_2026_sprawka](https://github.com/Tomzonkal/Devops_2026_sprawka) w folderze `Lab_8/nrIndeksu/`
- Kod (testy + workflow) w postaci pull requesta do repozytorium kursowego (DevOps2026)
- Wszelkie edycje skryptów testowych i automatyzujących workflow są zabronione (czyli plików niewymienionych w instrukcji)
- Pushe mają być wykonywane WYŁĄCZNIE Z NASZYCH KONT GITHUB


### Tematy do rozwinięcia w sprawozdaniu w celu podniesienia oceny

Ocena jest podwyższona o ile wcześniejsze kroki instrukcji zostały wykonane. Nie ma możliwości zaliczenia laboratoriów samym tematem dodatkowym.

Tematy te proszę zamieścić w osobnym rozdziale:

- Czym jest **multi-stage build** w Docker i jakie korzyści przynosi (rozmiar obrazu, bezpieczeństwo)?
- Co to są **Docker layer cache** i jak wpływają na czas budowania obrazów w CI/CD?
- Jaka jest różnica między tagiem `:latest` a tagiem zawierającym hash commita (`${{ github.sha }}`) — jakie ryzyko niesie używanie wyłącznie `:latest`?
