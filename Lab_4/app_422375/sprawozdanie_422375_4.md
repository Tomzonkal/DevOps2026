Dokumentacja Laboratorium 4: Diagnostyka i naprawa środowiska Docker Compose
Cel zadania:
Głównym założeniem laboratorium była analiza, zidentyfikowanie i usunięcie błędów konfiguracyjnych w wielokontenerowej aplikacji (PostgreSQL, backend we Flasku, frontend w Nginx). Aplikacja nie działała poprawnie ze względu na celowo wprowadzone usterki w pliku docker-compose.yml.

Część 1: Analiza architektoniczna i naprawa konfiguracji
Proces debugowania opierał się na analizie logów generowanych przez kontenery oraz audycie pliku konfiguracyjnego środowiska. Wykryte anomalie podzieliłem na trzy główne kategorie:

1.1. Rozwiązywanie problemów z siecią i komunikacją (Backend <-> Baza danych)
Symptomy: Aplikacja backendowa w logach zwracała błąd Error: Could not connect to database after 10 attempts, co jasno wskazywało na problem z warstwą sieciową lub błędne dane uwierzytelniające.
Diagnoza i wdrożone poprawki:

Błędny adres hosta: Zmienna środowiskowa DATABASE_URL kierowała ruch do hosta o nazwie database (fragment ...postgres@database:5432...). Wewnętrzny serwer DNS Dockera nie mógł rozwiązać tej nazwy, ponieważ usługa bazy danych została zadeklarowana jako db. Zmodyfikowałem URL tak, aby wskazywał na właściwy kontener (@db).

Izolacja sieciowa: Mimo poprawy nazwy, usługi nadal się nie widziały. Analiza sekcji networks wykazała, że backend znajdował się wyłącznie w sieci app_network, a baza danych w db_network. Dodałem db_network do definicji backendu, co otworzyło kanał komunikacyjny.

1.2. Optymalizacja zależności Frontendu
Symptomy: Błędy logiczne w architekturze uruchamiania aplikacji.
Diagnoza i wdrożone poprawki:
W pliku konfiguracyjnym frontend posiadał dyrektywę depends_on: - db oraz był wpięty w sieć db_network. Z punktu widzenia wzorców projektowych jest to błąd – warstwa prezentacji nie powinna mieć bezpośredniego dostępu do bazy danych.
Zmieniłem konfigurację frontendu tak, aby zależał bezpośrednio od usługi backend (depends_on: - backend) oraz usunąłem go z sieci bazodanowej, zostawiając jedynie w app_network.

1.3. Konfiguracja mechanizmu persystencji danych
Symptomy: Baza danych uruchamiała się poprawnie, jednak po wykonaniu restartu kontenerów wszelkie zapisane informacje znikały.
Diagnoza i wdrożone poprawki:
Zidentyfikowałem błędną ścieżkę montowania wolumenu dla obrazu postgres:15. Zadeklarowana ścieżka /var/lib/postgresql nie jest docelowym folderem, w którym silnik bazy zapisuje swoje pliki. Poprawiłem mapowanie wolumenu dodając podkatalog /data na końcu ścieżki (zgodnie z oficjalną specyfikacją obrazu). Ścieżka po naprawie: postgres_data:/var/lib/postgresql/data.

Część 2: Weryfikacja działania systemu
Po naniesieniu poprawek przebudowałem środowisko poleceniem docker compose up --build. Wszystkie usługi wystartowały poprawnie.

2.1. Testy komunikacji i interfejsów (API)
Wykonano zapytania w celu potwierdzenia gotowości poszczególnych komponentów:

Test witalności (Backend):

Bash
curl http://localhost:5000/health
# Otrzymana odpowiedź: {"status":"ok"}
Test początkowego stanu bazy (Backend):

Bash
    curl http://localhost:5000/items
    # Otrzymana odpowiedź: []
    ```
*   **Test serwera WWW (Frontend):**
    Wykonanie `curl http://localhost:80` zwróciło poprawną strukturę dokumentu HTML.

### 2.2. Walidacja wolumenów (Trwałość danych)
W celu sprawdzenia poprawnego działania zmapowanych wolumenów, zasymulowano pracę z API.

1. **Wprowadzenie testowych rekordów:**
   Wysłano dwa żądania POST dodające nowe elementy:
   
```bash
   curl -X POST http://localhost:5000/items -H "Content-Type: application/json" -d '{"name":"test"}'
   curl -X POST http://localhost:5000/items -H "Content-Type: application/json" -d '{"name":"Kacper"}'
Potwierdzenie zapisu:

Bash
curl http://localhost:5000/items
# Oczekiwany wynik ze struktury JSON:
# [{"created_at":"2026-04-21 09:21:09.473756","id":1,"name":"test"},{"created_at":"2026-04-21 09:22:16.371790","id":2,"name":"Kacper"}]
Cykl życia kontenera (Restart):
Zatrzymano środowisko (docker compose down) i uruchomiono je ponownie (docker compose up). Ponowne odpytanie endpointu /items zwróciło listę z dodanymi wcześniej elementami, co jednoznacznie potwierdza poprawne skonfigurowanie persystencji.

Czyszczenie wolumenów:
Wykonanie komendy docker compose down -v całkowicie usunęło powiązane wolumeny. Po ponownym postawieniu środowiska, baza danych zwróciła czysty stan ([]).

Podsumowanie
Wszystkie błędy strukturalne i konfiguracyjne zostały skutecznie odnalezione i wyeliminowane. Przebudowana aplikacja działa stabilnie, zapewnia poprawną separację sieciową serwisów oraz odpowiednio realizuje mechanizm trwałego przechowywania danych za pomocą zmapowanych wolumenów. Wymogi laboratorium zostały zrealizowane w całości.
