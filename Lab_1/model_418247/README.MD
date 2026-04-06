# Sprawozdanie: Laboratorium 1 - Podstawy Git i GitHub
## 1. Konfiguracja klucza SSH
Wygenerowany został klucz ssh aby połączyć się lokalnie z GitHubem bez podawania hasła. Żeby tego dokonać w terminalu wywołana została komenda:

`ssh-keygen -t ed25519 -C "twoj_email@example.com"`

Następnie klucz publiczny `id_ed25519.pub` został skopiowany za pomocą `clip < ~/.ssh/id_ed25519.pub` i dodany w ustawieniach konta GitHub.

## 2. Pobranie repozytorium 
Po skonfigurowaniu klucza ssh pobrane zostało repozytorium na lokalny dysk za pomocą:

`git clone git@github.com:Tomzonkal/DevOps2026.git`


## 3. Utworzenie nowego Brancha
Następnym etapem było stworzenie nowej gałęzi roboczej w celu uniknięcia konfliktów takich jak praca wszystkich na gałęzi głównej i nadpisywanie pracy. Dokonano tego za pomocą komendy:

`git switch -c lab_1/new_branch_418247`

gdzie switch pozwalana nam na przeniesienie się na inną gałąź a `-c` dodatkowo ją tworzy.

![Image-1](./images/Image1.png)

Później sprawdzone zostało czy na pewno dokonano zmiany za pomocą: 

`git branch`

![Image-2](./images/Image2.png)

## 4. Edycja kodu
Wprowadzono nową funkcjonalność do istniejącej aplikacji.
1. Skopiowano folder `model_0000` i zmieniono jego nazwę na `model_418247`.
2. W pliku `config.py` dodano numer indeksu `418247` do listy `id_list`.
   
   ![Image-3](./images/Image3.png)
3. W skopiowanym folderze zmieniono nazwę funkcji w pliku wykonawczym na `run_model_418247`.
   ![Image-4](./images/Image4.png)
4. W głównym pliku `app.py` dodano import nowego modelu oraz utworzono nowy endpoint API:
   `@app.route('/api/model_418247', methods=['POST'])` 
   wywołujący stworzoną wcześniej funkcję.
    ![Image-5](./images/Image5.png)



