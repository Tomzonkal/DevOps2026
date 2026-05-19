# DevOps2026
## ZADANIE 9 GITHUB ACTIONS COMPOSITE ACTION

Cel laboratoriow.
Celem laboratoriow jest refaktoryzacja zduplikowanego workflow GitHub Actions z uzyciem **composite action** — wielokrotnie uzywalnej akcji przyjmujacej wersje Pythona jako parametr. Zamiast trzech identycznych jobow testujacych Python 3.9, 3.10 i 3.11 oddzielnie, student tworzy jedna composite action i uzywa jej w strategii matrix.


## WSTEP TEORETYCZNY ##

[GitHub Actions — Composite Actions](https://docs.github.com/en/actions/sharing-automations/creating-actions/creating-a-composite-action)

[Matrix strategy w GitHub Actions](https://docs.github.com/en/actions/writing-workflows/choosing-what-your-workflow-does/running-variations-of-jobs-in-a-workflow)

[Tworzenie wlasnych akcji](https://docs.github.com/en/actions/sharing-automations/creating-actions/about-custom-actions)

[Inputs w composite actions](https://docs.github.com/en/actions/sharing-automations/creating-actions/metadata-syntax-for-github-actions#inputs)

#### PROBLEM — DUPLIKACJA W WORKFLOW ####

Otworz plik `ci-naive.yml` z folderu startowego. Masz tam trzy joby: `test-python-39`, `test-python-310`, `test-python-311`. Kazdy z nich zawiera identyczne kroki:

```
checkout → setup-python → pip install → start server → pytest → stop server
```

Jedyna roznica miedzy jobami to numer wersji Pythona. To klasyczny przypadek naruszenia zasady **DRY (Don't Repeat Yourself)**. Konsekwencje:

- Jesli zmienisz sciezke do aplikacji, musisz zmienic ja w 3 miejscach
- Jesli dodasz nowy krok (np. linting), musisz dodac go 3 razy
- Jesli zechcesz testowac Python 3.12, dodajesz kolejny identyczny job

#### COMPOSITE ACTION — ROZWIAZANIE ####

Composite action to wielokrotnie uzywalna akcja zdefiniowana w pliku `action.yml`. Zamiast powielac kroki, definiujesz je raz i wywolujesz z parametrami:

```yaml
# Wywolanie composite action z parametrami
- uses: ./.github/actions/test-python-env-nrIndeksu
  with:
    python-version: '3.11'
    app-path: Lab_9/app_nrIndeksu
```

Kluczowe wlasciwosci composite action:
- `using: composite` — deklaruje typ akcji
- `inputs:` — parametry przyjmowane przez akcje (jak argumenty funkcji)
- `${{ inputs.nazwa }}` — uzycie wartosci parametru wewnatrz akcji
- kazdy krok `run:` **musi** miec `shell: bash` (w odroznieniu od zwyklych workflow)
- odwolanie do akcji lokalnej: `uses: ./.github/actions/nazwa-akcji` (sciezka wzgledna z `./`)

#### MATRIX STRATEGY ####

Matrix strategy pozwala uruchamiac jeden job wielokrotnie z roznymi wartosciami parametrow:

```yaml
jobs:
  test:
    strategy:
      matrix:
        python-version: ['3.9', '3.10', '3.11']
    steps:
      - uses: ./.github/actions/test-python-env-nrIndeksu
        with:
          python-version: ${{ matrix.python-version }}
```

GitHub Actions automatycznie tworzy trzy uruchomienia joba — po jednym dla kazdej wartosci z macierzy. Wyniki widoczne sa oddzielnie w zakladce Actions.


## Aby zaliczyc laboratoria, nalezy wykonac nastepujace kroki: ##

### 1 Zaktualizowac repo

- 1.1 Zaktualizowac wszystkie metadane projektu
```bash
git fetch --all
```

- 1.2 Przelaczyc sie na branch main
```bash
git checkout main
```

- 1.3 Pobrac zmiany w kodzie
```bash
git pull
```

### 2 Stworzyc nowy branch

- 2.1 Stworzenie brancha z rozwiazaniem laboratorium

```bash
git switch -c lab_9/new_branch_nrIndeksu
```

### 3 Przygotowanie srodowiska pracy

- 3.1 Skopiowac folder `app_0000` do `app_nrIndeksu`

```bash
cp -r Lab_9/app_0000 Lab_9/app_nrIndeksu
```

Cala dalsza praca odbywa sie wewnatrz folderu `app_nrIndeksu`. Nie modyfikuj `app_0000`.

### 4 Zapoznanie sie z kodem aplikacji i testami

- 4.1 Przeczytac plik `app.py` w swoim folderze

Aplikacja udostepnia REST API z trzema operacjami matematycznymi. Kazdy endpoint przyjmuje JSON i zwraca wynik:

| Endpoint | Metoda | Przykladowe wejscie | Przykladowe wyjscie |
|----------|--------|---------------------|---------------------|
| `/fibonacci` | POST | `{"n": 10}` | `{"result": 55}` |
| `/is-prime` | POST | `{"n": 7}` | `{"is_prime": true}` |
| `/sum-digits` | POST | `{"number": 123}` | `{"result": 6}` |
| `/health` | GET | — | `{"status": "ok"}` |

- 4.2 Uruchomic aplikacje lokalnie i sprawdzic czy dziala

```bash
cd Lab_9/app_nrIndeksu
pip install -r requirements.txt
python app.py
```

W osobnym terminalu przetestuj endpointy:

```bash
curl -X POST http://localhost:5000/fibonacci \
  -H "Content-Type: application/json" \
  -d '{"n": 10}'
```
Oczekiwana odpowiedz: `{"result": 55}`

```bash
curl -X POST http://localhost:5000/is-prime \
  -H "Content-Type: application/json" \
  -d '{"n": 7}'
```
Oczekiwana odpowiedz: `{"is_prime": true}`

```bash
curl -X POST http://localhost:5000/sum-digits \
  -H "Content-Type: application/json" \
  -d '{"number": 123}'
```
Oczekiwana odpowiedz: `{"result": 6}`

- 4.3 Przerwac dzialanie aplikacji (`Ctrl+C`)

- 4.4 Uruchomic testy lokalnie — najpierw uruchomic aplikacje w tle, nastepnie testy:

```bash
cd Lab_9/app_nrIndeksu
python app.py &
python -m pytest test_app.py -v
kill %1
```

Wszystkie testy powinny przejsc (zielone). Jesli nie — sprawdz czy aplikacja jest uruchomiona na porcie 5000.

**Sprawdz:** wszystkie testy zakonczone `PASSED` w wyniku `pytest`.

### 5 Analiza naiwnego workflow (cwiczenie — nie wymagane przez grading)

- 5.1 Otworzyc plik `ci-naive.yml` w swoim folderze i przeczytac jego zawartosc.

- 5.2 Policzyc ile razy powtarza sie identyczny blok krokow (checkout, setup-python, pip install, start server, pytest, stop server).

Ten krok sluzy zrozumieniu problemu DRY — nie musisz commitowac naiwnego workflow. Jesli chcesz zobaczyc go w akcji na GitHubie, mozesz go skopiowac i uruchomic:

```bash
cp Lab_9/app_nrIndeksu/ci-naive.yml .github/workflows/lab_9_naive_nrIndeksu.yml
# Nastepnie edytuj plik — zmien 'nrIndeksu' na swoj numer we wszystkich miejscach
git add .github/workflows/lab_9_naive_nrIndeksu.yml
git commit -m "lab_9: naiwny workflow (cwiczenie)"
git push -u origin lab_9/new_branch_nrIndeksu
```

**Sprawdz (opcjonalnie):** w zakladce **Actions** na GitHub — trzy joby w workflow `CI (naive)` dla Pythona 3.9, 3.10 i 3.11.

### 6 Stworzenie composite action

- 6.1 Stworzyc katalog dla swojej akcji:

```bash
mkdir -p .github/actions/test-python-env-nrIndeksu
```

- 6.2 Skopiowac scaffold akcji:

```bash
cp Lab_9/app_nrIndeksu/action.yml.scaffold .github/actions/test-python-env-nrIndeksu/action.yml
```

- 6.3 Uzupelnic plik `.github/actions/test-python-env-nrIndeksu/action.yml`.

Otworz plik i zastap wszystkie miejsca oznaczone `UZUPELNIJ` poprawnymi wyrazeniami. Masz dwa inputy zdefiniowane w sekcji `inputs:` — `python-version` i `app-path`. Odwoluj sie do nich przez `${{ inputs.python-version }}` i `${{ inputs.app-path }}`.

Konkretnie:
- `${{ inputs.UZUPELNIJ }}` przy `python-version:` → zastap `UZUPELNIJ` na `python-version`
- `UZUPELNIJ/requirements.txt` → zastap `UZUPELNIJ` na `${{ inputs.app-path }}`
- `python UZUPELNIJ/app.py &` → zastap `UZUPELNIJ` na `${{ inputs.app-path }}`
- `python -m pytest UZUPELNIJ/test_app.py -v` → zastap `UZUPELNIJ` na `${{ inputs.app-path }}`
- Dodaj `shell: bash` do kroku "Run tests" (jedyny krok `run:` bez tego pola)

- 6.4 Sprawdzic plik akcji lokalnie — przejsc po nim i upewnic sie, ze nie ma niezastapionego placeholdera:

**Sprawdz:** `grep -n "UZUPELNIJ" .github/actions/test-python-env-nrIndeksu/action.yml` — powinno zwrocic brak wynikow.

### 7 Napisanie workflow z matrix strategy

- 7.1 Stworzyc nowy plik workflow:

```bash
touch .github/workflows/lab_9_nrIndeksu.yml
```

- 7.2 Napisac workflow spelniajacy nastepujaca specyfikacje:

**Trigger:** zdarzenie `push` tylko na Twoim feature branchu (`lab_9/new_branch_nrIndeksu`).

**Job `test`** z matrix strategy:
```yaml
strategy:
  matrix:
    python-version: ['3.9', '3.10', '3.11']
```

**Kroki:**
1. Checkout kodu repozytorium (`actions/checkout@v4`)
2. Wywolanie Twojej composite action z parametrami

Wywolanie composite action ma wyglac tak (z odpowiednim numerem indeksu):
```yaml
- name: Test with Python ${{ matrix.python-version }}
  uses: ./.github/actions/test-python-env-nrIndeksu
  with:
    python-version: ${{ matrix.python-version }}
    app-path: Lab_9/app_nrIndeksu
```

**Uwaga:** `uses:` zaczyna sie od `./` — to sciezka wzgledna do lokalnej akcji w repozytorium. Bez `./` GitHub szuka akcji w Marketplace, a nie lokalnie.

### 8 Weryfikacja dzialania workflow

- 8.1 Wypchnac wszystkie zmiany:

```bash
git add .github/actions/test-python-env-nrIndeksu/ .github/workflows/lab_9_nrIndeksu.yml
git commit -m "lab_9: composite action i matrix workflow"
git push
```

- 8.2 W zakladce **Actions** sprawdzic, ze workflow `CI (matrix)` uruchomil sie i pokazuje trzy joby:
  - `test (3.9)`
  - `test (3.10)`
  - `test (3.11)`

Wszystkie trzy powinny byc zielone.

- 8.3 Porownac widok Actions dla `CI (naive)` i `CI (matrix)`:
  - naiwny: trzy oddzielne joby z osobnymi nazwami (`test-python-39` itd.)
  - matrix: jeden job `test` uruchomiony trzy razy z roznym parametrem

**Sprawdz:** trzy zielone checkmarki w workflow `CI (matrix)`.

### 9 Pull Request

- 9.1 Stworzyc Pull Request z brancha `lab_9/new_branch_nrIndeksu` do `main` w repozytorium kursowym (DevOps2026).

- 9.2 Zweryfikowac, ze workflow oceniajacy `lab_9_github_actions` uruchomil sie i przeszedl.

### 10 Sprawozdanie

- 10.1 Sprawozdanie umiescic w repozytorium [Devops_2026_sprawka](https://github.com/Tomzonkal/Devops_2026_sprawka) w folderze `Lab_9/nrIndeksu/`

```bash
git clone https://github.com/Tomzonkal/Devops_2026_sprawka.git
cd Devops_2026_sprawka
mkdir -p Lab_9/123456
# stworz plik sprawozdania Lab_9/123456/sprawozdanie.md
git add Lab_9/123456/
git commit -m "lab_9: sprawozdanie 123456"
git push
```

- 10.2 Sprawozdanie musi zawierac:
  - Pelna zawartosc pliku `action.yml` z wyjasnieniem kazdego pola (`name`, `inputs`, `runs`, `using`, `shell`)
  - Pelna zawartosc pliku `lab_9_nrIndeksu.yml` z wyjasnieniem sekcji `strategy.matrix`
  - Porownanie naiwnego workflow i workflow z composite action: ile linii kodu zaoszczedzono, co sie zmienilo
  - Opis co sie stalo gdy po raz pierwszy uruchomiles naiwny workflow (krok 5.4) i workflow z matrix (krok 8.2)
  - Zrzut ekranu trzech zielonych jobow w workflow `CI (matrix)`
  - Odpowiedz (3—5 zdan): **Dlaczego composite actions i matrix strategy sa lepsze od kopiowania krokow? Jakie problemy rozwiazuja w duzym projekcie z wieloma srodowiskami?**

- 10.3 Upewnij sie, ze w repozytorium kursowym (DevOps2026) na swoim branchu znajduja sie:
  - `Lab_9/app_nrIndeksu/` (wszystkie pliki: app.py, requirements.txt, test_app.py, ci-naive.yml, action.yml.scaffold)
  - `.github/actions/test-python-env-nrIndeksu/action.yml`
  - `.github/workflows/lab_9_naive_nrIndeksu.yml`
  - `.github/workflows/lab_9_nrIndeksu.yml`


### Wskazowki

- Jesli dostaniesz blad `Required property is missing: shell` — to brakuje `shell: bash` przy jednym z krokow `run:` w composite action
- Jesli dostaniesz blad `Can't find 'action.yml'` — sprawdz czy sciezka w `uses:` zaczyna sie od `./` i czy folder akcji jest poprawnie nazwany
- Jesli testy przechodza lokalnie ale nie w CI — sprawdz czy server jest gotowy przed uruchomieniem testow (petla health-check zamiast `sleep`)
- Jesli wszystkie trzy joby matrix failuja z tym samym bledem — problem jest w samej composite action, nie w wersji Pythona
- `matrix.python-version` w jobie jest dostepne jako zmienna dopiero po zadeklarowaniu sekcji `strategy.matrix`


### Zaliczenie laboratoriow

- Sprawozdanie w repozytorium [Devops_2026_sprawka](https://github.com/Tomzonkal/Devops_2026_sprawka) w folderze `Lab_9/nrIndeksu/`
- Kod (composite action + workflow matrix) w postaci pull requesta do repozytorium kursowego (DevOps2026)
- Wszelkie edycje skryptow testowych i automatyzujacych workflow sa zabronione (czyli plikow niewymienionych w instrukcji)
- Pushe maja byc wykonywane WYLACZNIE Z NASZYCH KONT GITHUB


### Tematy do rozwinieciaw sprawozdaniu w celu podniesienia oceny

Ocena jest podwyzszona o ile wczesniejsze kroki instrukcji zostaly wykonane. Nie ma mozliwosci zaliczenia laboratoriow samym tematem dodatkowym.

Tematy te prosze zamiecic w osobnym rozdziale:

- Czym jest **reusable workflow** w GitHub Actions i czym rozni sie od composite action — kiedy stosowac kazde z nich?
- Co to jest `fail-fast` w matrix strategy i kiedy warto je wylaczac (`fail-fast: false`)?
- Jak dziala **caching zaleznosci** (`actions/cache`) i jak dodac go do composite action zeby przyspieszyc pipeline?
