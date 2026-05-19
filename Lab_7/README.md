# DevOps2026
## ZADANIE 7 GITHUB ACTIONS

Cel laboratoriów.
Celem laboratoriów jest zapoznanie się z GitHub Actions — automatycznym systemem CI/CD wbudowanym w GitHub. Studenci otrzymują działającą aplikację Python oraz celowo błędny workflow. Ich zadaniem jest zrozumienie kodu aplikacji, napisanie testów z pomocą AI oraz naprawienie workflow tak, żeby uruchamiał się wyłącznie na ich feature branchu.


## WSTĘP TEORETYCZNY ##

[GitHub Actions — oficjalna dokumentacja](https://docs.github.com/en/actions)

[Wyzwalacze workflow (`on:`) — dokumentacja](https://docs.github.com/en/actions/writing-workflows/choosing-when-your-workflow-runs/events-that-trigger-workflows)

[Filtrowanie branchy w GitHub Actions](https://docs.github.com/en/actions/writing-workflows/choosing-when-your-workflow-runs/events-that-trigger-workflows#push)

[pytest — dokumentacja](https://docs.pytest.org/)

#### CZYM JEST GITHUB ACTIONS ####

GitHub Actions to platforma CI/CD zintegrowana bezpośrednio z GitHub. Pozwala automatycznie uruchamiać zadania (testy, buildy, deploymenty) w odpowiedzi na zdarzenia w repozytorium, takie jak `push` czy `pull_request`.

Workflow definiujemy w pliku YAML wewnątrz katalogu `.github/workflows/`. Najważniejsze sekcje:

- `on:` — określa kiedy workflow ma się uruchomić (na jakie zdarzenia i na jakich branchach)
- `jobs:` — lista zadań do wykonania (każde w osobnym środowisku)
- `steps:` — kolejne kroki wewnątrz jednego joba

#### DLACZEGO FILTROWANIE BRANCHY MA ZNACZENIE ####

W zespole programistycznym każdy developer pracuje na swojej gałęzi. Workflow uruchamiany na każdym pushu do `main` działa tylko dla kodu, który przeszedł code review i został scalony. Workflow uruchamiany na feature branchu daje programiście natychmiastowy feedback na temat jego własnych zmian — **zanim** trafi on do głównej gałęzi.

Konfigurowanie workflow tak, żeby uruchamiał się wyłącznie na wybranych branchach, to podstawowa umiejętność w CI/CD:
- izoluje feedback do pracy konkretnego developera
- nie zaśmieca historii workflow niepowiązanymi buildami
- umożliwia różne polityki testowania dla różnych typów branchy (feature, release, hotfix)

#### AI JAKO NARZĘDZIE DO PISANIA TESTÓW ####

W tym laboratorium świadomie korzystamy z modeli językowych (LLM, np. Claude) do generowania testów. Jest to akceptowana praktyka w nowoczesnym DevOpsie. Zadanie polega na:
1. Wklejeniu kodu `calculator.py` do LLM z prośbą o napisanie testów
2. Przeanalizowaniu wygenerowanych testów i zrozumieniu każdego przypadku testowego
3. Uruchomieniu testów lokalnie i poprawienie ich, jeśli nie działają
4. Zrozumieniu *dlaczego* testy testują konkretne zachowania — to jest najważniejszy element oceny


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
git switch -c lab_7/new_branch_nrIndeksu
git push -u origin lab_7/new_branch_nrIndeksu
```

### 3 Przygotowanie środowiska pracy

- 3.1 Skopiować folder `app_0000` do `app_nrIndeksu`

```bash
cp -r Lab_7/app_0000 Lab_7/app_123456
```

Cała dalsza praca odbywa się wewnątrz folderu `app_nrIndeksu`. Nie modyfikuj `app_0000`.

- 3.2 Skopiować plik workflow do katalogu `.github/workflows/` i nadać mu unikalną nazwę

```bash
cp Lab_7/app_123456/ci.yml .github/workflows/lab_7_123456.yml
```

Nazwij plik `lab_7_nrIndeksu.yml` — unikalny sufiks zapobiega konfliktom z workflow innych studentów.

**Uwaga:** po skopiowaniu plik wymaga edycji — jest celowo błędny i zawiera placeholder `app_nrIndeksu` w ścieżce. Edycję wykonasz w kroku 6.

### 4 Zapoznanie się z kodem aplikacji

- 4.1 Przeczytać plik `calculator.py` w swoim folderze

Aplikacja udostępnia REST API kalkulatora z czterema operacjami matematycznymi. Każdy endpoint przyjmuje JSON z polami `a` i `b` i zwraca wynik w polu `result`.

- 4.2 Uruchomić aplikację lokalnie i sprawdzić czy działa

```bash
cd Lab_7/app_123456
pip install -r requirements.txt
python calculator.py
```

W osobnym terminalu przetestuj wszystkie endpointy:

```bash
curl -X POST http://localhost:5000/add \
  -H "Content-Type: application/json" \
  -d '{"a": 10, "b": 5}'
```
Oczekiwana odpowiedź: `{"result": 15}`

```bash
curl -X POST http://localhost:5000/subtract \
  -H "Content-Type: application/json" \
  -d '{"a": 10, "b": 3}'
```
Oczekiwana odpowiedź: `{"result": 7}`

```bash
curl -X POST http://localhost:5000/multiply \
  -H "Content-Type: application/json" \
  -d '{"a": 4, "b": 5}'
```
Oczekiwana odpowiedź: `{"result": 20}`

```bash
curl -X POST http://localhost:5000/divide \
  -H "Content-Type: application/json" \
  -d '{"a": 10, "b": 0}'
```
Oczekiwana odpowiedź: HTTP 400 z komunikatem o błędzie.

```bash
curl http://localhost:5000/health
```
Oczekiwana odpowiedź: `{"status": "ok"}`

- 4.3 Przerwać działanie aplikacji (`Ctrl+C`)

### 5 Napisanie testów z pomocą AI

- 5.1 Wkleić zawartość pliku `calculator.py` do LLM (np. Claude) z następującą prośbą:

> *"Napisz testy pytest dla tej aplikacji Flask. Testy powinny używać biblioteki `requests` do wykonywania żądań HTTP do działającego serwera. Pokryj wszystkie endpointy (/add, /subtract, /multiply, /divide), przypadki brzegowe (dzielenie przez zero, liczby ujemne, liczby zmiennoprzecinkowe) oraz przypadki błędów (brakujące pola w JSON)."*

- 5.2 Zapisać wygenerowany kod jako `test_calculator.py` w folderze `app_nrIndeksu/`

- 5.3 Uruchomić testy lokalnie — najpierw uruchomić aplikację w tle, następnie testy:

```bash
cd Lab_7/app_123456
python calculator.py &
python -m pytest test_calculator.py -v
```

- 5.4 Jeżeli testy nie przechodzą — poprawić je. Może być konieczna kilkukrotna iteracja z AI. Udokumentować każdą iterację w sprawozdaniu.

- 5.5 Zatrzymać aplikację uruchomioną w tle:

```bash
kill %1
```

### 6 Analiza i naprawa workflow

- 6.1 Otworzyć plik `.github/workflows/lab_7_nrIndeksu.yml` i przeanalizować jego zawartość.

- 6.2 Spróbować wypchnąć commit na swój branch i obserwować zakładkę **Actions** na GitHub:

```bash
git add .
git commit -m "lab_7: dodano test_calculator.py"
git push
```

Czy workflow uruchomił się? Dlaczego (lub dlaczego nie)?

- 6.3 Zidentyfikować oba błędy konfiguracyjne w workflow i naprawić je. Wskazówki znajdziesz w sekcji **Wskazówki** poniżej.

- 6.4 Po naprawie wypchnąć zmiany i zweryfikować, że workflow uruchomił się poprawnie — zielony checkmark na branchu.

```bash
git add .github/workflows/lab_7_nrIndeksu.yml
git commit -m "lab_7: naprawiono workflow"
git push
```

### 7 Weryfikacja działania workflow

- 7.1 Na GitHub, w zakładce **Actions**, znaleźć uruchomienie workflow dla swojego brancha. Zrzut ekranu zielonego workflow zachować do sprawozdania.

- 7.2 Stworzyć Pull Request z brancha `lab_7/new_branch_nrIndeksu` do `main`.

- 7.3 Zweryfikować, że Twój workflow (`lab_7_nrIndeksu.yml`) **NIE uruchomił się** dla tego Pull Requesta.

  W zakładce **Actions** po otwarciu PR zobaczysz uruchomiony workflow `lab_7_github_actions` — to jest workflow oceniający (uruchamiany przez prowadzącego na każdy PR do `main`), **nie** Twój workflow. Sprawdź czy na liście uruchomień pojawia się Twój workflow `CI` — jeśli naprawiłeś błąd 1 poprawnie, nie powinien się uruchomić.

  Zrzut ekranu potwierdzający brak uruchomienia Twojego workflow `CI` na Pull Requeście zachować do sprawozdania.

### 8 Sprawozdanie

- 8.1 Sprawozdanie ma być dokumentacją pracy, tj. opisem wykonanych kroków wraz ze zrzutami ekranu i technicznym uzasadnieniem każdej zmiany. Ma ono pozwolić na odtworzenie zadania z wykorzystaniem instrukcji ze sprawozdania.

- 8.2 Sprawozdanie należy umieścić w **osobnym repozytorium**: [https://github.com/Tomzonkal/Devops_2026_sprawka](https://github.com/Tomzonkal/Devops_2026_sprawka)

  Sklonuj repozytorium ze sprawozdaniami, stwórz folder `Lab_7/nrIndeksu/` i umieść tam plik Markdown ze sprawozdaniem:

  ```bash
  git clone https://github.com/Tomzonkal/Devops_2026_sprawka.git
  cd Devops_2026_sprawka
  mkdir -p Lab_7/123456
  # stwórz plik sprawozdania Lab_7/123456/sprawozdanie.md
  git add Lab_7/123456/
  git commit -m "lab_7: sprawozdanie 123456"
  git push
  ```

- 8.3 Sprawozdanie musi zawierać:
  - Opis każdego z 2 znalezionych błędów w workflow (przed/po naprawie — fragment kodu)
  - Wyjaśnienie, dlaczego dany błąd powodował nieprawidłowe działanie CI
  - Opis procesu pisania testów z AI (ile iteracji, co poprawiałeś i dlaczego)
  - Zrzut ekranu zielonego workflow na feature branchu
  - Zrzut ekranu potwierdzający brak uruchomienia workflow na Pull Requeście do `main`
  - Odpowiedź (3–5 zdań) na pytanie: **Dlaczego branch-specific triggering jest ważny w CI/CD?**

- 8.4 Upewnij się, że w repozytorium kursowym (DevOps2026) na swoim branchu znajdują się:
  - `Lab_7/app_123456/test_calculator.py`
  - `.github/workflows/lab_7_123456.yml` (naprawiony workflow)

  Jeśli nie wykonałeś jeszcze commita tych plików — zrób to teraz, a następnie utwórz Pull Request z brancha `lab_7/new_branch_123456` do `main` w repozytorium kursowym.

### Wskazówki

- Przeczytaj dokumentację GitHub Actions dotyczącą sekcji `on:` — szczególnie różnicę między zdarzeniami `push` i `pull_request` oraz tym, jak działa filtrowanie przez `branches:`
- Jeżeli testy przechodzą lokalnie, ale nie w CI — zastanów się, co różni Twoje środowisko lokalne od środowiska GitHub Actions (co jest zainstalowane lokalnie, a co musi zostać zainstalowane w CI)
- Flaga `-v` w pytest wyświetla szczegółowe nazwy testów — pomaga zrozumieć, które testy przechodzą, a które nie


### Zaliczenie laboratoriów
- Sprawozdanie w repozytorium [Devops_2026_sprawka](https://github.com/Tomzonkal/Devops_2026_sprawka) w folderze `Lab_7/nrIndeksu/`
- Kod (testy + naprawiony workflow) w postaci pull requesta do repozytorium kursowego (DevOps2026) — można dodać commita do brancha z już utworzonym pull requestem
- Wszelkie edycje skryptów testowych i automatyzujących workflow są zabronione (czyli plików niewymienionych w instrukcji)
- Pushe mają być wykonywane WYŁĄCZNIE Z NASZYCH KONT GITHUB

### Tematy do rozwinięcia w sprawozdaniu w celu podniesienia oceny

Ocena jest podwyższona o ile wcześniejsze kroki instrukcji zostały wykonane. Nie ma możliwości zaliczenia laboratoriów samym tematem dodatkowym.

Tematy te proszę zamieścić w osobnym rozdziale:

- Czym jest **matrix strategy** w GitHub Actions i w jakim scenariuszu warto ją stosować?
- Co to są **GitHub Actions Secrets** i jak bezpiecznie przekazywać tokeny/hasła do workflow?
- Jaka jest różnica między `runs-on: ubuntu-latest` a pinowaniem konkretnej wersji (np. `ubuntu-22.04`) — jakie ryzyko niesie `latest`?
