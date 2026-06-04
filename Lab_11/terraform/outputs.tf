output "aks_name" {
  description = "Nazwa klastra AKS — uzyj do az aks get-credentials"
  value       = azurerm_kubernetes_cluster.aks.name
}

output "resource_group_name" {
  description = "Nazwa Resource Group"
  value       = azurerm_resource_group.rg.name
}

output "get_credentials_command" {
  description = "Gotowa komenda do pobrania kubeconfig"
  value       = "az aks get-credentials --resource-group ${azurerm_resource_group.rg.name} --name ${azurerm_kubernetes_cluster.aks.name}"
}

output "app_ip" {
  description = "Publiczny IP aplikacji — uzyj do stress testu i weryfikacji (moze byc <pending> przez 1-2 min po apply)"
  value       = try(kubernetes_service_v1.podinfo.status[0].load_balancer[0].ingress[0].ip, "Jeszcze niedostepny — poczekaj chwile i uruchom: terraform output app_ip")
}
