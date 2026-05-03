# Wstęp
Celem ćwiczenia było zapoznanie się z typowymi problemami bezpieczeństwa w konfiguracji Dockera i Docker Compose. Pomogło to w nauce identyfikacji i naprawy luki bezpieczeństwa w Dockerfile oraz pliku `docker-compose.yml`, rozumienia konsekwencji każdego z błędów oraz stosowania dobrych praktyk w budowaniu bezpiecznych obrazów kontenerów.

# Przebieg Ćwiczeń
Na początku standardowo aktualizujemy metadane, przełączamy gałąź na `main` i pobieramy zmiany w kodzie:

![git fetch --all](img/image_1.png)

![git checkout main i git pull](img/image_2.png)

Teraz tworzymy nową gałąź z rozwiązaniem laboratorium:

![git switch -c lab_5/new_branch_415942](img/image_3.png)

![git push --set-upstream origin lab_5/new_branch_415942](img/image_4.png)

Teraz utworzymy kopię `app_0000` z numerem naszego indeksu, na której będziemy następnie pracować:

![Kopiowanie folderu cp -r Lab_5/app_0000 Lab_5/app_415942](img/image_5.png)

Dodatkowo tworzymy jeszcze centralny punkt zarządzania konfiguracją, czyli plik `.env` na podstawie skopiowanego pliku `.env.example`:

![Kopiowanie pliku konfiguracyjnego .env](img/image_6.png)

Teraz, po uruchomieniu aplikacji „Docker Desktop" startujemy „Docker Compose" w folderze `app_415942`:

![docker compose up --build](img/image_7.png)

Przed rozpoczęciem pracy sprawdźmy jeszcze, czy aplikacja działa:

![curl http://localhost:5000/health (status ok)](img/image_8.png)

![curl http://localhost:5000/items (pusta lista)](img/image_9.png)

Widzimy, że status `/health` jest „ok", a lista `/items` pusta. Wszystko zatem jest w porządku. Przeprowadźmy teraz inspekcję warstw zbudowanego obrazu backendu za pomocą komendy:

`docker history lab5_app_123456_backend --no-trunc`

Wśród historii warstw możemy między innymi zaobserwować lukę bezpieczeństwa. Widać bezpośrednio dwie instrukcje ENV, które zapisują sztywno w obrazie poufne dane. Każdy, kto pobierze ten obraz, może uruchomić polecenie `docker history` i zobaczyć oba klucze:

![Odkryte klucze w wyniku docker history](img/image_10.png)

Możemy także zobaczyć, że obraz jest też bardzo obszerny w rozmiarze, co widać w poniższych fragmentach linijek:

![Duże rozmiary warstw w docker history (np. 694MB)](img/image_11.png)

Sprawdźmy teraz z jakim użytkownikiem działa proces w kontenerze:

![Sprawdzenie użytkownika - docker compose exec backend whoami (root)](img/image_12.png)

Teraz zamknijmy aplikację:

![Wyłączenie środowiska - docker compose down](img/image_13.png)

Wyślijmy teraz pliki `backend/Dockerfile`, `frontend/Dockerfile` oraz `docker-compose.yml` do chatu LLM, np. Gemini Pro, by zobaczyć jak zdiagnozuje on 4 poniższe błędy:
1. Niespięte wersje obrazów bazowych,
2. Hardkodowane sekrety w Dockerfile,
3. Hardkodowane hasło w docker-compose.yml,
4. Kontener uruchomiony jako root.

Zajmijmy się najpierw pierwszym problemem. Musimy zmienić wersję obrazu z frontendowego Dockerfile z najnowszej, na lżejszą i bezpieczniejszą wersję, np. `1.25-alpine`:

![Stary plik frontend/Dockerfile (FROM nginx:latest)](img/image_14.png)

![Poprawiony plik frontend/Dockerfile (FROM nginx:1.25-alpine)](img/image_15.png)

Kolejnym problemem są wcześniej wspomniane hardkodowane sekrety w backendowym Dockerfile. Należy je usunąć stąd i przenieść do `docker-compose.yml`.

Zmiana w backendowym Dockerfile:

![Poprawiony plik backend/Dockerfile - usunięte ENV z kluczami](img/image_16.png)

Zmiana w `docker-compose.yml`:

![Stara konfiguracja docker-compose.yml z hasłem w plain text](img/image_17.png)

![Przeniesione zmienne konfiguracyjne do sekcji environment](img/image_18.png)

Teraz te klucze oraz hasło, w tym także hasło wewnątrz adresu URL bazy danych, trzeba zamienić na odwołania do pliku `.env` w głównym folderze, gdzie zostaną przeniesione.

![Końcowa poprawiona sekcja backend w docker-compose.yml z referencjami do zmiennych](img/image_19.png)

Plik `.env`:

![Stworzony plik .env z hasłami i kluczami](img/image_20.png)

Dodajmy jeszcze wszystkie pliki z końcówką `.env` do pliku `.gitignore`, aby nie zostały one wysłane do publicznego repozytorium:

![Edycja .gitignore w dodająca *.env](img/image_21.png)

Ostatnim błędem jest uruchamianie kontenera jako root. Na końcu budowania obrazu musimy dodać "zwykłego" użytkownika z uprawnieniami jedynie do folderu z aplikacją i nakazać Dockerowi uruchamiać aplikację z właśnie tego konta. Musimy dodać poniższe linijki do backendowego Dockerfile:

![Dodanie użytkownika bez uprawnień root w backend/Dockerfile](img/image_22.png)

Uruchommy teraz Docker Compose i sprawdźmy czy działa poprawnie:

![docker compose up --build po wszystkich poprawkach bezpieczeństwa](img/image_23.png)

![Weryfikacja curl po naprawie](img/image_24.png)

Zobaczmy teraz czy problemy rzeczywiście zostały rozwiązane. Sprawdźmy najpierw wersję obrazu. Możemy zobaczyć, że wersja NGINX to rzeczywiście 1.25:

![docker inspect sprawdzający wersję NGINXa (1.25.5)](img/image_25.png)

Możemy od razu zobaczyć, że użytkownikiem na którym działa kontener już nie jest root:
```bash
$ docker compose exec backend whoami
appuser
```

Włączmy `docker history`. Widzimy, że klucze już się nie wyświetlają:

```bash
<missing>
ENV PYTHON_SHA256=c08bc65a81971c1dd5783182826503369466c7e67374d1646519adf052076684
<missing>
ENV PYTHON_VERSION=3.12.13
<missing>
ENV GPG_KEY=7169605F62C751356D054A26A821E680E5FA6305
<missing>
RUN /bin/sh -c set -eux; apt-get update; apt-get install -y-no-install-recommends
<missing>
ENV LANG C.UTF-8
<missing>
ENV PATH=/usr/local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
```

Zweryfikujmy jeszcze na końcu persystencję przy dodaniu przykładowego elementu:

```bash
$ curl -X POST http://localhost:5000/items \
-H "Content-Type: application/json" \
-d '{"name": "element testowy"}'

{"created_at":"2026-04-18 16:16:22.405915", "id":1,"name":"element testowy"}
```

Teraz uruchommy aplikację ponownie. Element rzeczywiście przetrwał restart:
```bash
$ curl http://localhost:5000/items
[{"created_at":"2026-04-18 16:16:22.405915", "id":1,"name":"element testowy"}]
```

# Podsumowanie

W tym laboratorium skupiliśmy się na najlepszych praktykach bezpieczeństwa podczas pracy z Dockerem. Zidentyfikowaliśmy i załataliśmy cztery główne luki:
* **Ustalanie wersji obrazów (Image Pinning)** – zamieniliśmy tag `latest` na konkretną, bezpieczniejszą dystrybucję `alpine`, co zmniejszyło ryzyko ataków i znacząco odchudziło obraz.
* **Usuwanie twardych sekretów (Hardcoded Secrets)** – wynieśliśmy wrażliwe dane z pliku `Dockerfile` zapobiegając wyciekom w historii budowania obrazu (`docker history`).
* **Zarządzanie zmiennymi środowiskowymi** – przenieśliśmy hasła i klucze do wykluczonego z repozytorium pliku `.env`, poprawiając konfigurację `docker-compose.yml`.
* **Ograniczanie uprawnień (Least Privilege)** – skonfigurowaliśmy uruchamianie procesu w kontenerze z poziomu specjalnie utworzonego użytkownika `appuser` (zamiast domyślnego `root`), minimalizując potencjalne straty w przypadku włamania.

Dzięki tym zmianom uzyskaliśmy znacznie bezpieczniejsze i zoptymalizowane środowisko, spełniające podstawowe standardy produkcyjne.