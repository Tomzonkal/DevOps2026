# dev_ops_lato_2026
## ZADANIE 1 GITHUB

Cel laboratoriów.
Celem laboratoriów jest zapoznanie się z mergami, konfliktami i dwoma sposobami ich rozwiązywania.



Przydatne linki:
- [Git cheatsheet](https://education.github.com/git-cheat-sheet-education.pdf)

Działanie poszczególnych komend

![Jak działają komendy](https://miro.medium.com/v2/resize:fit:720/format:webp/1*gZX2Cs-To3k1h63hHhPPcw.png)

Aby zaliczyć laboratoria należy wykonać następujące kroki 
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
git switch -c lab_2/new_branch_nrIndeksu_v1
git push
```

- 2.2 Stworzenie brancha z drugą wersją rozwiązania problemu 

```bash
git switch -c lab_2/new_branch_nrIndeksu_v2
git push
```

- 2.3 Stworzenie brancha z trzecią wersją rozwiązania problemu

```bash
git switch -c lab_2/new_branch_nrIndeksu_v3
git push
```
### 3 Edytowanie poszczególnych branchy 
- 3.1 Skopiować folder model_0000 do tego samego katalogu Lab_2 i podmienić nazwe na model_nrIndeksu np. model_123456
- 3.2 Sprawić aby dla każdej wersji plik **model.py** posiadał tylko jedną funkcję dla przypisanej jej wersji.
**ISTOTNE JEST ABY LINIJKI W KODZIE SIĘ POKRYWAŁY – ODSTĘPY MUSZĄ BYĆ USUNIĘTE -> wywołanie konfliktu**
    - Zedytować plik **model.py**
    - dodać funkcję w pliku app.py i nr indeksu do configa tak jak w lab_1
    - dodać commit i wypushować zmianę dla wersji

```bash
git checkout lab_2/new_branch_nrIndeksu_v1
git add *
git commit -m "zrobiono wersje 1"
git push 
```
- 3.3 powtórzyć krok 3.2 dla wersji 2 i 3   


### 4 Mergowanie kodu z poziomu prostego brancha 
- 4.1 Wykonać merga request z wersji 2 do wersji 1

```bash
git switch lab_2/new_branch_nrIndeksu_v1
git merge lab_2/new_branch_nrIndeksu_v2
```
- 4.2 Rozwiązać konflikty w lokalnym środowisku tak aby docelowo dwie wersje pojawiły się w wersji 1. W pliku **app.py** wykonywanie predykcji powinno być wykonywane dwa razy

### 5 Mergowanie kodu z wykorzystaniem brancha pomocniczego
Dla skomplikowanych merge'ów niezbędne może się okazać zrobienie tego w oddzielnym branchu gdzie powoli kod będzie mergowany i testowany i dopiero potem może być on finalnie spięty z docelowym branchem

- 5.1 Utworzenie brancha do mergowania z wersji 1 po mergu

```bash
git checkout lab_2/new_branch_nrIndeksu_v1
git switch -c lab_2/new_branch_nrIndeksu_merge_3_to_1
git push
```
- 5.2 Dla brancha do mergowania wykonać połączenie z branchem v3
```bash
git checkout lab_2/new_branch_nrIndeksu_merge_3_to_1
git merge lab_2/new_branch_nrIndeksu_v3
```
- 5.3 Rozwiązać konflikty tak by finalnie pojawiły się 3 wersje, to samo w pliku  **app.py**

- 5.4 spushowac zmiany na zdalne repo 
```bash
git add *
git commit -m "zmergowano 3 z 1"
git push 
```


- 5.5 Zmergować zmiany z brancha pomocniczego do brancha v1 
```bash
git checkout  lab_2/new_branch_nrIndeksu_v1
git merge  lab_2/new_branch_nrIndeksu_merge_3_to_1
git push 
```

### 6 Wykonać pull requesta do branchy TEST
6.1 Wykonać pull request tak jak w LAB_1 jeżeli testy przejdą oznacza, że kod działą prawidłowo 


### 7 Sprawozdanie 

- 7.1 Sprawozdanie ma być dokumentacją pracy tj opisem wykonanych kroków wraz z zdjęciami i opisem wykorzystywanych metod. Ma ona pozwolić na odtworzenie zadania z wykorzystaniem instrukcji ze sprawozdania
- 7.2 Ma być ono zapisane za pomocą markdowna w skopiowanym folderze.


### Zaliczenie laboratoriów 
- Sprawozdanie w docelowej lokalizacji 
- Gotowe do oddania praca i sprawozdanie w postaci pull requesta (można dodać commita do brancha z już utworzonym pull requestem aby dodać sprawozdanie)
- Wszelkie edycje skryptów testowych i automatyzujących workflow jest zabronione (czyli plików nie wymienionych w instrukcji)
- Pushe mają być wykonywane WYŁĄCZNIE Z NASZYCH KONT GITHUB 

### Tematy do rozwinięcia w sprawozdaniu w celu podniesienia oceny z sprawozdania 

Ocena jest podwyższona o ile wcześniejsze kroki instrukcji zostały wykonane, nie ma możliwości zaliczenia laboratoriów samym tematem dodatkowym.

Tematy te proszę zamieścić w osobnym rozdziale

- dlaczego mergowanie z branchem pomocniczym nie wywołuje konfliktów 
- ile jest rodzaji mergy w gitcie
- jak zarządzać projektem aby uniknąć zbędnych konfliktów
- stworzyć diagram prezentujący operacje wykonywane w trakcie zajęć (jak są łączone/tworzone poszczególne branche)
