# DevOps2026
## ZADANIE 3 GITHUB

Cel laboratoriów.
Celem laboratoriów jest zapoznanie się z code review i podstawowymi plikami budującymi repo oraz przywracaniem commitów.


## WSTĘP TEORETYCZNY ##
[Mock funkcji](https://jestjs.io/docs/mock-functions#:~:text=Mock%20functions%20allow%20you%20to,time%20configuration%20of%20return%20values)

[TDD](https://geek.justjoin.it/czym-technika-tdd-wyglada-cykl-zycia/)

[Git hooks](https://git-scm.com/book/en/v2/Customizing-Git-Git-Hooks)

#### PROGRAM ZACZYNA SIĘ OD PROJEKTU, A NIE OD IMPLEMENTACJI ####

Katalogi naszego rozwiązania mogą projektować określone struktury/funkcjonalności/domeny naszego finalnego produktu.
GIT NIE CZYTA pustych katalogów, dlatego konieczne jest wykorzystanie pliku .gitkeep (w standardzie oznacza pusty plik, który ma na celu utrzymać katalog w repo).


#### REPO TO NIE ŚMIETNIK ####
Repozytorium kodu nie powinno służyć do trzymania wielkich plików buildów, plików z danymi itp. Repo musi ograniczyć się do rzeczy niezbędnych, tj. plików do uruchomienia kodu jak i jego zrozumienia.
Podczas tworzenia kodu może się okazać, że jest sporo plików utworzonych przez przypadek. Aby `git add *` ich nie obejmował, powstał plik .gitignore — wszelkie nazwy plików w nim umieszczone nie będą uwzględnione podczas tworzenia commita.


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

### 2 Stworzyć nowe branche
- 2.1 Stworzenie brancha z pierwszą wersją rozwiązania problemu

```bash
git switch -c lab_3/new_branch_nrIndeksu
git push
```

### 3 Edytowanie brancha
- 3.1 Dodać folder model_nrIndeksu do katalogu Lab_3 i dodać plik nr_indeksu.csv
- 3.2 Wykonać commita i wypchnąć go na zdalne repo
```bash
git checkout lab_3/new_branch_nrIndeksu
git add *
git commit -m "dodano plik csv do nowego folderu z modelem"
git push
```

### 4 Code review
- 4.1 Dla tego commita należy wykonać pull request do branchu TEST (nie przejmować się, jeżeli testy nie przejdą)
- 4.2 Uruchomić tryb REVIEW i do wybranej linijki kodu app.py w sekcji importów dodać komentarz o braku importu dla nowo powstałego folderu
- 4.3 Dla całego pliku nr_indeksu.csv dodać komentarz, że plik taki nie może znajdować się w repozytorium i należy umieścić go w .gitignore
- 4.4 Zamknąć review i odesłać podsumowanie do pull requesta z prośbą o zmianę kodu (NIE AKCEPTOWAĆ)

### 5 Poprawka kodu
- 5.1 W tym samym branchu wykonać usunięcie pliku csv
```bash
git rm nr_indeksu.csv
```
- 5.2 Dodać do pliku .gitignore linijkę `*.csv`
- 5.3 Dodać do folderu z modelem plik nowy_nr_indeksu.csv
- 5.4 Dodać pusty plik .gitkeep
- Stworzyć commita za pomocą `git add *` i wysłać na zdalne repo

### 6 Naprawa repo ###
Często może się zdarzyć, że wrzucimy commita, który chcemy cofnąć.

- 6.1 Dodać nowy plik np. "test_plik.txt" i uzupełnić go przykładowym tekstem, a następnie dodać do commita i wypchnąć zmiany na repo
- 6.2 Zweryfikować, czy plik jest widoczny na pull requeście
- 6.3 Zedytować plik i wypchnąć zmiany na zdalny serwer
- 6.4 Cofnąć zmiany do commita z kroku 6.1 za pomocą komendy

```bash
git revert hash_commita
```

- 6.5 Rozwiązać konflikty, wypchnąć zmiany i zweryfikować, czy zmiany zostały odwrócone


### 7 Pre-commit hooks

Laboratorium nawiązuje do tematu Git hooks omówionego we wstępie teoretycznym.
Narzędzie `pre-commit` automatycznie uruchamia hooki przed każdym commitem — mogą one sprawdzać i **naprawiać** kod zanim trafi do repozytorium.

#### 7.1 Zainstalować narzędzie pre-commit

```bash
pip install pre-commit
pre-commit --version
```

#### 7.2 Skopiować folder `env_0000` do `env_nrIndeksu`

```bash
cp -r Lab_3/env_0000 Lab_3/env_123456
```

#### 7.3 Zainstalować hooki w lokalnym repozytorium

Z poziomu głównego katalogu repozytorium:

```bash
pre-commit install
```

Po tej komendzie w `.git/hooks/pre-commit` pojawi się skrypt uruchamiany automatycznie przy każdym `git commit`.

#### 7.4 Spróbować zacommitować celowo zepsuty plik

W folderze `env_nrIndeksu/` znajduje się plik `bad_code.py` z celowymi błędami formatowania (niezgodnymi z PEP 8): brak spacji przy operatorach, zła kolejność importów, zbyt długie linie.

```bash
git add Lab_3/env_nrIndeksu/bad_code.py
git commit -m "dodano bad_code.py - przed naprawą"
```

**Obserwacja:** Commit nie przejdzie. Hooki `black` i `isort` automatycznie zmodyfikują plik. Zobaczysz komunikat:

```
black....................................................................Failed
- hook id: black
- files were modified by this hook

isort....................................................................Failed
- hook id: isort
- files were modified by this hook
```

#### 7.5 Sprawdzić zmiany wprowadzone przez hooki

```bash
git diff Lab_3/env_nrIndeksu/bad_code.py
```

Zwróć uwagę co dokładnie zostało zmienione (wklej diff do sprawozdania).

#### 7.6 Dodać naprawiony plik i wykonać commit ponownie

```bash
git add Lab_3/env_nrIndeksu/bad_code.py
git commit -m "dodano bad_code.py - po naprawie przez pre-commit"
```

Tym razem commit przejdzie pomyślnie — hooki nie znajdą już nic do naprawy.

---

### 8 Sprawozdanie

- 8.1 Sprawozdanie ma być dokumentacją pracy, tj. opisem wykonanych kroków wraz ze zdjęciami i opisem wykorzystywanych metod. Ma ono pozwolić na odtworzenie zadania z wykorzystaniem instrukcji ze sprawozdania.
- 8.2 Ma być ono zapisane za pomocą Markdown w nowo stworzonym folderze.
- 8.3 W sprawozdaniu opisać zadanie 7: co zrobiły hooki, wkleić diff z kroku 7.5, wyjaśnić dlaczego drugi commit przeszedł.


### Zaliczenie laboratoriów
- Sprawozdanie w docelowej lokalizacji
- Gotowe do oddania praca i sprawozdanie w postaci pull requesta (można dodać commita do brancha z już utworzonym pull requestem, aby dodać sprawozdanie)
- Wszelkie edycje skryptów testowych i automatyzujących workflow są zabronione (czyli plików niewymienionych w instrukcji)
- Pushe mają być wykonywane WYŁĄCZNIE Z NASZYCH KONT GITHUB

### Tematy do rozwinięcia w sprawozdaniu w celu podniesienia oceny

Ocena jest podwyższona o ile wcześniejsze kroki instrukcji zostały wykonane. Nie ma możliwości zaliczenia laboratoriów samym tematem dodatkowym.

Tematy te proszę zamieścić w osobnym rozdziale:

- czym różnią się git hooksy client-side od server-side, jakie to są i kiedy się je wykorzystuje
- czym różni się git reset od git revert
- jaką rolę pełnią mocki w TDD
