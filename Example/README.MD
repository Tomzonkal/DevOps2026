# Sprawozdanie – Lab 1

> **Autor:** 123456  
> **Data:** 2026-03-16  
> **Repozytorium:** git@github.com:Tomzonkal/DevOps2026.git

---

## Ocena 3 – Weryfikacja działania

Poniżej screenshoty potwierdzające że zadanie zostało wykonane poprawnie.

### Screenshot 1 – Aktywna gałąź robocza

![Gałąź robocza lab_1/new_branch_123456 widoczna w terminalu po komendzie git branch](screenshots/screen_1.png)

Widać gwiazdkę przy `lab_1/new_branch_123456` – znaczy że jesteśmy na właściwej gałęzi.

### Screenshot 2 – Kod widoczny na GitHubie

![Widok repozytorium na GitHub z wybraną gałęzią lab_1/new_branch_123456 i folderem model_123456](screenshots/screen_2.png)

Po przełączeniu na gałąź `lab_1/new_branch_123456` widać folder `model_123456` oraz zmienione pliki `app.py` i `config.py`.

### Screenshot 3 – Testy w pull requeście przeszły

![Pull request z zielonym statusem wszystkich testów GitHub Actions](screenshots/screen_3.png)

Wszystkie testy GitHub Actions są zielone, co potwierdza że endpoint `/api/model_123456` działa poprawnie.

---

## Ocena 4 – Opis komend i efektów

Poniżej opisałem każdą komendę której użyłem podczas laboratorium, w kolejności w jakiej je wykonywałem.

---

### Krok 1 – Generowanie klucza SSH
```bash
ssh-keygen -t ed25519 -C "twoj_email@example.com"
```

Generuje parę kluczy algorytmem Ed25519. W `~/.ssh/` pojawiają się `id_ed25519` (prywatny) i `id_ed25519.pub` (publiczny, wgrywamy na GitHuba).

---

### Krok 2 – Klonowanie repozytorium
```bash
git clone git@github.com:Tomzonkal/DevOps2026.git
```

Pobiera repozytorium na dysk lokalny. Powstaje katalog `DevOps2026/` z plikami projektu i folderem `.git/`.

---

### Krok 3 – Stworzenie gałęzi roboczej
```bash
git switch -c lab_1/new_branch_123456
```

Tworzy nową gałąź i od razu na nią przechodzi. Kolejne commity trafiają tutaj, nie ruszamy `main`.

---

### Krok 4 – Weryfikacja aktywnej gałęzi
```bash
git branch
```

Listuje lokalne gałęzie. Gwiazdka (`*`) przy nazwie = jesteśmy we właściwym miejscu.

---

### Krok 5 – Edycja `config.py`
```python
id_list = [
    "0000",
    "123456"
]
```

Dodanie `"123456"` do listy sprawia że pytest automatycznie przetestuje nasz endpoint. Bez tego wpisu test się w ogóle nie odpali.

---

### Krok 6 – Edycja `model_123456/model.py`
```python
# Przed:
def run_model_0000(input):
# Po:
def run_model_123456(input):
```

Zmiana nazwy funkcji na unikalną. Import w `app.py` nie będzie kolidował z funkcjami innych studentów.

---

### Krok 7 – Edycja `app.py`
```python
from model_123456 import model as model_123456

@app.route('/api/model_123456', methods=['POST'])
def model_123456_input():
    data = request.get_json()
    input = data["input"]
    result = model_123456.run_model_123456(input=input)
    return jsonify({'result': result}), 200
```

Rejestruje nowy endpoint POST w Flasku – odbiera JSON, przekazuje do modelu, zwraca predykcję.

---

### Krok 8 – Staging zmian
```bash
git add *
```

Dodaje zmienione pliki do strefy staging przed commitem. Uwaga: `git add *` pomija pliki z kropką na początku, np. `.env` – wtedy lepiej `git add -A`.

---

### Krok 9 – Konfiguracja tożsamości Gita
```bash
git config --global user.email "twoj_email@example.com"
git config --global user.name "TwojaNazwa"
```

Ustawia dane autora commitów globalnie. Robi się to raz na danym komputerze.

---

### Krok 10 – Tworzenie commita
```bash
git commit -m "dodano model dla użytkownika 123456"
```

Zapisuje snapshot ze staging do lokalnej historii. Zmiany są lokalnie – jeszcze nie na serwerze.

---

### Krok 11 – Push
```bash
git push --set-upstream origin lab_1/new_branch_123456
```

Wysyła gałąź na GitHuba i ustawia tracking branch. Kolejne `git push` nie będą wymagać podawania nazwy.

---

### Krok 12 – Pull request do gałęzi TEST

Przez interfejs GitHuba: **base:** `TEST`, **compare:** `lab_1/new_branch_123456`. GitHub Actions odpala pytest automatycznie po utworzeniu PR.

---

## Ocena 5 – Dokumentacja techniczna

---

### Overview

Laboratorium 1 z DevOpsa polegało na przejściu przez podstawowy workflow Gita i GitHuba. Głównym zadaniem było sklonowanie istniejącego repozytorium, stworzenie własnej gałęzi roboczej, rozszerzenie aplikacji Flask o nowy endpoint serwujący predykcje modelu ML, a na koniec wypchnięcie zmian i weryfikacja przez zautomatyzowany pipeline CI.

Po tym laboratorium powinniśmy:
- umieć samodzielnie zarządzać gałęziami w Gicie,
- rozumieć jak rozszerzać aplikację Flask o nowe endpointy REST,
- wiedzieć czym jest pull request i do czego służy code review,
- rozumieć jak testy automatyczne weryfikują kod w pipeline CI.

---

### Prerequisites

| Wymaganie | Minimalna wersja | Jak sprawdzić |
|-----------|-----------------|---------------|
| Git | 2.35+ | `git --version` |
| Python | 3.9+ | `python --version` |
| pip | 23+ | `pip --version` |
| Konto GitHub | – | dostęp do repo kursu |
| Klucz SSH w GitHubie | – | [docs.github.com](https://docs.github.com/en/authentication/connecting-to-github-with-ssh) |

Biblioteki Python (plik `requirements`):
```
flask
scikit-learn
pytest
requests
```

---

### Step-by-step guide

#### Krok 1 – Konfiguracja klucza SSH
```bash
ssh-keygen -t ed25519 -C "twoj_email@student.agh.edu.pl"
cat ~/.ssh/id_ed25519.pub
```

Kopiujemy wyświetlony klucz publiczny i dodajemy go w GitHubie: **Settings → SSH and GPG keys → New SSH key**.

Klucz SSH zastępuje hasło przy każdej operacji `push`/`pull` – bez niego każde połączenie z repozytorium wymagałoby ręcznego logowania. Ed25519 jest aktualnie zalecanym algorytmem – jest bezpieczniejszy i szybszy od starszego RSA.

> **Uwaga:** Jeśli klucz już istnieje (`~/.ssh/id_ed25519`), nie trzeba generować nowego – wystarczy wgrać istniejący klucz publiczny. Generowanie nowego nadpiszę stary i zerwie połączenie ze wszystkimi serwisami które go używają.

**Weryfikacja:** `ssh -T git@github.com` powinno zwrócić `Hi <username>! You've successfully authenticated`.

---

#### Krok 2 – Klonowanie repozytorium
```bash
git clone git@github.com:Tomzonkal/DevOps2026.git
cd DevOps2026
```

`git clone` pobiera całą historię projektu razem z wszystkimi gałęziami i commitami, nie tylko aktualny stan plików. Katalog `Lab_1/` zawiera bazową aplikację Flask z przykładowym modelem `model_0000`, który służy jako szablon do skopiowania.

> **Uwaga:** Błąd `Permission denied (publickey)` oznacza że klucz SSH nie jest poprawnie skonfigurowany albo nie jest załadowany do agenta SSH (`ssh-add ~/.ssh/id_ed25519`). Wróć do Kroku 1.

**Oczekiwany wynik:**
```
Cloning into 'DevOps2026'...
remote: Enumerating objects: ...
```

---

#### Krok 3 – Stworzenie gałęzi roboczej
```bash
cd Lab_1
git switch -c lab_1/new_branch_123456
git push --set-upstream origin lab_1/new_branch_123456
```

Gałąź izoluje nasze zmiany od kodu innych studentów i od gałęzi `main`. Dzięki temu można pracować równolegle bez ryzyka nadpisania cudzych zmian. Prefix `lab_1/` to konwencja nazewnicza – GitHub grupuje gałęzie z tym samym prefixem w widoku listy, co ułatwia nawigację gdy jest ich dużo.

Natychmiastowy push gałęzi na serwer (`--set-upstream`) to dobra praktyka – nawet zanim dodamy jakikolwiek commit, gałąź jest już widoczna na GitHubie i można do niej wrócić z innego komputera.

> **Uwaga:** `123456` to numer indeksu – używanie cudzego spowoduje konflikty przy merge i brak zaliczenia.

**Oczekiwany wynik:** `git branch` pokazuje `* lab_1/new_branch_123456`.

---

#### Krok 4 – Skopiowanie folderu modelu
```bash
cp -r model_0000 model_123456
```

Kopiujemy cały folder szablonu zamiast tworzyć pliki od zera. Nowy folder zawiera `model.py` z logiką predykcji i `model.pkl` – gotowy wytrenowany model scikit-learn w formacie pickle. Nie podmieniamy `model.pkl` – ma zwracać z góry określony wynik, który sprawdzają testy.

**Struktura po skopiowaniu:**
```
Lab_1/
├── model_0000/
│   ├── model.pkl
│   └── model.py
└── model_123456/
    ├── model.pkl
    └── model.py
```

---

#### Krok 5 – Edycja `model_123456/model.py`

Zmieniamy nazwę funkcji z `run_model_0000` na `run_model_123456`:
```python
import pickle
import os

def run_model_123456(input):
    path = os.path.dirname(__file__)
    with open(path + "/model.pkl", "rb") as f:
        model = pickle.load(f)
    result = model.predict(input)
    result = float(result[0])
    return result
```

Funkcja ładuje model z `.pkl` za pomocą `pickle`, wywołuje metodę `predict()` scikit-learn i konwertuje wynik do `float` (bo `predict()` zwraca tablicę numpy – samo `result[0]` to nadal obiekt numpy, nie czysty Python float, co mogłoby powodować problemy przy serializacji do JSON).

`os.path.dirname(__file__)` to ścieżka do katalogu w którym leży `model.py`. Bez tego otwieranie `model.pkl` przez relatywną ścieżkę działałoby tylko wtedy gdy uruchamiamy skrypt z konkretnego katalogu – z innego miejsca dostalibyśmy `FileNotFoundError`.

---

#### Krok 6 – Edycja `config.py`
```python
id_list = [
    "0000",
    "123456"   # ← dodajemy swój numer indeksu
]
```

Lista `id_list` jest odczytywana przez `api_test.py`. Pytest używa `@pytest.mark.parametrize` żeby automatycznie wygenerować osobny test dla każdego ID z listy – nie musimy ręcznie pisać testów dla każdego studenta. Mechanizm jest prosty: brak wpisu = brak testu = brak zaliczenia, nawet jeśli endpoint działa poprawnie.

---

#### Krok 7 – Edycja `app.py`

Dodajemy import na górze pliku (za istniejącymi importami):
```python
from model_123456 import model as model_123456
```

I nowy endpoint pod istniejącą funkcją `model_00000_input`:
```python
@app.route('/api/model_123456', methods=['POST'])
def model_123456_input():
    data = request.get_json()
    input = data["input"]
    result = model_123456.run_model_123456(input=input)
    return jsonify({'result': result}), 200
```

Dekorator `@app.route` rejestruje funkcję jako handler HTTP dla konkretnej ścieżki. Flask mapuje przychodzące requesty na odpowiednie funkcje na podstawie URL i metody HTTP. `request.get_json()` parsuje body requestu – jeśli klient nie wyśle nagłówka `Content-Type: application/json`, metoda zwróci `None` i dostaniemy błąd przy próbie dostępu do `data["input"]`.

> **Uwaga:** Python jest wrażliwy na mieszanie spacji i tabulatorów – trzymamy się tego samego stylu co reszta pliku.

---

#### Krok 8 – Commit i push
```bash
git add config.py app.py model_123456/model.py
git commit -m "dodano model dla użytkownika 123456"
git push
```

`git add` z konkretnymi nazwami plików (zamiast `*`) daje pewność że commitujemy tylko to co chcemy. `git commit` tworzy snapshot lokalnie – dopiero `git push` wysyła zmiany na serwer. Ta dwuetapowość to cecha Gita jako systemu rozprószonego: można pracować i commitować offline, a zsynchronizować się z serwerem później.

---

#### Krok 9 – Weryfikacja na GitHubie i pull request

1. Wchodzimy na stronę repo na GitHubie.
2. Przełączamy selektor gałęzi na `lab_1/new_branch_123456` i sprawdzamy czy nasze pliki są widoczne.
3. Zakładka **Pull requests → New pull request**.
4. Ustawiamy: **base:** `TEST`, **compare:** `lab_1/new_branch_123456`.
5. Klikamy **Create pull request**.

Pull request to nie tylko mechanizm do mergowania kodu – to też przestrzeń do code review. W środowisku zespołowym ktoś inny przegląda zmiany zanim trafią do głównej gałęzi. Tutaj rolę reviewera pełni GitHub Actions, który automatycznie odpala testy i raportuje wynik bezpośrednio w PR.

---

### Expected output

#### Odpowiedź endpointu (test manualny)
```bash
curl -X POST http://localhost:5000/api/model_123456 \
     -H "Content-Type: application/json" \
     -d '{"input": [[1, 2, 3, 4]]}'
```
```json
{"result": 2.0}
```

#### Wynik testów pytest
```
collected 2 items

api_test.py::test_api_models[0000] PASSED
api_test.py::test_api_models[123456] PASSED

====== 2 passed in 0.42s ======
```

#### Status GitHub Actions w pull requeście

Wszystkie czeki powinny mieć status **✓**. Jeśli coś nie przechodzi – klikamy **Details** żeby zobaczyć logi i sprawdzić na którym kroku pipeline się wyłożył.

---


### Podsumowanie

W tym laboratorium przeszliśmy przez kompletny cykl pracy z repozytorium Git w środowisku GitHub:

1. **Skonfigurowanie SSH** – żeby nie wpisywać hasła przy każdym pushu.
2. **Sklonowanie repo i stworzenie gałęzi** – dzięki temu każdy student pracuje na swoim kodzie bez nadpisywania cudzych zmian.
3. **Rozszerzenie aplikacji Flask** – dodanie nowego endpointu z modelem ML pokazuje jak w praktyce integruje się kod w zespole.
4. **Commit i push** – ważne żeby rozumieć różnicę między lokalnym zapisem a wysłaniem na serwer.
5. **Pull request i CI** – automatyczne testy przez pytest i GitHub Actions to podstawa współczesnego developmentu.

Całość dobrze ilustruje **GitHub Flow**: krótka gałąź → commit → push → pull request → testy → merge.