# Sprawozdanie — Lab 5: Bezpieczeństwo Docker i Docker Compose

**Student:** 999999  
**Data:** 2026-04-10  
**Repozytorium:** DevOps2026  
**Branch:** lab5-test

---

## Wstęp

Celem laboratorium było zapoznanie się z typowymi problemami bezpieczeństwa w konfiguracji Dockera i Docker Compose. Aplikacja dostarczona w szablonie `app_0000` działała poprawnie funkcjonalnie, jednak zawierała sześć poważnych luk bezpieczeństwa. Poniżej opisano każdy z wykrytych problemów: co było błędem, jakie stanowi zagrożenie, jak zostało naprawione i jak można zweryfikować poprawność naprawy.

---

## BŁĄD 1 — Niespięte wersje obrazów bazowych (`latest`)

### Co było błędem

W plikach `backend/Dockerfile`, `frontend/Dockerfile` oraz `docker-compose.yml` używano tagu `latest` dla obrazów bazowych:

```dockerfile
# backend/Dockerfile — przed naprawą
FROM python:latest
```

```dockerfile
# frontend/Dockerfile — przed naprawą
FROM nginx:latest
```

```yaml
# docker-compose.yml — przed naprawą
  db:
    image: postgres:latest
```

### Zagrożenie bezpieczeństwa

Tag `latest` nie wskazuje na konkretną wersję obrazu — jest to dynamiczny alias, który w dowolnej chwili może zmienić swoje wskazanie na nową wersję. W środowisku produkcyjnym oznacza to:

- **Nieprzewidywalność wdrożeń** — po `docker pull` lub po rebuildzie obraz może zawierać zupełnie inną wersję oprogramowania, co może złamać działającą aplikację.
- **Brak kontroli nad podatnościami** — nowa wersja obrazu może wprowadzić nowe CVE (Common Vulnerabilities and Exposures), o których operator może nie wiedzieć.
- **Problemy z odtwarzalnością** — środowisko produkcyjne, staging i development mogą działać na różnych wersjach obrazów, jeśli `latest` zmienił wskazanie.

### Naprawa

```dockerfile
# backend/Dockerfile — po naprawie
FROM python:3.11-slim
```

```dockerfile
# frontend/Dockerfile — po naprawie
FROM nginx:1.25-alpine
```

```yaml
# docker-compose.yml — po naprawie
  db:
    image: postgres:15
```

Dodatkowo użyto wariantów `-slim` i `-alpine`, które są mniejsze, mają mniejszą powierzchnię ataku i mniej potencjalnych podatności niż pełne obrazy.

### Weryfikacja

```bash
docker inspect lab5_app_999999_backend | grep -i "python"
# Wynik powinien zawierać: "python:3.11-slim"
```

---

## BŁĄD 2 — Hardkodowane sekrety w Dockerfile (`ENV`)

### Co było błędem

W pliku `backend/Dockerfile` znajdowały się dwie linie ustawiające zmienne środowiskowe z wartościami sekretów bezpośrednio w pliku:

```dockerfile
# backend/Dockerfile — przed naprawą
ENV API_KEY=super-secret-api-key-abc123
ENV SECRET_KEY=my-secret-key-do-not-share-2026
```

### Zagrożenie bezpieczeństwa

Dyrektywa `ENV` w Dockerfile zapisuje wartość na stałe w warstwie obrazu Docker. Oznacza to, że:

- **Każdy, kto posiada obraz**, może odczytać te wartości przez `docker history <image> --no-trunc` lub `docker inspect <image>`.
- **Sekrety trafiają do rejestru** — jeśli obraz jest pushowany do Docker Hub lub prywatnego rejestru, sekrety są tam przechowywane na stałe.
- **Historia git ujawnia sekrety** — Dockerfile jest przechowywany w repozytorium git, więc sekrety są widoczne w historii commitów.
- **Rotacja jest niemożliwa bez rebuildu** — zmiana klucza API wymaga przebudowania całego obrazu.

Wynik `docker history` przed naprawą (symulowany):
```
IMAGE          CREATED BY
<id>           /bin/sh -c #(nop)  ENV API_KEY=super-secret-api-key-abc123
<id>           /bin/sh -c #(nop)  ENV SECRET_KEY=my-secret-key-do-not-share-2026
```

### Naprawa

Usunięto linie `ENV` z `backend/Dockerfile`. Sekrety są teraz przekazywane przez plik `.env` i sekcję `environment` w `docker-compose.yml`:

```yaml
# docker-compose.yml — po naprawie
  backend:
    environment:
      API_KEY: ${API_KEY}
      SECRET_KEY: ${SECRET_KEY}
```

Plik `.env` zawiera rzeczywiste wartości i **nie powinien** trafiać do repozytorium git (dodać do `.gitignore`).

### Weryfikacja

```bash
docker history lab5_app_999999_backend --no-trunc
# Wynik NIE powinien zawierać wartości API_KEY ani SECRET_KEY

docker compose exec backend env | grep API_KEY
# Wynik powinien pokazać wartość z pliku .env: API_KEY=change-me-in-production
```

---

## BŁĄD 3 — Hardkodowane hasło w `docker-compose.yml`

### Co było błędem

W pliku `docker-compose.yml` hasło do bazy danych oraz pełny URL bazy były zapisane jawnym tekstem:

```yaml
# docker-compose.yml — przed naprawą
  db:
    environment:
      POSTGRES_PASSWORD: "password123"

  backend:
    environment:
      DATABASE_URL: postgresql://devops:password123@db:5432/devops_db
```

### Zagrożenie bezpieczeństwa

Plik `docker-compose.yml` jest plikiem konfiguracyjnym aplikacji, który zazwyczaj jest commitowany do repozytorium git. Skutki:

- **Hasło widoczne w historii commitów** — nawet po usunięciu go z bieżącej wersji pliku, hasło pozostaje w historii git i jest dostępne przez `git log -p`.
- **Każdy z dostępem do repozytorium zna hasło** — w projektach open-source lub przy wycieku repozytorium hasło do bazy danych jest od razu kompromitowane.
- **Ryzyko ponownego użycia hasła** — proste hasła jak `password123` są łatwe do odgadnięcia i mogą być używane przez programistów w innych miejscach.

### Naprawa

```yaml
# docker-compose.yml — po naprawie
  db:
    environment:
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}

  backend:
    environment:
      DATABASE_URL: postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@db:5432/${POSTGRES_DB}
```

Wartości są teraz pobierane z pliku `.env`, który nie jest commitowany do repozytorium.

### Weryfikacja

```bash
# .env zawiera:
# POSTGRES_PASSWORD=devops123

docker compose config | grep POSTGRES_PASSWORD
# Wynik powinien pokazać podstawioną wartość: POSTGRES_PASSWORD: devops123
# (Ale plik docker-compose.yml nie zawiera literalnego "devops123")
```

---

## BŁĄD 4 — Kontener uruchomiony jako root

### Co było błędem

W oryginalnym `backend/Dockerfile` brakowało dyrektywy `USER`, co oznacza, że aplikacja uruchamiała się z uprawnieniami użytkownika `root` wewnątrz kontenera:

```dockerfile
# backend/Dockerfile — przed naprawą (brak USER i brak adduser)
FROM python:latest
WORKDIR /app
# ... (brak tworzenia użytkownika i brak USER)
CMD ["gunicorn", "--bind", "0.0.0.0:5000", ...]
```

Weryfikacja przed naprawą:
```bash
docker compose exec backend whoami
# Wynik: root
```

### Zagrożenie bezpieczeństwa

Uruchamianie procesu aplikacji jako root wewnątrz kontenera stanowi poważne zagrożenie:

- **Eskalacja uprawnień** — jeśli w aplikacji webowej istnieje podatność Remote Code Execution (RCE), atakujący uzyskuje uprawnienia roota wewnątrz kontenera.
- **Przejęcie hosta** — root w kontenerze, w połączeniu z błędami konfiguracji Docker (np. podmontowanym `/proc`, `/sys` lub gniazdem Docker), może prowadzić do ucieczki z kontenera i przejęcia kontroli nad hostem.
- **Dostęp do wrażliwych plików** — root może czytać i modyfikować dowolne pliki w systemie plików kontenera, w tym konfiguracje, certyfikaty i tokeny.
- **Naruszenie zasady minimalnych uprawnień (PoLP)** — aplikacja webowa nie potrzebuje uprawnień roota do swojego działania.

### Naprawa

```dockerfile
# backend/Dockerfile — po naprawie
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser
USER appuser
```

Stworzono dedykowanego użytkownika systemowego `appuser` bez powłoki i bez hasła, należącego do grupy `appgroup`. Przed uruchomieniem aplikacji następuje przełączenie na tego użytkownika.

### Weryfikacja

```bash
docker compose exec backend whoami
# Oczekiwany wynik: appuser (nie root)

docker compose exec backend id
# Oczekiwany wynik: uid=999(appuser) gid=999(appgroup) groups=999(appgroup)
```

---

## BŁĄD 5 — Nadmierne uprawnienia do plików (`chmod 777`)

### Co było błędem

W `backend/Dockerfile` katalog `/app` był ustawiany z uprawnieniami `777`:

```dockerfile
# backend/Dockerfile — przed naprawą
RUN chmod 777 /app
```

### Zagrożenie bezpieczeństwa

Uprawnienia `777` (`rwxrwxrwx`) oznaczają, że **każdy użytkownik w systemie** może czytać, zapisywać i wykonywać pliki w katalogu `/app`. Konsekwencje:

- **Modyfikacja kodu aplikacji** — jeśli atakujący uzyska dostęp do jakiegokolwiek procesu działającego w kontenerze (nawet jako inny, nieuprzywilejowany użytkownik), może nadpisać pliki aplikacji (np. `app.py`) złośliwym kodem.
- **Wstrzyknięcie malware** — możliwe jest dopisanie backdoora do pliku aplikacji, który zostanie wykonany przy obsłudze następnego żądania.
- **Naruszenie integralności** — brak ochrony katalogu aplikacji podważa zasadę integralności kodu (code integrity).
- **Standardy bezpieczeństwa** — większość standardów (CIS Benchmarks, NIST) wymaga restrykcyjnych uprawnień do katalogów zawierających kod wykonywany przez usługi.

### Naprawa

```dockerfile
# backend/Dockerfile — po naprawie
RUN chmod 755 /app
```

Uprawnienia `755` (`rwxr-xr-x`) oznaczają, że właściciel ma pełny dostęp, a pozostali użytkownicy mogą tylko czytać i wykonywać (ale nie zapisywać) pliki w katalogu.

### Weryfikacja

```bash
docker compose exec backend ls -la /
# Wynik powinien pokazać: drwxr-xr-x ... app
# (755, nie 777)
```

---

## BŁĄD 6 — Podmontowanie gniazda Docker (`/var/run/docker.sock`)

### Co było błędem

W sekcji `volumes` serwisu `db` w `docker-compose.yml` znajdowało się podmontowanie gniazda Docker:

```yaml
# docker-compose.yml — przed naprawą
  db:
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - /var/run/docker.sock:/var/run/docker.sock
```

### Zagrożenie bezpieczeństwa

Gniazdo Docker (`/var/run/docker.sock`) to interfejs Unix Socket, przez który klient Docker komunikuje się z demonem Docker na hoście. Podmontowanie go do kontenera:

- **Daje pełną kontrolę nad demonem Docker** — kontener może tworzyć, uruchamiać, zatrzymywać i usuwać inne kontenery na hoście.
- **Jest równoznaczne z uprawnieniami roota na hoście** — przez API Dockera można uruchomić uprzywilejowany kontener (`--privileged`) z podmontowanym katalogiem głównym hosta (`-v /:/host`), co daje pełny dostęp do systemu plików hosta.
- **Umożliwia eskalację z kontenera na host** — nawet jeśli aplikacja działa jako nieuprzywilejowany użytkownik wewnątrz kontenera, dostęp do gniazda Docker pozwala na pełną kompromitację hosta.
- **CVE i exploity** — istnieją udokumentowane techniki ataku (container escape) wykorzystujące podmontowane gniazdo Docker.
- **Zasada minimalnych uprawnień** — serwis bazy danych `postgres` nie ma absolutnie żadnej potrzeby dostępu do demona Docker.

### Naprawa

```yaml
# docker-compose.yml — po naprawie
  db:
    volumes:
      - postgres_data:/var/lib/postgresql/data
      # Usunięto: - /var/run/docker.sock:/var/run/docker.sock
```

Linia z podmontowaniem gniazda Docker została całkowicie usunięta.

### Weryfikacja

```bash
docker compose exec db ls -la /var/run/docker.sock 2>&1
# Oczekiwany wynik: błąd "No such file or directory"
# (gniazdo nie jest dostępne wewnątrz kontenera)

docker inspect lab5_app_999999_db | grep docker.sock
# Oczekiwany wynik: brak wyników
```

---

## Podsumowanie naprawionych błędów

| # | Plik | Błąd | Naprawa |
|---|------|------|---------|
| 1 | Wszystkie Dockerfile, docker-compose.yml | Tag `latest` dla obrazów | Spięto wersje: `python:3.11-slim`, `nginx:1.25-alpine`, `postgres:15` |
| 2 | backend/Dockerfile | `ENV API_KEY=...` i `ENV SECRET_KEY=...` | Usunięto z Dockerfile; przekazywane przez `docker-compose.yml` z pliku `.env` |
| 3 | docker-compose.yml | `POSTGRES_PASSWORD: "password123"` i hardkodowany URL | Zastąpiono zmiennymi: `${POSTGRES_PASSWORD}`, `${POSTGRES_USER}`, `${POSTGRES_DB}` |
| 4 | backend/Dockerfile | Brak `USER` — kontener działa jako root | Dodano `adduser appuser` i `USER appuser` |
| 5 | backend/Dockerfile | `chmod 777 /app` | Zmieniono na `chmod 755 /app` |
| 6 | docker-compose.yml | `/var/run/docker.sock:/var/run/docker.sock` w wolumenach `db` | Usunięto podmontowanie gniazda Docker |

---

## Tematy dodatkowe

### Docker Content Trust (DCT)

Docker Content Trust (DCT) to mechanizm weryfikacji autentyczności i integralności obrazów Docker oparty na podpisach kryptograficznych (Notary/TUF — The Update Framework). Dzięki DCT można mieć pewność, że pobierany obraz pochodzi od zaufanego wydawcy i nie został zmodyfikowany w trakcie przesyłania.

Aby włączyć DCT:
```bash
export DOCKER_CONTENT_TRUST=1
```

Po włączeniu:
- `docker pull` weryfikuje podpis obrazu i odrzuca niepodpisane obrazy.
- `docker push` automatycznie podpisuje pushowany obraz.
- Próba uruchomienia niepodpisanego obrazu kończy się błędem: `Error: remote trust data does not exist`.

W praktyce DCT zmienia podejście do zarządzania obrazami: każdy obraz musi być podpisany kluczem prywatnym, a klucze publiczne (root key, targets key) są przechowywane w Notary Server. Wymaga to zarządzania kluczami kryptograficznymi (generowanie, przechowywanie, rotacja), co zwiększa bezpieczeństwo kosztem dodatkowej złożoności operacyjnej.

DCT jest szczególnie ważne w środowiskach produkcyjnych, gdzie atakujący mógłby przeprowadzić atak "man-in-the-middle" na rejestr Docker i podmienić obraz na złośliwy.

### Multi-stage builds

Multi-stage builds to technika budowania obrazów Docker, w której jeden `Dockerfile` zawiera wiele sekcji `FROM`. Każda sekcja to niezależny etap budowania. Tylko artefakty jawnie skopiowane z poprzednich etapów (`COPY --from=<stage>`) trafiają do końcowego obrazu.

Przykład dla aplikacji Python:
```dockerfile
# Etap 1: Budowanie (zawiera narzędzia kompilacji, pip, wheel)
FROM python:3.11 AS builder
WORKDIR /build
COPY requirements.txt .
RUN pip wheel --no-cache-dir --wheel-dir /wheels -r requirements.txt

# Etap 2: Produkcja (tylko niezbędne elementy)
FROM python:3.11-slim AS production
COPY --from=builder /wheels /wheels
RUN pip install --no-cache-dir --no-index --find-links=/wheels /wheels/*.whl
```

Korzyści dla bezpieczeństwa:
- **Mniejsza powierzchnia ataku** — obraz produkcyjny nie zawiera kompilatora, pip, ani narzędzi deweloperskich, które mogłyby zostać użyte przez atakującego.
- **Mniej podatności CVE** — każda zainstalowana paczka to potencjalna podatność; mniejszy obraz = mniej CVE w raportach skanerów bezpieczeństwa (Trivy, Snyk, Grype).
- **Brak narzędzi do eksploatacji** — atakujący, który uzyska RCE, nie ma dostępu do `gcc`, `curl`, `wget` czy innych narzędzi przydatnych w post-exploitation.

### Docker Secrets w Docker Swarm

Docker Secrets (`docker secret`) to mechanizm bezpiecznego zarządzania wrażliwymi danymi w Docker Swarm (orkiestratorze kontenerów). Sekrety są:
- Szyfrowane w spoczynku (AES-256-GCM) w Raft log Swarm managera.
- Przekazywane do kontenerów przez szyfrowany kanał TLS.
- Montowane jako pliki w `/run/secrets/<secret_name>` wewnątrz kontenera (nie jako zmienne środowiskowe).
- Dostępne tylko dla serwisów, którym jawnie przyznano dostęp.

Różnice względem zmiennych środowiskowych:
| Aspekt | Docker Secrets | Zmienne środowiskowe (`env_file`) |
|--------|---------------|----------------------------------|
| Szyfrowanie | TAK (AES-256) | NIE (plaintext w `.env`) |
| Widoczność | Tylko w `/run/secrets/` | `docker inspect` ujawnia wartości |
| Orkiestracja | Tylko Docker Swarm | Wszystkie środowiska |
| Rotacja | Bez restartu serwisu | Wymaga restartu kontenera |
| Audit | Centralny rejestr Swarm | Brak centralnego zarządzania |

Główna różnica: zmienne środowiskowe mogą być widoczne przez `docker inspect`, w logach procesów (`/proc/<pid>/environ`), a wartości mogą wyciec przez niedbałe logowanie aplikacji. Sekrety Docker są dostępne jako pliki tylko dla uprawnionego procesu i nie są eksponowane przez API Docker.

---

## Wnioski

Laboratorium pokazało, że aplikacja może działać poprawnie funkcjonalnie, a jednocześnie zawierać poważne luki bezpieczeństwa. Wszystkie sześć naprawionych błędów to typowe problemy spotykane w rzeczywistych projektach, szczególnie na wczesnych etapach rozwoju, gdy priorytetem jest funkcjonalność, a nie bezpieczeństwo.

Kluczowe wnioski:
1. **Sekrety nigdy nie powinny trafiać do kodu** — ani do Dockerfile, ani do docker-compose.yml.
2. **Zasada minimalnych uprawnień** — kontenery powinny działać z najniższymi możliwymi uprawnieniami.
3. **Spięte wersje obrazów** — zawsze używaj konkretnych tagów wersji dla odtwarzalności i przewidywalności.
4. **Gniazdo Docker to klucz do hosta** — podmontowanie `/var/run/docker.sock` to jeden z najpoważniejszych błędów konfiguracyjnych Docker.

---

## Ocena zadania

### Co było dobrze zaprojektowane w zadaniu

Zadanie jest bardzo dobrze przemyślane pod względem pedagogicznym. Sześć błędów obejmuje
różne kategorie zagrożeń — od niespójności wersji, przez wycieki sekretów, po eskalację
uprawnień — co daje szeroki, przekrojowy przegląd tematu bezpieczeństwa kontenerów.
Podejście "napraw istniejący kod" zamiast "napisz od zera" jest wartościowe, bo uczy
czytania i audytu cudzej konfiguracji, co jest codzienną pracą inżyniera DevSecOps.

Aplikacja jest na tyle prosta (Flask + PostgreSQL + Nginx), że student nie gubi się
w logice biznesowej i skupia się wyłącznie na aspektach bezpieczeństwa. Jednocześnie
jest wystarczająco realistyczna, żeby pokazać rzeczywiste problemy z prawdziwych projektów.

Szczególnie dobrze zaprojektowany jest **błąd 6** (docker.sock): gniazdo Dockera jest
podmontowane do serwisu `db`, gdzie nie ma absolutnie żadnego uzasadnienia. To zmusza
studenta do rzeczywistego zastanowienia się nad tym, czego każdy serwis faktycznie
potrzebuje — zamiast mechanicznego poprawiania zaznaczonych linii.

**GitHub Action** z dwoma jobami (`security-checks` i `build-and-test`) jest rzetelny.
Nie ogranicza się do sprawdzenia tekstu konfiguracji — faktycznie buduje obrazy,
uruchamia kontenery i weryfikuje działanie poprawek end-to-end (whoami, warstwy obrazu,
persystencja danych po restarcie). To szczególnie cenne, bo uczy, że poprawność
konfiguracji bezpieczeństwa powinna być testowana automatycznie.

---

### Co było trudne lub niejasne

Najbardziej nieoczywiste były **błąd 2 w połączeniu z błędem 3**. Samo usunięcie
`ENV API_KEY=...` z Dockerfile nie wystarczy — trzeba równocześnie dodać te zmienne
do sekcji `environment:` w `docker-compose.yml` oraz zadbać o spójność pliku
`.env` i `.env.example`. Instrukcja mogłaby wyraźniej zaznaczyć, że naprawienie
błędu 2 wymaga skoordynowanych zmian w dwóch plikach jednocześnie.

Kolejna niejasność dotyczy **kolejności dyrektyw w Dockerfile** przy naprawie błędu 4.
Dyrektywa `USER appuser` musi być umieszczona po `RUN chmod` i `RUN pip install`,
ale przed `CMD`. Student musi rozumieć, że zmiana właściciela pliku lub `chmod`
wykonana po `USER appuser` może się nie powieść, jeśli nieuprzywilejowany użytkownik
nie ma uprawnień do modyfikacji danego katalogu. Jest to ważny niuans warstw Docker,
który nie jest wprost wyjaśniony w README — student musi go wydedukować samodzielnie
lub natknąć się na błąd przy budowaniu.

Ponadto, w README brak jest informacji, że `.env` powinien być w `.gitignore`.
Zadanie wymaga utworzenia pliku `.env` z prawdziwymi wartościami, ale nie mówi wprost,
że nie wolno go commitować — student pracujący po raz pierwszy z Docker Compose
może to przeoczyć.

---

### Co można poprawić w instrukcji lub szablonie

**1. Wskazówka o `.gitignore` dla `.env`**  
Szablon powinien zawierać gotowy plik `.gitignore` (lub przynajmniej jego fragment)
z wpisem `.env`. Alternatywnie README powinien zawierać wyraźne ostrzeżenie:
*"Nie commituj pliku `.env` do repozytorium — dodaj go do `.gitignore`"*.

**2. Sekcja "Jak zweryfikować każdą poprawkę lokalnie"**  
Przy każdym z 6 błędów warto podać konkretną komendę weryfikacyjną, np.:
- Błąd 2: `docker history <image> --no-trunc | grep -E "API_KEY|SECRET_KEY"`
- Błąd 4: `docker compose exec backend whoami`
- Błąd 6: `docker compose exec db ls /var/run/docker.sock`

Taka sekcja uczy studenta nie tylko jak naprawić problem, ale jak go zweryfikować —
co jest kluczową umiejętnością inżyniera DevSecOps.

**3. Sugestia dotycząca `.dockerignore`**  
Szablon nie zawiera pliku `.dockerignore`. W realnych projektach jego brak powoduje
kopiowanie do kontekstu budowania pliku `.env`, pliku `.git/`, `__pycache__` itd.
Warto dodać to jako opcjonalne zadanie rozszerzające lub przynajmniej o tym wspomnieć.

**4. Wyraźniejszy opis zależności między błędami 2 i 3**  
README powinien zawierać akapit wyjaśniający, że "naprawa błędu 2 (ENV w Dockerfile)
jest ściśle powiązana z naprawą błędu 3 (docker-compose.yml) — oba błędy razem tworzą
kompletny problem zarządzania sekretami i powinny być naprawiane razem".

**5. Numeracja komentarzy w szablonie `app_0000`**  
Warto zostawić komentarze `# BLAD N:` przy każdym błędzie w plikach szablonu,
żeby student miał pewność, ile błędów jest w danym pliku i gdzie dokładnie.
Aktualnie student musi samodzielnie znaleźć i policzyć błędy bez podpowiedzi
co do ich lokalizacji.

---

### Czy GitHub Action poprawnie weryfikuje wszystkie poprawki

**Tak** — GitHub Action (`lab_5.yml`) jest starannie napisany i skutecznie weryfikuje
wszystkie 6 poprawek. Kilka szczegółowych obserwacji:

- **Błąd 1**: sprawdzany zarówno w Dockerfile (regex `FROM ... :latest`), jak
  i w `docker-compose.yml` (przez parser YAML w Python). Dobrze obsługuje przypadek
  obrazu bez jakiegokolwiek tagu (np. `image: postgres` bez dwukropka), który traktuje
  jako równoważny `latest`.

- **Błąd 2**: używa wyrażeń regularnych do wyszukania `ENV API_KEY=` z wartością
  nie będącą referencją `${...}`. Podejście jest poprawne dla standardowej składni.
  Nie obsługuje wieloliniowej składni `ENV KEY1=v1 \\\n    KEY2=v2`, ale jest to
  mało prawdopodobny przypadek w tym ćwiczeniu.

- **Błąd 3**: sprawdza zarówno `POSTGRES_PASSWORD` w sekcji `db`, jak i hasło
  wbudowane w `DATABASE_URL` backendu za pomocą wyrażenia regularnego na URL
  `postgresql://user:PASSWORD@host`. Bardzo dokładne i wielowarstwowe podejście.

- **Błąd 4**: weryfikuje obecność `USER` w Dockerfile i jawnie odrzuca `USER root`
  oraz `USER 0`. Poprawna i skuteczna logika.

- **Błąd 5**: prosty `grep` na `chmod 777` — wystarczający dla tego przypadku.

- **Błąd 6**: `grep -q docker.sock` w pliku `docker-compose.yml` — minimalistyczny,
  ale skuteczny, bo ciąg `docker.sock` nie pojawi się w poprawnej konfiguracji.

**Jedna potencjalna luka w weryfikacji CI**: workflow nie sprawdza, czy plik `.env`
nie jest przypadkowo commitowany do repozytorium (brak kroku weryfikującego `.gitignore`).
Student mógłby "naprawić" błąd 3 przez usunięcie hardkodowanych haseł z docker-compose.yml,
ale jednocześnie wkomitować plik `.env` z tymi samymi hasłami — CI zatwierdzi PR,
a bezpieczeństwo i tak będzie naruszone.

---

### Sugestie dla prowadzącego (co dodać/zmienić w Lab 5)

**1. Dodanie błędu 7 — brak `.dockerignore` (opcjonalny)**  
Brak `.dockerignore` powoduje, że plik `.env` jest kopiowany do kontekstu budowania
i potencjalnie trafia do warstw obrazu. Byłoby to naturalne rozszerzenie lekcji
z błędów 2 i 3 — kompletny łańcuch zarządzania sekretami.

**2. Rozszerzenie CI o sprawdzenie `.gitignore`**  
Dodanie kroku weryfikującego, że `.env` jest w `.gitignore` (lub nie jest w indeksie git):
```bash
git check-ignore -q "Lab_5/app_NNNNN/.env" || \
  (echo "::warning::.env nie jest w .gitignore — sekrety mogą trafić do repozytorium"; exit 0)
```

**3. Integracja skanera CVE (Trivy lub Grype)**  
Po zbudowaniu obrazów warto uruchomić `trivy image --severity HIGH,CRITICAL <image>`.
Studenci zobaczą, że spięte wersje obrazów (błąd 1) bezpośrednio przekładają się
na liczbę wykrytych CVE — co nadaje temu błędowi mierzalny, konkretny wymiar.

**4. Zadanie "Zanim naprawisz — udokumentuj exploit"**  
Ciekawe wzbogacenie: przed naprawieniem każdego błędu, student powinien udowodnić,
że błąd jest exploitowalny. Na przykład:
- Błąd 2: `docker history <image> --no-trunc | grep SECRET` — dokumentacja wycieku
- Błąd 4: `docker compose exec backend whoami` → `root` — dokumentacja konta root
- Błąd 6: `docker compose exec db docker ps` przez podmontowane gniazdo

Takie "najpierw exploit, potem fix" lepiej motywuje i utrwala wiedzę.

**5. Sekcja o Docker Bench for Security**  
Docker Bench for Security (https://github.com/docker/docker-bench-security) to narzędzie
automatycznie sprawdzające konfigurację Dockera pod kątem CIS Docker Benchmark.
Uruchomienie go przed i po naprawkach, ze zrzutem ekranu porównującym wyniki,
byłoby wartościowym ćwiczeniem pokazującym praktyczne zastosowanie standardów.

**6. Informacja o środowiskach produkcyjnych — Docker Secrets / Vault**  
Dla zaawansowanych: krótka sekcja o tym, że w produkcji plik `.env` jest
zastępowany przez Docker Secrets (Swarm), Kubernetes Secrets lub zewnętrzny Vault
(HashiCorp Vault, AWS Secrets Manager). Daje to studentom perspektywę, co czeka ich
poza środowiskiem lokalnym.
