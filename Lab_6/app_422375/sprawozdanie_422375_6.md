Sprawozdanie z Laboratorium 6: Optymalizacja obrazów Docker
Indeks: 422375
Imię: Tadeusz

1. Tabela podsumowująca optymalizacje
Etap	Obraz bazowy	Rozmiar	Co zmieniono
Baseline	python:3.11	1.63 GB	— (stan początkowy)
Po opt. 1	python:3.11	1.62 GB	Zmiana kolejności warstw i usunięcie cache pip.
Po opt. 2	python:3.11	1.62 GB	Dodanie pliku .dockerignore.
Po opt. 3	python:3.11-slim	210 MB	Zmiana obrazu bazowego na wersję slim.
Po opt. 4	python:3.11-slim	194 MB	Wdrożenie multi-stage build.
2. Szczegóły wprowadzonych optymalizacji
Optymalizacja 1: Kolejność warstw (Cache)
Przed zmianą:
Instrukcja kopiowania całego katalogu (COPY . .) znajdowała się przed instrukcją RUN pip install. Jakakolwiek modyfikacja w kodzie (np. w pliku app.py) unieważniała warstwę instalacji pakietów i wymuszała ich ponowne pobieranie.
Po zmianie:

Dockerfile
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py .
Dlaczego to poprawia obraz: Najpierw kopiujemy tylko plik z zależnościami i je instalujemy. Dzięki temu, jeśli modyfikujemy jedynie kod aplikacji (app.py), warstwa z pip install zostaje zaciągnięta z cache, co drastycznie skraca czas budowania. Dodatkowo flaga --no-cache-dir usuwa zbędne pliki tymczasowe po instalatorze pip, redukując nieznacznie wagę obrazu (w naszym przypadku o ok. 10 MB).

Optymalizacja 2: .dockerignore
Przed zmianą: Brak pliku .dockerignore sprawiał, że Docker wysyłał cały kontekst katalogu (wraz z plikami testów, środowisk wirtualnych itp.) do demona budującego. Zmierzył to początkowy rozmiar kontekstu, który w logach wynosił 1.46kB.
Po zmianie: Utworzono plik .dockerignore.
Dlaczego to poprawia obraz: Zignorowano zbędne w kontenerze pliki testowe i konfiguracyjne. W efekcie kontekst przesyłany do daemona zmniejszył się do 63B. Znacznie przyspiesza to proces budowania w dużych repozytoriach (gdzie ucinamy setki megabajtów) oraz zabezpiecza przed przypadkowym skopiowaniem niepotrzebnych lub wrażliwych plików na produkcję.

Optymalizacja 3: Zmiana obrazu bazowego
Przed zmianą: FROM python:3.11 (pełny, ciężki obraz deweloperski ważący około 1 GB, zawierający m.in. narzędzia i kompilatory C).
Po zmianie: FROM python:3.11-slim
Dlaczego to poprawia obraz: Obraz slim został celowo odchudzony z pakietów systemowych, które nie są niezbędne do samego uruchomienia aplikacji. Użycie go poskutkowało diametralnym zmniejszeniem całkowitego rozmiaru obrazu do 210 MB.

Optymalizacja 4: Multi-stage build
Przed zmianą: W obrazie finalnym znajdowały się narzędzia kompilacyjne i środowisko instalacyjne pip, mimo że w środowisku produkcyjnym aplikacja jedynie wykonuje gotowy kod.
Po zmianie: Rozdzielono proces na etap kompilacji (AS builder) oraz lekkie środowisko uruchomieniowe. Użyto flagi --user i przeniesiono poleceniem COPY --from=builder jedynie niezbędne, gotowe biblioteki zainstalowane w katalogu /root/.local.
Dlaczego to poprawia obraz: Finalny kontener uruchomieniowy (ważący teraz zaledwie 194 MB) jest wolny od narzędzi użytych na etapie budowania oraz zależności developerskich. Minimalizuje to wagę ostatecznego obrazu, skraca czasy pobierania i wysyłania do rejestru oraz drastycznie redukuje powierzchnię ataku (security attack surface) na środowisku produkcyjnym.

