# User-Assigned Managed Identity — tozsamosc dla GitHub Actions.
#
# W odroznieniu od App Registration (azuread_application), Managed Identity
# jest zwyklym zasobem Azure ARM — nie wymaga zadnych uprawnien w Entra ID,
# wystarczy rola Contributor na subskrypcji lub resource group.
#
# Jak dziala Workload Identity Federation z UAMI:
# 1. GitHub Actions generuje krotkozyciowy token JWT podpisany przez GitHub OIDC
# 2. Azure weryfikuje podpis i sprawdza czy "subject" pasuje do federated credential
# 3. Azure wydaje token dostepowy dla tej tożsamości — bez hasel w GHA Secrets
#
# Dokumentacja: https://learn.microsoft.com/en-us/azure/active-directory/workload-identities/workload-identity-federation

resource "azurerm_user_assigned_identity" "gha" {
  name                = "${var.prefix}-gha-identity"
  resource_group_name = azurerm_resource_group.gha.name
  location            = azurerm_resource_group.gha.location
}

# Federated credential dla srodowiska GitHub Actions.
# Subject format dla environment: repo:<org>/<repo>:environment:<env>
#
# Uzywamy environment zamiast branch — sekrety sa przechowywane w srodowisku
# i workflow musi je deklarowac przez "environment: lab11". Daje to lepsza
# kontrole: mozna dodac protection rules (np. wymagana akceptacja przed deploy).
resource "azurerm_federated_identity_credential" "gha_environment" {
  name                = "gha-lab11-environment"
  resource_group_name = azurerm_resource_group.gha.name
  parent_id           = azurerm_user_assigned_identity.gha.id
  issuer              = "https://token.actions.githubusercontent.com"
  subject             = "repo:${var.github_org}/${var.github_repo}:environment:${var.github_environment}"
  audience            = ["api://AzureADTokenExchange"]
}
