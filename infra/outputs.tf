output "acr_login_server" {
  description = "Adres logowania Azure Container Registry"
  value       = azurerm_container_registry.main.login_server
}

output "acr_name" {
  description = "Nazwa Azure Container Registry"
  value       = azurerm_container_registry.main.name
}

output "aks_name" {
  description = "Nazwa klastra AKS"
  value       = azurerm_kubernetes_cluster.main.name
}

output "resource_group_name" {
  description = "Nazwa grupy zasobów"
  value       = azurerm_resource_group.main.name
}
