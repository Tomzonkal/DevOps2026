# Wstęp
Celem ćwiczenia było zapoznanie się z podstawami Dockera i Docker Compose poprzez diagnozę i naprawę celowo zepsutej aplikacji wieloserwisowej. Pomogło to w nauce analizowania logów kontenerów, zrozumieniu konfiguracji sieci, wolumenów i zależności między serwisami.

# Przebieg Ćwiczeń
Na początku standardowo aktualizujemy metadane, przełączamy gałąź na `main` i pobieramy zmiany w kodzie:

![git fetch --all](img/image_1.png)

![git checkout main i git pull](img/image_2.png)

Teraz tworzymy nową gałąź z rozwiązaniem laboratorium:

![git switch -c lab_4/new_branch_415942](img/image_3.png)

![git push --set-upstream origin](img/image_4.png)

Teraz utworzymy kopię `app_0000` z numerem naszego indeksu, na której będziemy następnie pracować:

![Kopiowanie folderu cp -r app_0000 app_415942](img/image_5.png)

Dodatkowo tworzymy jeszcze centralny punkt zarządzania konfiguracją, czyli plik `.env` na podstawie skopiowanego pliku `.env.example`:

![Kopiowanie pliku konfiguracyjnego .env](img/image_6.png)

Teraz, po uruchomieniu aplikacji „Docker Desktop” startujemy „Docker Compose” w folderze `app_415942`:

![docker compose up --build](img/image_7.png)

Zauważmy teraz błąd, który pojawia się podczas startowania. Jak można zobaczyć Docker Compose nie był w stanie połączyć się z bazą danych mimo 10 prób:

![Logi błędu z backend-1: Could not connect to database after 10 attempts](img/image_8.png)

W osobnym terminalu sprawdźmy w tym czasie stan serwerów:

![Wynik komendy docker compose ps](img/image_9.png)

Możemy z niego wyczytać, że środowisko jest:
* Aktywne i stabilne,
* Gotowe operacyjnie,
* Udostępnione,
* Architektonicznie niekompletne - brakuje warstwy logiki biznesowej (backend/API).

Zatrzymajmy teraz aplikację:

![Wynik komendy docker compose down](img/image_10.png)

Zdiagnozujmy teraz problemy za pomocą chatu LLM - np. Gemini Pro. Wklejmy do niego komunikaty błędów z logów oraz treść pliku `docker-compose.yml` i poprośmy o wskazanie błędów. Poniżej możemy zobaczyć fragment wypowiedzi chatu:

![Odpowiedź LLM - identyfikacja błędów z siecią i nazwą hosta](img/image_11.png)

Dalej Gemini zasugerował, aby zamienić część `db` oraz `backend` pliku `docker-compose.yml` ze starej wersji:

![Fragment błędnego kodu docker-compose.yml pokazany w LLM](img/image_12.png)

Na poniższą, poprawną wersję. Edytujemy zatem nasz plik `docker-compose.yml`:

![Poprawiony kod pliku docker-compose.yml w edytorze](img/image_13.png)

Teraz uruchommy Docker Compose ponownie i zobaczmy czy pozbyliśmy się błędu:

![Logi z budowania obrazów i startu kontenerów](img/image_14.png)

![Błąd initdb w logach bazy danych (kolidujący stary wolumen)](img/image_15.png)

Na razie nie widać żadnego błędu [w backendzie]. Następnie sprawdźmy odpowiedź backendu na endpoint `/health`:

![curl http://localhost:5000/health zwracający status ok](img/image_16.png)

Dostajemy pozytywną odpowiedź określającą status jako „ok". Kolejno zweryfikujmy dostępność frontendu:

![curl http://localhost:80 i otrzymany kod HTML strony](img/image_17.png)

Otrzymujemy oczekiwaną odpowiedź, jaką jest strona HTML aplikacji. Sprawdźmy jeszcze czy endpoint `/items` działa. Powinniśmy dostać pustą listę w nawiasach kwadratowych:

![curl http://localhost:5000/items zwracający puste []](img/image_18.png)

Ostatnim krokiem będzie weryfikacja persystencji danych. Dodajmy przykładowy element przez API:

![curl -X POST dodający element testowy](img/image_19.png)

I zobaczmy czy pojawi się on na liście `/items`:

![curl GET weryfikujący obecność nowego elementu na liście](img/image_20.png)

Jak możemy zobaczyć, element rzeczywiście pojawił się na liście. Teraz zobaczmy czy element przetrwa ponowne uruchomienie aplikacji:

![docker compose down zatrzymujący aplikację](img/image_21.png)

![docker compose up startujący ponownie aplikację](img/image_22.png)

![curl weryfikujący, że element przetrwał restart (persystencja)](img/image_23.png)

Widzimy, że element jest nadal na liście. Teraz usuńmy wolumen wyłączając Docker Compose z parametrem `-v` i zobaczmy czy po restarcie aplikacji lista `/items` się wyczyściła. Możemy zobaczyć, że wyczyszczenie zakończyło się sukcesem:

![docker compose down -v oraz końcowy curl pokazujący pustą listę](img/image_24.png)

# Podsumowanie

W tym laboratorium przeszliśmy przez proces wdrażania, diagnozowania i naprawy środowiska wielokontenerowego przy użyciu narzędzi Docker i Docker Compose:
* **Uruchamianie i weryfikacja środowiska** – wykorzystanie poleceń `docker compose up --build`, `down` oraz `ps` do kontrolowania cyklu życia aplikacji.
* **Analiza logów i diagnoza problemów** – odczytywanie komunikatów błędów bezpośrednio z logów kontenerów, co pozwoliło zidentyfikować brak komunikacji między API a bazą danych.
* **Konfiguracja izolacji sieciowej (Networks)** – rozwiązanie błędu polegającego na przypisaniu usług do odrębnych, niewidzących się sieci (`app_network` vs `db_network`).
* **Wewnętrzny system DNS Dockera** – naprawa adresacji URL bazy danych w zmiennych środowiskowych, poprzez zastąpienie błędnej nazwy hosta właściwą nazwą serwisu (`db`).
* **Zależności operacyjne (Depends_on & Healthcheck)** – wymuszenie odpowiedniej kolejności startowania kontenerów, gwarantując, że backend uruchomi się dopiero po osiągnięciu pełnej gotowości przez bazę danych.
* **Persystencja danych (Volumes)** – testowanie trwałości danych po zamknięciu kontenerów oraz świadome ich czyszczenie przy pomocy parametru `-v`.

Całość dobrze ilustruje specyfikę pracy z aplikacjami opartymi na mikrousługach: lokalizacja usterki w logach → naprawa konfiguracji deklaratywnej `.yml` → re-deploy → weryfikacja poprawności komunikacji i persystencji.