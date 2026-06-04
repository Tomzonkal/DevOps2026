# DevOps2026
## ZADANIE 11 KUBERNETES W AZURE (AKS) — ZARZADZANIE KLASTREM PRZEZ TERRAFORM

## CEL LABORATORIUM

Celem laboratorium jest praktyczne poznanie Kubernetes (K8s) jako platformy do uruchamiania konteneryzowanych aplikacji w chmurze. Mamy juz infrastrukture Terraform w Azure (Lab 10) — teraz Terraform posluzy rowniez do zarzadzania zasobami wewnatrz klastra Kubernetes. Zadaniem jest uzupelnienie gotowej konfiguracji Terraform, wdrozenie aplikacji na klaster AKS, zademonstrowanie mechanizmu self-healing (automatyczne odtwarzanie podow) oraz reaktywnego skalowania przez HPA (Horizontal Pod Autoscaler).


## WSTEP TEORETYCZNY

[Kubernetes — podstawowe pojecia](https://kubernetes.io/docs/concepts/overview/)

[Azure Kubernetes Service (AKS) — dokumentacja](https://learn.microsoft.com/en-us/azure/aks/intro-kubernetes)

[Terraform provider kubernetes](https://registry.terraform.io/providers/hashicorp/kubernetes/latest/docs)

[Horizontal Pod Autoscaler](https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/)

[NGINX Ingress Controller](https://kubernetes.github.io/ingress-nginx/)

#### KUBERNETES — KLUCZOWE POJECIA

Kubernetes to platforma do orkiestracji kontenerow. Zamiast uruchamiac kontenery recznie (`docker run`), opisujesz *pozadany stan* klastra w plikach YAML (lub HCL przez Terraform), a K8s stale dazy do jego osiagniecia.

Kluczowe obiekty:

- **Pod** — najmniejsza jednostka K8s. Jeden lub wiecej kontenerow dzielacych siec i storage.
- **Deployment** — opisuje ile replik Poda ma dzialac i jak je aktualizowac (rolling update). Jezeli Pod padnie, Deployment automatycznie go odtworzy.
- **Service** — stabilny adres sieciowy dla zestawu Podow (Pody maja ulotne IP, Service — nie).
- **ConfigMap** — konfiguracja aplikacji jako klucz-wartosc. Oddzielona od obrazu kontenera.
- **Secret** — jak ConfigMap, ale dla danych wrazliwych (hasla, tokeny). Przechowywany zakodowany.
- **Ingress** — reguly routingu HTTP/HTTPS z zewnatrz klastra do wewnetrznych Service.
- **HPA** — automatycznie zmienia liczbe replik Deploymentu na podstawie metryk (CPU, RAM).

#### DLACZEGO K8S ZAMIAST DOCKER COMPOSE?

```
docker run myapp   # Jezeli proces padnie — kontener nie wroci bez restartu manualnego
                   # Skalowanie = recznie uruchamiasz kolejne instancje
                   # Aktualizacja = downtime podczas zmiany kontenera

kubectl apply      # Deployment gwarantuje N dzialajacych replik w kazdej chwili
                   # HPA sam dodaje repliki pod obciazeniem
                   # Rolling update = zero downtime
```

#### UWAGA O KOSZTACH

Standard_B2s (2 vCPU, 4 GB RAM) kosztuje ok. 0,048 USD/godzine za wezel. Klaster 2-wezlowy przez 3 godziny to ok. 0,30 USD. Pamietaj o obowiazkowym `terraform destroy` na koncu laboratorium!


## Aby wykonac laboratorium, nalezy wykonac nastepujace kroki:

### 1 Przygotowanie srodowiska

- 1.1 Upewnij sie ze masz zainstalowane:

```bash
# Terraform (min. 1.5)
terraform version

# Azure CLI
az version

# kubectl
kubectl version --client

```

Instalacja kubectl (jesli brak):
```bash
# Linux
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
chmod +x kubectl && sudo mv kubectl /usr/local/bin/

# macOS
brew install kubectl
```


- 1.2 Stworz branch roboczy:

```bash
git switch -c lab11/nrIndeksu
git push -u origin lab11/nrIndeksu
```

- 1.3 Zaloguj sie do Azure:

```bash
az login
az account show  # sprawdz ze masz aktywna subskrypcje
```

- 1.4 Skopiuj przyklad konfiguracji:

```bash
cd Lab_11/terraform
cp terraform.tfvars.example terraform.tfvars
```

Edytuj `terraform.tfvars` — ustaw swoj prefiks (numer indeksu):
```hcl
prefix = "devops123456"   # tylko male litery i cyfry, max 12 znakow
```

Sprawdz: `cat terraform.tfvars` — plik istnieje i zawiera Twoj prefiks.

---

### 2 Konfiguracja tozsamosci dla GitHub Actions (jednorazowo)

GitHub Actions musi miec uprawnienia do tworzenia zasobow w Azure. Zamiast przechowywac haslo (`client_secret`) w GHA Secrets, uzywamy **Workload Identity Federation (OIDC)** — GHA i Azure wymieniaja sie krotkozyciowymi tokenami, bez zadnych hasel w repozytorium.

- 2.1 Stworz tozsamosc (App Registration) w Azure:

```bash
cd Lab_11/terraform-gha-identity
cp terraform.tfvars.example terraform.tfvars
```

Uzupelnij `terraform.tfvars`:
```hcl
github_org    = "TwojaNazwaUzytkownikaGitHub"
github_repo   = "DevOps2026"
github_branch = "lab11/nrIndeksu"
```

```bash
terraform init
terraform apply
```

- 2.2 Stworz srodowisko o nazwie rownej Twojemu numerowi indeksu w Twoim forku:

`Settings → Environments → New environment` → wpisz `<nrIndeksu>` (np. `123456`) → kliknij **Configure environment**

Workflow automatycznie wyciaga numer indeksu z nazwy brancha (`lab11/123456` → `123456`)
i uzywa go jako nazwy srodowiska — nie musisz nic konfigurowac w samym workflow.

- 2.3 Dodaj sekrety do srodowiska `<nrIndeksu>` (nie do repozytorium):

`Settings → Environments → <nrIndeksu> → Environment secrets → Add secret`

| Secret name | Wartosc z terraform output |
|-------------|---------------------------|
| `AZURE_CLIENT_ID` | `terraform output -raw AZURE_CLIENT_ID` |
| `AZURE_TENANT_ID` | `terraform output -raw AZURE_TENANT_ID` |
| `AZURE_SUBSCRIPTION_ID` | `terraform output -raw AZURE_SUBSCRIPTION_ID` |

- 2.4 Dodaj zmienna do srodowiska `<nrIndeksu>`:

`Settings → Environments → <nrIndeksu> → Environment variables → Add variable`

| Variable name | Wartosc |
|---------------|---------|
| `TF_PREFIX` | Twoj prefiks (ten sam co `prefix` w terraform.tfvars, np. `devops123456`) |

Sprawdz: Przejdz do `Actions` w Twoim forku → wybierz workflow **Terraform Lab 11 — AKS** (z `.github/workflows/lab11-terraform.yml`) → kliknij **Run workflow** → wybierz swoj branch `lab11/<nrIndeksu>` i akcje `plan` → job `Plan` powinien skonczyc sie sukcesem.

```bash
cd ..  # wróc do Lab_11/terraform
```

---

### 3 Stworzenie klastra AKS

- 3.1 Zainicjuj Terraform:

```bash
terraform init
```

Sprawdz: komenda konczy sie `Terraform has been successfully initialized!`

- 3.2 Stworz klaster AKS (tylko):

```bash
terraform apply -target=azurerm_resource_group.rg \
                -target=azurerm_kubernetes_cluster.aks
```

Zatwierdz wpisujac `yes`. Czas oczekiwania: ok. 5-8 minut.

Sprawdz: `terraform output aks_name` — zwraca nazwe klastra.

- 3.3 Pobierz kubeconfig — dodaj klaster do lokalnego `~/.kube/config`:

```bash
az aks get-credentials \
  --resource-group $(terraform output -raw resource_group_name) \
  --name $(terraform output -raw aks_name)
```

Sprawdz:
```bash
kubectl get nodes
# Oczekiwany wynik: 2 wezly w stanie Ready
# Jesli wezly pokazuja NotReady — poczekaj 2-3 minuty i powtor komende.
# Azure startuje wezly asynchronicznie po stworzeniu klastra.
```

---

### 4 Uzupelnienie konfiguracji aplikacji

Otwierz plik `terraform/app.tf` i uzupelnij wszystkie miejsca oznaczone `← TODO`:

- **replicas** — liczba startowych replik (1-3)
- **image** — obraz Docker aplikacji. Uzyj obrazu `stefanprodan/podinfo` z tagu `6.6.0`
- **cpu (requests)** — minimalne zasoby CPU. Uzyj wartosci `50m` (50 millicores)
- **cpu (limits)** — maksymalne zasoby CPU. Uzyj wartosci `200m`

> **Dlaczego resources.requests.cpu jest obowiazkowe?**
> HPA mierzy zuzycie CPU jako procent wartosci `requests`. Bez tego pola
> HPA nie wie od czego liczyc procenty i pokazuje `<unknown>/50%` — nie skaluje.

Nastepnie otwierz `terraform/config.tf` i uzupelnij:

- **PODINFO_UI_MESSAGE** — dowolna wiadomosc (np. `"Czesc z AGH DevOps 2026!"`)
- **PODINFO_LOG_LEVEL** — poziom logowania (`info` lub `debug`)
- **password** — dowolne haslo (plain text, min. 8 znakow)

Przed przejsciem do nastepnego kroku sprawdz poprawnosc skladni HCL:
```bash
terraform validate
# Oczekiwany wynik: Success! The configuration is valid.
# Jesli sa bledy (np. "Invalid expression") — popraw je zanim uruchomisz apply.
```

---

### 5 Wdrozenie aplikacji

- 5.1 Wdorz aplikacje:

```bash
terraform apply
```

Zatwierdz wpisujac `yes`. Czas: ok. 2-3 minut.

- 5.2 Sprawdz ze Pody dzialaja:

```bash
kubectl get pods
# Oczekiwany wynik: podinfo-<hash> w stanie Running
```

- 5.3 Pobierz publiczny IP aplikacji i sprawdz ze odpowiada:

```bash
terraform output app_ip
# Jesli pokazuje "Jeszcze niedostepny" — poczekaj 1-2 minuty (Azure tworzy Load Balancer)
# i uruchom ponownie: terraform output app_ip

# Gdy IP jest juz dostepne:
curl http://$(terraform output -raw app_ip)/
# Oczekiwany wynik: JSON z polem "hostname" i "message"
```

- 5.4 Sprawdz ze HPA zostal stworzony:

```bash
kubectl get hpa
# Kolumna TARGETS pokazuje format: CURRENT/TARGET
# Przyklad: "5%/50%" oznacza ze aktualnie zuzywa 5% CPU, a prog skalowania to 50%
# UWAGA: Przez ok. 2 minuty po apply moze pokazywac "<unknown>/50%".
# To normalne — Metrics Server potrzebuje chwili na pierwsze odczyty.
```

Sprawdz (po 2-3 minutach): `kubectl get hpa` — kolumna TARGETS pokazuje wartosc procentowa, nie `<unknown>`.

---

### 6 Self-healing — automatyczne odtwarzanie Podow

Kubernetes gwarantuje ze zawsze dziala zdefiniowana liczba replik Deploymentu.
Sprawdz to eksperymentalnie:

- 7.1 W jednym terminalu obserwuj Pody w czasie rzeczywistym:

```bash
kubectl get pods -w
```

- 7.2 W drugim terminalu usun jeden Pod:

```bash
# Pobierz nazwe Poda
kubectl get pods -l app=podinfo

# Usun go
kubectl delete pod <NAZWA-PODA>
```

- 7.3 Obserwuj co dzieje sie w pierwszym terminalu.

Sprawdz: w ciagu ok. 10-20 sekund pojawia sie nowy Pod w stanie `ContainerCreating`, a nastepnie `Running`. Usuniety Pod znika. Deployment przywraca wymagana liczbe replik automatycznie.

> **Aha moment:** Nie uruchamiasz "kontenera" — uruchamiasz "pozadany stan".
> Deployment mowi: "chce N dzialajacych replik podinfo". K8s stale sprawdza
> czy ten stan jest osiagniety i koryguje odchylenia.

---

### 8 HPA — skalowanie reaktywne

- 8.1 Otwierz `terraform/hpa.tf` i uzupelnij wszystkie TODO:

```
min_replicas        = 1
max_replicas        = 5
average_utilization = 50
```

Zastosuj:
```bash
terraform apply
```

- 8.2 Uruchom stress test w jednym terminalu:

```bash
cd Lab_11
chmod +x stress.sh

APP_IP=$(cd terraform && terraform output -raw app_ip)
./stress.sh "http://${APP_IP}"
```

- 8.3 W drugim terminalu obserwuj HPA i Pody:

```bash
# W jednym oknie:
kubectl get hpa -w

# W drugim oknie:
kubectl get pods -w
```

Sprawdz po ok. 2-3 minutach:
- `kubectl get hpa` — kolumna REPLICAS wzrosla powyzej wartosci startowej
- `kubectl get pods -l app=podinfo` — widocznych jest wiecej niz 1 Pod

- 8.4 Zatrzymaj stress test (Ctrl+C) i obserwuj scale-down (moze zajac ok. 5 minut — to celowe zachowanie K8s zapobiegajace "trzepotaniu").

- 8.5 Zweryfikuj rozklad ruchu miedzy Podami podczas dzialania stress testu:

```bash
# Uruchom podczas stress testu:
APP_IP=$(cd terraform && terraform output -raw app_ip)
for i in $(seq 1 10); do
  curl -s "http://${APP_IP}/" | python3 -c "import sys,json; print(json.load(sys.stdin)['hostname'])"
done
```

Sprawdz: rozne Pody obslugiway kolejne requesty (rozne nazwy hostname w odpowiedziach).

---

### 9 Czyszczenie infrastruktury (OBOWIAZKOWE)

```bash
terraform destroy
```

Zatwierdz wpisujac `yes`. Czas: ok. 5-10 minut.

Sprawdz:
```bash
az group list --query "[?name=='<PREFIX>-rg']" -o table
# Oczekiwany wynik: pusta lista — resource group usunieta
```

---

## Typowe bledy

**1. `Error: context "<prefix>-aks" does not exist`**

Terraform nie moze polaczyc sie z klastrem bo kubeconfig nie zostal pobrany.
Wykonaj:
```bash
az aks get-credentials --resource-group <PREFIX>-rg --name <PREFIX>-aks
kubectl get nodes  # weryfikacja
```
Nastepnie ponow `terraform apply`.

**2. `kubectl get hpa` pokazuje `<unknown>/50%` — HPA nie skaluje**

Przyczyna: brak `resources.requests.cpu` w Deployment, lub Metrics Server nie zdazyl zebrach pierwszych danych.

Sprawdz czy requests CPU jest ustawiony:
```bash
kubectl describe pod -l app=podinfo | grep -A3 "Limits\|Requests"
```
Jezeli widzisz puste Requests — uzupelnij `cpu` w `app.tf` i wykonaj `terraform apply`.
Jezeli Requests sa ustawione — poczekaj 2-3 minuty na pierwsze odczyty Metrics Server.

**3. `terraform output app_ip` zwraca "Jeszcze niedostepny" po dlugim czasie**

Azure tworzy Load Balancer asynchronicznie. Zazwyczaj zajmuje to 1-3 minuty.
Sprawdz status serwisu bezposrednio:
```bash
kubectl get svc podinfo
# Kolumna EXTERNAL-IP: jesli pokazuje <pending> — poczekaj i powtor
# Jesli po 5 minutach nadal <pending>:
kubectl describe svc podinfo  # sprawdz Events na dole output
```
Najczestszy powod: subskrypcja Azure ma limit publicznych IP (sprawdz w Azure Portal → Quotas).

**5. Po `terraform destroy` nadal widac zasoby w Azure Portal**

Azure usuwa zasoby asynchronicznie. Poczekaj 5-10 minut i odswiez portal.
Mozesz sprawdzic status: `az group show --name <PREFIX>-rg --query properties.provisioningState`
Jezeli pokazuje `Deleting` — trwa usuwanie. Jezeli `Deleted` lub blad `ResourceGroupNotFound` — zakonczone.


## Zaliczenie laboratoriow

Wypchnij zmiany na swoj fork i otworz Pull Request na branch `lab11/<nrIndeksu>`.

```bash
git add Lab_11/terraform/*.tf Lab_11/terraform/terraform.tfvars
git commit -m "lab11: K8s na AKS — Deployment, ConfigMap, Ingress, HPA"
git push origin lab11/nrIndeksu
```

Do PR dolacz:
1. Screenshot z `kubectl get pods` pokazujacy Running pody
2. Screenshot z `kubectl get hpa` pokazujacy TARGETS z wartoscia procentowa (nie `<unknown>`)
3. Screenshot z `kubectl get pods -w` podczas self-healing (moment usuwania i odtwarzania poda)
4. Screenshot lub log z `kubectl get hpa -w` podczas stress testu pokazujacy wzrost REPLICAS
5. Wynik `terraform output get_credentials_command` (jako tekst w opisie PR)

**Kryteria oceny:**

| Kryterium | Punkty |
|-----------|--------|
| `terraform apply` konczy sie bez bledow | 20 |
| Aplikacja dostepna przez Ingress (`curl` zwraca JSON) | 20 |
| Self-healing udokumentowany (screenshot kubectl get pods -w) | 20 |
| HPA skaluje do 2+ replik podczas stress testu | 20 |
| `terraform destroy` wykonany (brak resource group w Azure) | 10 |
| **Bonus:** W logach widac rozne hostname podow podczas stress testu | 10 |

**Tematy do rozwinięcia (dla chętnych):**
- Dodaj PersistentVolume do podinfo (przechowywanie sesji miedzy restartami)
- Skonfiguruj Namespace i przenieś aplikacje do dedykowanego namespace
- Dodaj NetworkPolicy ograniczajaca ruch miedzy podami
