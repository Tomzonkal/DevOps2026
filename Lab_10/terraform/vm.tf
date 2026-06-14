resource "azurerm_public_ip" "vm_pip" {
  name                = "${var.prefix}-vm-pip"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  allocation_method   = "Static"
  sku                 = "Standard"
}

resource "azurerm_network_interface" "vm_nic" {
  name                = "${var.prefix}-vm-nic"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name

  ip_configuration {
    name                          = "internal"
    subnet_id                     = azurerm_subnet.subnet.id
    private_ip_address_allocation = "Dynamic"
    public_ip_address_id          = azurerm_public_ip.vm_pip.id
  }
}

resource "azurerm_linux_virtual_machine" "vm" {
  name                = "${var.prefix}-vm"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  size                = "Standard_D2s_v3"
  admin_username      = var.admin_username

  network_interface_ids = [azurerm_network_interface.vm_nic.id]

  admin_ssh_key {
    username   = var.admin_username
    public_key = var.ssh_public_key
  }

  os_disk {
    caching              = "ReadWrite"
    storage_account_type = "Standard_LRS"
  }

  source_image_reference {
    publisher = "Canonical"
    offer     = "0001-com-ubuntu-server-jammy"
    sku       = "22_04-lts-gen2"
    version   = "latest"
  }

  identity {
    type = "SystemAssigned"
  }

  # cloud-init: instalacja Docker i Azure CLI przy starcie VM
  custom_data = base64encode(<<-EOF
    #!/bin/bash
    set -e
    apt-get update -y
    apt-get install -y apt-transport-https ca-certificates curl gnupg lsb-release

    # Docker
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg \
      | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
    echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] \
      https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" \
      | tee /etc/apt/sources.list.d/docker.list > /dev/null
    apt-get update -y
    apt-get install -y docker-ce docker-ce-cli containerd.io

    # Azure CLI
    curl -sL https://aka.ms/InstallAzureCLIdeb | bash

    usermod -aG docker ${var.admin_username}
    systemctl enable docker
    systemctl start docker
  EOF
  )
}

# Uprawnienie: VM moze pobierac bloby z Storage Account (do pobrania Dockerfile)
resource "azurerm_role_assignment" "vm_sa_blob_reader" {
  scope                = azurerm_storage_account.sa.id
  role_definition_name = "Storage Blob Data Reader"
  principal_id         = azurerm_linux_virtual_machine.vm.identity[0].principal_id
}

# VM musi miec mozliwosc wypychania obrazow Docker do rejestru.
# Dostepne role ACR: AcrPull (tylko pull), AcrPush (pull + push), AcrDelete (pull + push + delete)
# Wskazowka: principal_id to azurerm_linux_virtual_machine.vm.identity[0].principal_id
resource "azurerm_role_assignment" "vm_acr_push" {
  scope                = azurerm_container_registry.acr.id
  role_definition_name = "AcrPush"
  principal_id = azurerm_linux_virtual_machine.vm.identity[0].principal_id
}
