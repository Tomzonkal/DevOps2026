# Sprawozdanie z laboratorium 1

## 1. Generowanie klucza SSH i dodanie go do konta.

Użyłem historii terminala (komenda `history`), aby odnaleźć wywołanie polecenia generującego klucz SSH, które wykonałem wcześniej. 

Poniższy zrzut ekranu prezentuje odnaleziony ciąg komend.

> **Uwaga:** Widoczne na zrzucie ekranu wywołanie `whoami` służyło jedynie potwierdzeniu mojej tożsamości w momencie przeszukiwania historii terminala.

<img src="keygen-ss.png" width="600">

Następnie wybrałem domyślnie ustawioną lokalizację, gdzie został zapisany klucz oraz podałem swój passphrase.

W celu podłączenia klucza do konta na GitHubie wszedłem w Settings -> SSH and GPG keys -> New SSH key. Tutaj podałem swój klucz i jego nazwę.

<img src="ssh-ss.png" width="600">

## 2. Pobranie repo i utworzenie gałęzi roboczej.

Wykorzystując komendę `git clone git@github.com:Tomzonkal/DevOps2026.git` pobrałem repo na lokalną maszynę.

Powyższy wycinek z dziennika `git reflog`  potwierdza poprawne pobranie repozytorium na dysk za pomocą komendy `git clone`:

<img src="reflog-1.png" width="600">

Następnie utworzyłem gałąź roboczą wykorzystując komendę `git switch -c lab_1/new_branch_422973`. Podczas tworzenie brancha następują dwie rzeczy: po pierwsze tworzona jest gałąz, a po drugie wskaznik HEAD od razu na nią wskazuje.
Osobiście jestem przyzwyczajony do `git checkout -b <nazwa>` ale w dokumentacji wyczytałem, ze jest to tylko zmiana standardu.

<img src="image.png" width="600">
