resource "azurerm_container_registry" "acr" {
  name                          = "${var.prefix}acr"
  resource_group_name           = azurerm_resource_group.rg.name
  location                      = azurerm_resource_group.rg.location
  sku                           = "Premium"
  admin_enabled                 = false
  public_network_access_enabled = false  # ACR dostepny wylacznie przez private endpoint
}

resource "azurerm_private_dns_zone" "acr_dns" {
  name                = "privatelink.azurecr.io"
  resource_group_name = azurerm_resource_group.rg.name
}

resource "azurerm_private_dns_zone_virtual_network_link" "acr_dns_link" {
  name                  = "${var.prefix}-acr-dns-link"
  resource_group_name   = azurerm_resource_group.rg.name
  private_dns_zone_name = azurerm_private_dns_zone.acr_dns.name
  registration_enabled  = false

  # ← TODO: podlacz VNet do strefy DNS aby VM mogla rozwiazywac
  # nazwe ACR (np. devops123456acr.azurecr.io) na prywatny adres IP.
  # Bez tego linku DNS VM bedzie widziec publiczny IP ACR (ktory jest zablokowany).
  # Wskazowka: uzyj azurerm_virtual_network.vnet.id
  #
  virtual_network_id = "" # ← TODO
}

resource "azurerm_private_endpoint" "acr_pe" {
  name                = "${var.prefix}-acr-pe"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  subnet_id           = azurerm_subnet.subnet.id

  private_service_connection {
    name                           = "${var.prefix}-acr-psc"
    private_connection_resource_id = azurerm_container_registry.acr.id
    is_manual_connection           = false

    # ← TODO: uzupelnij subresource_names dla Azure Container Registry.
    # Wskazowka: dla ACR jedyna dostepna subresource to "registry".
    # Dokumentacja: https://learn.microsoft.com/en-us/azure/private-link/private-endpoint-overview#private-link-resource
    #
    subresource_names = [] # ← TODO
  }

  private_dns_zone_group {
    name = "acr-dns-zone-group"

    # ← TODO: podlacz prywatna strefe DNS do private endpoint.
    # Terraform automatycznie utworzy rekord A wskazujacy na prywatny IP.
    # Wskazowka: uzyj [azurerm_private_dns_zone.acr_dns.id]
    #
    private_dns_zone_ids = [] # ← TODO
  }
}
