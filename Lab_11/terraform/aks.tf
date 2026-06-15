# Klaster AKS — gotowy do uzycia, nie wymaga zmian.
# Standard_B2s: 2 vCPU, 4 GB RAM — wystarczajacy dla laboratorium.
# Czas tworzenia klastra: ok. 5-8 minut.

resource "azurerm_kubernetes_cluster" "aks" {
  name                = "${var.prefix}-aks"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  dns_prefix          = "${var.prefix}aks"

  default_node_pool {
    name       = "default"
    node_count = var.node_count
    vm_size    = "Standard_B2s"
  }

  # SystemAssigned identity — AKS zarzadza wlasna tozsamoscia w Azure AD.
  identity {
    type = "SystemAssigned"
  }

  # OIDC Issuer — wymagany przez Workload Identity Federation (GHA OIDC).
  # Raz wlaczony nie moze byc wylaczony (Azure blokuje zmiane).
  oidc_issuer_enabled = true

  # Metrics Server jest potrzebny dla HPA (Horizontal Pod Autoscaler).
  # W AKS jest wlaczony domyslnie od wersji 1.27+.
}
