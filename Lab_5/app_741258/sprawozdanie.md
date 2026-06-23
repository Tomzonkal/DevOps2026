# Sprawozdanie — Lab 5: Naprawa błędów bezpieczeństwa Docker

**Student:** 741258  
**Data:** 2026-04-14

## Opis naprawionych błędów

### BŁĄD 1 — Niespięte wersje obrazów bazowych (`latest`)

**Problem:** Użycie tagu `latest` w obrazach bazowych jest niebezpieczne, ponieważ przy każdym buildzie może zostać pobrany inny obraz. Utrudnia to reprodukowalność środowiska i może wprowadzić nieoczekiwane zmiany, w tym luki bezpieczeństwa.

**Poprawka:**
- `backend/Dockerfile`: `FROM python:latest` → `FROM python:3.12.3-slim`
- `frontend/Dockerfile`: `FROM nginx:latest` → `FROM nginx:1.27.0-alpine`
- `docker-compose.yml`: `image: postgres:latest` → `image: postgres:16.3-alpine`

Użycie konkretnych wersji gwarantuje powtarzalność buildów i kontrolę nad aktualizacjami.

---

### BŁĄD 2 — Hardkodowane sekrety w ENV w Dockerfile

**Problem:** Umieszczanie sekretów (kluczy API, kluczy szyfrowania) bezpośrednio w Dockerfile powoduje, że trafiają one do warstw obrazu Docker. Każdy, kto ma dostęp do obrazu, może je odczytać poleceniem `docker history` lub `docker inspect`.

**Poprawka:** Usunięto z `backend/Dockerfile` linie:
```
ENV API_KEY=super-secret-api-key-abc123
ENV SECRET_KEY=my-secret-key-do-not-share-2026
```
Zmienne `API_KEY` i `SECRET_KEY` są teraz przekazywane przez sekcję `environment` w `docker-compose.yml` z odwołaniem do pliku `.env` (np. `API_KEY: ${API_KEY}`).

---

### BŁĄD 3 — Hardkodowane hasło w docker-compose.yml

**Problem:** Hasło do bazy danych zapisane jawnie w pliku `docker-compose.yml` trafia do repozytorium git. Każda osoba z dostępem do repozytorium zna dane uwierzytelniające do produkcyjnej bazy danych.

**Poprawka:**
- `POSTGRES_PASSWORD: "password123"` → `POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}`
- `POSTGRES_DB` i `POSTGRES_USER` również przeniesione do zmiennych środowiskowych
- `DATABASE_URL` zmienione z hardkodowanych danych na: `postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@db:5432/${POSTGRES_DB}`

Rzeczywiste wartości przechowywane są w pliku `.env`, który jest wykluczony z repozytorium przez `.gitignore`. Plik `.env.example` zawiera przykładowe (puste/zastępcze) wartości.

---

### BŁĄD 4 — Kontener działa jako root

**Problem:** Domyślnie procesy w kontenerze Docker uruchamiają się jako użytkownik `root` (UID 0). W przypadku podatności w aplikacji lub ucieczki z kontenera atakujący uzyskuje uprawnienia roota na hoście lub w sieci kontenerów.

**Poprawka:** Dodano do `backend/Dockerfile` przed instrukcją `CMD`:
```dockerfile
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser
USER appuser
```
Aplikacja działa teraz jako niepriwilejowany użytkownik systemowy `appuser`, co ogranicza możliwy zasięg ataku (principle of least privilege).
