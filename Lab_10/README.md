# DevOps2026
## ZADANIE 10 TERRAFORM W AZURE — INFRASTRUKTURA JAKO KOD

Cel laboratoriow.
Celem laboratoriow jest praktyczne poznanie narzedzia Terraform do zarzadzania infrastruktura chmurowa w Azure. Student tworzy maszyne wirtualna, Azure Container Registry oraz Storage Account, konfiguruje polaczenia sieciowe (service endpoint, private endpoint) i przeprowadza caly cykl: provisioning przez pipeline CI/CD z recznym zatwierdzeniem, budowanie obrazu Docker na VM i wypchnięcie go do prywatnego rejestru, a na koncu obowiazkowe usuniecie infrastruktury aby nie wyczerpac kredytow Azure Student.


## WSTEP TEORETYCZNY ##

[Terraform — Getting Started with Azure](https://developer.hashicorp.com/terraform/tutorials/azure-get-started)

[Dokumentacja providera azurerm](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs)

[Service Endpoints w Azure Virtual Network](https://learn.microsoft.com/en-us/azure/virtual-network/virtual-network-service-endpoints-overview)

[Private Endpoints w Azure](https://learn.microsoft.com/en-us/azure/private-link/private-endpoint-overview)

[Managed Identity w Azure](https://learn.microsoft.com/en-us/azure/active-directory/managed-identities-azure-resources/overview)

[GitHub Actions — Environments i protection rules](https://docs.github.com/en/actions/deployment/targeting-different-environments/using-environments-for-deployment)

#### INFRASTRUKTURA JAKO KOD (IaC) ####

Terraform to narzedzie do definiowania infrastruktury w jezyku deklaratywnym HCL (HashiCorp Configuration Language). Zamiast klikac w portalu Azure, definiujesz stan docelowy infrastruktury w plikach `.tf`, a Terraform oblicza niezbedne zmiany i je stosuje.

Kluczowe pojecia:
- **provider** — wtyczka do komunikacji z danym dostawca chmury (tu: `azurerm`)
- **resource** — pojedynczy zasob infrastruktury (VM, siec, rejestr)
- **variable** — parametr wejsciowy konfigurowalny bez zmiany kodu
- **output** — wartosc wyjsciowa po apply (np. publiczny adres IP VM)
- **state** — plik `.tfstate` przechowujacy aktualny stan infrastruktury

Podstawowy cykl:
```
terraform init     # pobiera provider, inicjalizuje katalog roboczy
terraform plan     # pokazuje co zostanie zmienione (BEZ modyfikacji!)
terraform apply    # aplikuje zmiany
terraform destroy  # niszczy cala infrastrukture
```

#### SERVICE ENDPOINT VS PRIVATE ENDPOINT ####

**Service Endpoint** optymalizuje routing ruchu z VM do uslug Azure — zamiast wychodzic przez publiczny internet, ruch plynie secia szkieletowa Microsoft. Usluga nadal ma publiczny adres IP, ale mozna ograniczyc dostep tylko do wybranych podsieci.

**Private Endpoint** tworzy prywatny interfejs sieciowy w Twojej VNet z dedykowanym prywatnym adresem IP. Usluga (tu: ACR) staje sie dostepna pod prywatnym IP i mozna wylaczyl jej publiczny dostep. VM komunikuje sie z ACR wylacznie przez VNet, ruch nigdy nie wychodzi do internetu.

#### MANAGED IDENTITY ####

System-assigned Managed Identity to automatycznie tworzona tozsamosc Azure dla VM. Zamiast przechowywa hasla lub klucze API, VM uwierzytelnia sie w uslugach Azure (ACR, Storage) uzywajac swojej tozsamosci. Wystarczy przypisac roli na zasobie — i VM ma dostep bez zadnych hasel w kodzie.

#### UWAGA O KOSZTACH ####

ACR w SKU Premium kosztuje ok. 0,65 USD/dzien. VM Standard_B1s kosztuje ok. 0,012 USD/godzine. Calkowity koszt laboratorium (2-3 godziny) to ok. 0,20-0,30 USD przy dokladnym wykonaniu kroku `terraform destroy` na koncu. Jesli zapomnisz zniszczyc infrastrukture, koszty beda narastac. Sprawdz swoje saldo w Azure Portal przed i po laboratorium.


## Aby wykonac laboratorium, nalezy wykonac nastepujace kroki: ##

### 1 Przygotowanie srodowiska lokalnego

- 1.1 Zainstaluj Terraform (min. wersja 1.5):

```bash
# Linux — przez tfenv (zalecane)
git clone --depth=1 https://github.com/tfutils/tfenv.git ~/.tfenv
echo 'export PATH="$HOME/.tfenv/bin:$PATH"' >> ~/.bashrc && source ~/.bashrc
tfenv install 1.9.0 && tfenv use 1.9.0

# macOS
brew install tfenv && tfenv install 1.9.0 && tfenv use 1.9.0
```

- 1.2 Zainstaluj Azure CLI jesli nie masz:

```bash
# Linux
curl -sL https://aka.ms/InstallAzureCLIdeb | sudo bash

# macOS
brew install azure-cli
```

- 1.3 Sforkuj repozytorium kursu na swoje konto GitHub: przejdz do DevOps2026 i kliknij przycisk **Fork** w prawym gornym rogu.

- 1.4 Sklonuj swoj fork lokalnie:

```bash
git clone git@github.com:<TWOJ_GITHUB_LOGIN>/DevOps2026.git
cd DevOps2026
```

- 1.5 Stworz branch roboczy:

```bash
git switch -c lab10/nrIndeksu
git push -u origin lab10/nrIndeksu
```

- 1.6 Wygeneruj klucz SSH dla tej VM (lub uzyj istniejacego):

```bash
ssh-keygen -t rsa -b 4096 -C "devops-lab10" -f ~/.ssh/id_lab10 -N ""
cat ~/.ssh/id_lab10.pub   # skopiuj te wartosc — bedzie potrzebna w nastepnym kroku
```

**Sprawdz:** `terraform version` zwraca wersje >= 1.5 oraz `az version` zwraca zainstalowana wersje CLI.

### 2 Logowanie do Azure

- 2.1 Zaloguj sie do Azure:

```bash
az login
az account show --query id -o tsv   # zapamietaj Subscription ID
```

**Sprawdz:** `az account show` zwraca Twoja subskrypcje.

### 3 Konfiguracja workflow

- 3.1 Skopiuj szablon workflow do katalogu `.github/workflows/`:

```bash
cp Lab_10/terraform.yml .github/workflows/lab10_nrIndeksu.yml
```

**Sprawdz:** Plik `.github/workflows/lab10_nrIndeksu.yml` istnieje w repozytorium.

### 4 Uzupelnienie szkieletu — service endpoint dla Storage Account

- 4.1 Otworz plik `Lab_10/terraform/network.tf`. Znajdz blok `azurerm_subnet` i uzupelnij pole `service_endpoints` tak, aby subnet miala zarejestrowany service endpoint dla Azure Storage.

Dokumentacja: [Service endpoints — property service_endpoints](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/subnet#service_endpoints)

Poprawny wpis wygada tak:
```hcl
service_endpoints = ["Microsoft.Storage"]
```

**Sprawdz:** `grep -n "TODO" Lab_10/terraform/network.tf` — powinno zwrocic brak wynikow.

### 5 Uzupelnienie szkieletu — network rules dla Storage Account

- 5.1 Otworz plik `Lab_10/terraform/storage.tf`. Znajdz blok `network_rules` i uzupelnij pole `virtual_network_subnet_ids` wstawiajac referencje do ID subnetu.

Wskazowka: uzupelnij:
```hcl
virtual_network_subnet_ids = [azurerm_subnet.subnet.id]
```

Dzieki temu Storage Account rejestruje subnet jako zaufana siec. Ruch z VM bedzie optymalnie kierowany przez Microsoft backbone.

**Sprawdz:** `grep -n "TODO" Lab_10/terraform/storage.tf` — powinno zwrocic brak wynikow.

### 6 Uzupelnienie szkieletu — private endpoint i DNS dla ACR

- 6.1 Otworz plik `Lab_10/terraform/acr.tf`. Sa tam trzy miejsca z komentarzem `← TODO`:

**a) `virtual_network_id`** w bloku `azurerm_private_dns_zone_virtual_network_link`:
```hcl
virtual_network_id = azurerm_virtual_network.vnet.id
```
Bez tego linku VM nie bedzie mogla rozwiazywac nazwy ACR na prywatny IP.

**b) `subresource_names`** w bloku `private_service_connection`:
```hcl
subresource_names = ["registry"]
```
To jest jedyna dostepna subresource dla Azure Container Registry.

**c) `private_dns_zone_ids`** w bloku `private_dns_zone_group`:
```hcl
private_dns_zone_ids = [azurerm_private_dns_zone.acr_dns.id]
```
Terraform automatycznie utworzy rekord A wskazujacy na prywatny IP private endpoint.

**Sprawdz:** `grep -n "TODO" Lab_10/terraform/acr.tf` — powinno zwrocic brak wynikow.

### 7 Uzupelnienie szkieletu — uprawnienia VM do ACR

- 7.1 Otworz plik `Lab_10/terraform/vm.tf`. Znajdz blok `azurerm_role_assignment` o nazwie `vm_acr_push` i uzupelnij:

**a) `role_definition_name`** — wybierz minimalna role ktora pozwala VM wykonac `docker push`:
```hcl
role_definition_name = "AcrPush"
```

**b) `principal_id`** — ID managed identity VM (automatycznie przypisanej przy tworzeniu VM):
```hcl
principal_id = azurerm_linux_virtual_machine.vm.identity[0].principal_id
```

**Sprawdz:** `grep -n "TODO" Lab_10/terraform/vm.tf` — powinno zwrocic brak wynikow.

### 8 Weryfikacja lokalna i commit

- 8.1 Skopiuj plik konfiguracyjny i uzupelnij go:

```bash
cp Lab_10/terraform/terraform.tfvars.example Lab_10/terraform/terraform.tfvars
```

Edytuj `Lab_10/terraform/terraform.tfvars`:
```hcl
prefix         = "devopsnrIndeksu"   # tylko male litery i cyfry, max 12 znakow
location       = "polandcentral"
admin_username = "azureuser"
ssh_public_key = "ssh-ed25519 AAAA..."  # zawartosc ~/.ssh/id_lab10.pub
```

- 8.2 Zainicjalizuj i zwaliduj konfiguracje:

```bash
cd Lab_10/terraform
terraform init
terraform validate
```

**Sprawdz:** `terraform validate` zwraca `The configuration is valid.`

- 8.3 Wypchnij zmiany (CI uruchomi validate):

```bash
cd <katalog-glowny-repo>
git add Lab_10/terraform/ .github/workflows/lab10_nrIndeksu.yml
git add Lab_10/terraform/.terraform.lock.hcl
git commit -m "lab10: terraform infrastructure + pipeline"
git push
```

**Sprawdz:** Job `terraform-validate` w zakladce **Actions** jest zielony.

### 9 Uruchomienie infrastruktury lokalnie

Poniewaz plan i apply wymagaja polaczenia z Azure, uruchamiaj je lokalnie po `az login`.

- 9.1 Uruchom plan aby zobaczyc co zostanie stworzone:

```bash
cd Lab_10/terraform
terraform plan -var-file=terraform.tfvars
```

Przeczytaj output — powinny byc widoczne zasoby: VM, VNet, NSG, Storage Account, ACR, Private Endpoint, Private DNS Zone, role assignments.

- 9.2 Jesli plan wyglada poprawnie, zastosuj infrastrukture:

```bash
terraform apply -var-file=terraform.tfvars
```

Wpisz `yes` gdy Terraform zapyta o potwierdzenie. Operacja zajmuje 5-10 minut.

**Sprawdz:** `terraform apply` konczy sie komunikatem `Apply complete!` bez bledow.

### 10 Weryfikacja infrastruktury

- 10.1 Sprawdz stworzone zasoby przez Azure CLI (wpisz swoj prefiks):

```bash
az resource list --resource-group devopsnrIndeksu-rg --output table
```

Powinny byc widoczne m.in.: `virtualMachines`, `virtualNetworks`, `storageAccounts`, `registries`, `privateEndpoints`.

- 10.2 Pobierz publiczny IP VM z outputs Terraform:

```bash
cd Lab_10/terraform
terraform output vm_public_ip
# lub gotowa komenda SSH:
terraform output ssh_command
```

- 10.3 Polacz sie z VM:

```bash
ssh -i ~/.ssh/id_lab10 azureuser@<VM_PUBLIC_IP>
```

- 10.4 Na VM poczekaj az cloud-init skonczy instalacje pakietow (Docker + Azure CLI):

```bash
cloud-init status --wait
# Oczekiwany wynik: status: done
```

Moze to zajac 3-5 minut od momentu uruchomienia VM.

**Sprawdz:** `docker --version` i `az version` zwracaja zainstalowane wersje.

### 11 Build i push obrazu Docker

> Wszystkie komendy w tym kroku uruchamiaj na VM przez SSH.

- 11.1 Zaloguj sie do Azure uzywajac managed identity VM:

```bash
az login --identity
```

Brak hasla, brak kodu — VM uwierzytelnia sie automatycznie przez swoja tozsamosc IAM.

- 11.2 Zweryfikuj polaczenie z ACR przez private endpoint:

```bash
# Sprawdz czy nazwa ACR rozwiazuje sie na prywatny IP (np. 10.0.1.x)
nslookup devopsnrIndeksuacr.azurecr.io
```

Adres IP w odpowiedzi powinien byc z zakresu `10.0.x.x` (prywatny), a nie publiczny. To potwierdzenie ze private endpoint dziala.

- 11.3 Pobierz Dockerfile z Storage Account:

```bash
SA_NAME="devopsnrIndeksusa"
az storage blob download \
  --account-name $SA_NAME \
  --container-name dockerfiles \
  --name Dockerfile \
  --file ~/Dockerfile \
  --auth-mode login
cat ~/Dockerfile
```

- 11.4 Zaloguj sie do ACR uzywajac managed identity:

```bash
ACR_NAME="devopsnrIndeksuacr"
az acr login --name $ACR_NAME
```

- 11.5 Zbuduj obraz i wypchaj do ACR:

```bash
docker build -t ${ACR_NAME}.azurecr.io/lab10-app:v1 ~/
docker push ${ACR_NAME}.azurecr.io/lab10-app:v1
```

- 11.6 Zweryfikuj ze obraz jest w rejestrze:

```bash
az acr repository list --name $ACR_NAME --output table
az acr repository show-tags --name $ACR_NAME --repository lab10-app --output table
```

**Sprawdz:** `az acr repository list` pokazuje `lab10-app`. `az acr repository show-tags` pokazuje tag `v1`.

### 12 WAZNE: Usuniecie infrastruktury

> **Azure Student daje ograniczona kwote kredytow. Pozostawienie infrastruktury bedzie generowac koszty. Po zakonczeniu laboratorium MUSISZ zniszczyc wszystkie zasoby.**

- 12.1 Wyjdz z VM i uruchom destroy lokalnie:

```bash
exit   # wyjdz z SSH

cd Lab_10/terraform

# Ustaw zmienne srodowiskowe z wartosciami Twojego Service Principal
export ARM_CLIENT_ID="<appId>"
export ARM_CLIENT_SECRET="<password>"
export ARM_SUBSCRIPTION_ID="<subscription_id>"
export ARM_TENANT_ID="<tenant>"

terraform destroy -var-file=terraform.tfvars
```

Wpisz `yes` gdy Terraform zapyta o potwierdzenie. Operacja zajmuje ok. 5 minut.

- 12.2 Zweryfikuj ze zasoby zostaly usuniete:

```bash
az resource list --resource-group devopsnrIndeksu-rg --output table
```

Wynik powinien byc pusty lub zakonczyc sie bledem `ResourceGroupNotFound` — oba sa poprawne.

**Sprawdz:** `az resource list --resource-group devopsnrIndeksu-rg` zwraca pusta liste lub blad `ResourceGroupNotFound`.


### Typowe bledy

- **`Error: building AzureRM Client: could not configure AzureRM Provider`** — sprawdz czy wszystkie 4 sekrety `ARM_*` sa poprawnie ustawione w forku (GitHub Settings → Secrets). Czesto blad wynika z wklejenia wartosci z bialymi znakami na poczatku/koncu.

- **`Error: A resource with the ID already exists`** — poprzednie `terraform apply` nie dokonczylo sie lub zasoby z tym samym prefiksem istnieja juz z innego uruchomienia. Sprawdz portal Azure i recznie usun resource group: `az group delete --name devopsnrIndeksu-rg --yes`.

- **`Error: creating/updating Private Endpoint: waiting for creation`** — `subresource_names` sa bledne lub puste w `acr.tf`. Sprawdz czy `subresource_names = ["registry"]`.

- **`Error: docker: unauthorized: authentication required`** — rola `AcrPush` nie zostala poprawnie przypisana. Sprawdz czy `principal_id` w `vm_acr_push` wskazuje na `azurerm_linux_virtual_machine.vm.identity[0].principal_id`. Propagacja uprawnien Azure moze zajac 1-2 minuty po apply.

- **`dial tcp: lookup devopsnrIndeksuacr.azurecr.io: no such host`** — DNS nie rozwiazuje nazwy ACR. Sprawdz czy `virtual_network_id` w `azurerm_private_dns_zone_virtual_network_link` jest uzupelniony i czy `private_dns_zone_ids` w bloku `private_dns_zone_group` nie jest pusta lista.

- **Brak SSH do VM** — sprawdz czy NSG ma regule `AllowSSH` (port 22). Sprawdz czy klucz SSH w `terraform.tfvars` to klucz PUBLICZNY (`ssh-ed25519 AAAA...`), nie prywatny.

- **`cloud-init: status: running`** — VM wciaz instaluje pakiety. Uruchom ponownie `cloud-init status --wait` i poczekaj kilka minut.


### Zaliczenie laboratoriow

- Job `terraform-validate` w forku studenta — zielony w zakladce **Actions**
- Obraz `lab10-app:v1` widoczny w ACR (`az acr repository show-tags --name ... --repository lab10-app`)
- Infrastruktura zniszczona (`terraform destroy`) — brak zasobow w subskrypcji po zakonczeniu laboratorium
