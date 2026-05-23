output "vm_public_ip" {
  description = "Publiczny adres IP VM — uzyj do polaczenia SSH"
  value       = azurerm_public_ip.vm_pip.ip_address
}

output "acr_login_server" {
  description = "Adres rejestru ACR (uzyj jako prefiks obrazu Docker)"
  value       = azurerm_container_registry.acr.login_server
}

output "storage_account_name" {
  description = "Nazwa Storage Account (uzyj do pobierania Dockerfile)"
  value       = azurerm_storage_account.sa.name
}

output "resource_group_name" {
  description = "Nazwa Resource Group"
  value       = azurerm_resource_group.rg.name
}

output "ssh_command" {
  description = "Gotowa komenda SSH"
  value       = "ssh -i ~/.ssh/id_lab10 ${var.admin_username}@${azurerm_public_ip.vm_pip.ip_address}"
}
