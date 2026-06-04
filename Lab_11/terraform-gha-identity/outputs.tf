output "AZURE_CLIENT_ID" {
  description = "Wpisz jako GitHub Secret: AZURE_CLIENT_ID"
  value       = azurerm_user_assigned_identity.gha.client_id
}

output "AZURE_TENANT_ID" {
  description = "Wpisz jako GitHub Secret: AZURE_TENANT_ID"
  value       = data.azurerm_client_config.current.tenant_id
}

output "AZURE_SUBSCRIPTION_ID" {
  description = "Wpisz jako GitHub Secret: AZURE_SUBSCRIPTION_ID"
  value       = data.azurerm_subscription.current.subscription_id
}

output "setup_instructions" {
  description = "Instrukcja konfiguracji GitHub Secrets"
  value       = <<-EOT

    ============================================================
     Skopiuj ponizsze wartosci do GitHub Secrets swojego forka:
     Settings -> Secrets and variables -> Actions -> New secret
    ============================================================

     AZURE_CLIENT_ID       = ${azurerm_user_assigned_identity.gha.client_id}
     AZURE_TENANT_ID       = ${data.azurerm_client_config.current.tenant_id}
     AZURE_SUBSCRIPTION_ID = ${data.azurerm_subscription.current.subscription_id}

     NIE PRZECHOWUJ ZADNYCH HASEL — OIDC nie wymaga client_secret!

    ============================================================
  EOT
}
