Dokumentacja Laboratorium 5: Docker Security

Cel zadania:
Celem laboratorium było zidentyfikowanie oraz naprawienie luk bezpieczeństwa ukrytych w konfiguracji Dockera (pliki Dockerfile oraz docker-compose.yml). Mimo że sama aplikacja uruchamiała się poprawnie, jej konfiguracja zagrażała integralności hosta oraz poufności danych.

Część 1: Identyfikacja i naprawa podatności
Błąd 1: Niespięte wersje obrazów bazowych (Latest)
Przed naprawą: FROM python:latest (backend), FROM nginx:latest (frontend), image: postgres:latest (baza danych).

Zagrożenie: Używanie tagu latest powoduje pobieranie najnowszej dostępnej wersji obrazu podczas budowania. Prowadzi to do nieprzewidywalnych błędów budowania (co wystąpiło podczas wstępnej inspekcji, gdy nowa wersja Pythona złamała kompatybilność) oraz wystawia system na ataki typu supply chain attack.

Po naprawie: Zamieniono na sztywne, zweryfikowane wersje:

Dockerfile
# frontend/Dockerfile
FROM nginx:1.25-alpine
# backend/Dockerfile
FROM python:3.11-slim
# docker-compose.yml
image: postgres:15
Błąd 2: Hardkodowane sekrety w Dockerfile
Przed naprawą:

Dockerfile
ENV API_KEY=super-secret-api-key-abc123
ENV SECRET_KEY=my-secret-key-do-not-share-2026
Zagrożenie: Użycie instrukcji ENV utrwala sekrety w warstwach obrazu jako czysty tekst. Każda osoba z dostępem do wybudowanego obrazu kontenera mogła w łatwy sposób odczytać te wrażliwe informacje komendą docker history, kompromitując aplikację.

Po naprawie: Usunięto dyrektywy ENV z pliku Dockerfile. Sekrety zostały przeniesione do nienależącego do repozytorium pliku .env i są podawane w locie przez docker-compose.yml:

YAML
environment:
  API_KEY: ${API_KEY}
  SECRET_KEY: ${SECRET_KEY}
Błąd 3: Hardkodowane hasło do bazy danych
Przed naprawą:
W pliku docker-compose.yml:

YAML
POSTGRES_PASSWORD: "password123"
DATABASE_URL: postgresql://devops:password123@db:5432/devops_db
Zagrożenie: Umieszczenie jawnego hasła bezpośrednio w pliku konfiguracji orkiestracji (który jest commitowany do repozytorium Git) oznacza, że hasło na zawsze pozostaje w historii systemu kontroli wersji i jest dostępne dla każdej osoby z prawem do odczytu kodu, co ułatwia m.in. ataki ze strony insiderów.

Po naprawie: Zastąpiono hasła referencjami do zmiennych z pliku .env.

YAML
POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
DATABASE_URL: postgresql://devops:${POSTGRES_PASSWORD}@db:5432/devops_db
Błąd 4: Uruchamianie kontenera z prawami Roota
Przed naprawą: Brak dyrektywy USER w backend/Dockerfile. Domyślnie proces działał jako root wewnątrz kontenera.

Zagrożenie: Uruchamianie jako root to naruszenie zasady najmniejszych uprawnień. Jeżeli cyberprzestępca odkryłby lukę typu RCE (Remote Code Execution) w aplikacji, uzyskałby najwyższe przywileje w kontenerze. Zależnie od konfiguracji demona Docker, znacznie ułatwiłoby to eskalację uprawnień na maszynę gospodarza (hosta).

Po naprawie: Dodano utworzenie nowego użytkownika o ograniczonych uprawnieniach i wymuszono start z jego profilu.

Dockerfile
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser
USER appuser
Część 2: Weryfikacja po wdrożeniu poprawek (Dowody)
1. Potwierdzenie usunięcia uprawnień Roota z kontenera backendu:
Wynik wywołania komendy whoami wskazuje teraz na bezpiecznego użytkownika, a nie na roota:

Bash
tadlesz3@DESKTOP-Q00FRT0:~/DevOps2026/Lab_5/app_422375$ sudo docker compose exec backend whoami
appuser
2. Potwierdzenie oczyszczenia warstw z wrażliwych danych (Błąd 2):
Wywołanie komendy docker history dla uszkodzonego obrazu wyraźnie ukazywało sekrety zapisane otwartym tekstem:

Plaintext
IMAGE          CREATED        CREATED BY                                      SIZE      COMMENT
<missing>      5 days ago     ENV API_KEY=super-secret-api-key-abc123         0B        buildkit.dockerfile.v0
<missing>      5 days ago     ENV SECRET_KEY=my-secret-key-do-not-share-2026  0B        buildkit.dockerfile.v0
Po wdrożeniu poprawek, utworzeniu dedykowanego użytkownika i przeniesieniu sekretów do pliku .env, historia warstw nie zdradza już żadnych poufnych danych:

Plaintext
tadlesz3@DESKTOP-Q00FRT0:~/DevOps2026/Lab_5/app_422375$ sudo docker history app_422375-backend --no-trunc
IMAGE          CREATED        CREATED BY                                                                            SIZE      COMMENT
sha256:...     32 seconds ago CMD ["gunicorn" "--bind" "0.0.0.0:5000" "--workers" "2" "--preload" "app:app"]      0B        buildkit.dockerfile.v0
<missing>      32 seconds ago EXPOSE [5000/tcp]                                                                     0B        buildkit.dockerfile.v0
<missing>      32 seconds ago USER appuser                                                                          0B        buildkit.dockerfile.v0
<missing>      32 seconds ago RUN /bin/sh -c addgroup --system appgroup && adduser --system --ingroup app...        45.1kB    buildkit.dockerfile.v0
<missing>      32 seconds ago RUN /bin/sh -c python -c "import flask; import psycopg2; import gunicorn" # buildkit  12.3kB    buildkit.dockerfile.v0
<missing>      33 seconds ago COPY app.py . # buildkit                                                              180kB     buildkit.dockerfile.v0
<missing>      33 seconds ago RUN /bin/sh -c pip install --no-cache-dir -r requirements.txt # buildkit              27.8MB    buildkit.dockerfile.v0
<missing>      34 seconds ago COPY requirements.txt . # buildkit                                                    12.3kB    buildkit.dockerfile.v0
<missing>      34 seconds ago WORKDIR /app                                                                          0B        buildkit.dockerfile.v0
... [DALSZE WARSTWY BAZOWEGO OBRAZU PYTHON - BRAK ZDEFINIOWANYCH SEKRETÓW] ...
3. Weryfikacja działania aplikacji i persystencji (Krok 6):
Po wdrożeniu poprawek sprawdzono stabilność działania aplikacji endpointów API:

Bash
tadlesz3@DESKTOP-Q00FRT0:~/DevOps2026/Lab_5/app_422375$ curl http://localhost:5000/health
{"status":"ok"}

tadlesz3@DESKTOP-Q00FRT0:~/DevOps2026/Lab_5/app_422375$ curl -X POST http://localhost:5000/items -H "Content-Type: application/json" -d '{"name": "element bezpieczny"}'
{"created_at":"2026-05-13 23:31:37.081358","id":1,"name":"element bezpieczny"}

tadlesz3@DESKTOP-Q00FRT0:~/DevOps2026/Lab_5/app_422375$ sudo docker compose down
tadlesz3@DESKTOP-Q00FRT0:~/DevOps2026/Lab_5/app_422375$ sudo docker compose up -d

tadlesz3@DESKTOP-Q00FRT0:~/DevOps2026/Lab_5/app_422375$ curl http://localhost:5000/items
[{"created_at":"2026-05-13 23:31:37.081358","id":1,"name":"element bezpieczny"}]
Podsumowanie
Wszystkie 4 luki bezpieczeństwa (brak ustalonych wersji obrazów, hardkodowane sekrety w Dockerfile, jawne hasło w docker-compose.yml oraz uprawnienia root w kontenerze) zostały odnalezione, przeanalizowane i skutecznie wyeliminowane. Przebudowana aplikacja działa poprawnie, a jej konfiguracja jest teraz zgodna z podstawowymi dobrymi praktykami bezpieczeństwa środowisk kontenerowych (Docker Security Best Practices).
