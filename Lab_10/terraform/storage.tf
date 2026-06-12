resource "azurerm_storage_account" "sa" {
  name                     = "${var.prefix}sa"
  resource_group_name      = azurerm_resource_group.rg.name
  location                 = azurerm_resource_group.rg.location
  account_tier             = "Standard"
  account_replication_type = "LRS"

  network_rules {
    default_action = "Deny"

    virtual_network_subnet_ids = [azurerm_subnet.subnet.id]

    bypass = ["AzureServices", "Logging", "Metrics"]
  }
}

resource "azurerm_storage_container" "dockerfiles" {
  name                  = "dockerfiles"
  storage_account_name  = azurerm_storage_account.sa.name
  container_access_type = "private"
}

resource "azurerm_storage_blob" "dockerfile" {
  name                   = "Dockerfile"
  storage_account_name   = azurerm_storage_account.sa.name
  storage_container_name = azurerm_storage_container.dockerfiles.name
  type                   = "Block"
  source                 = "${path.module}/../app/Dockerfile"
}
