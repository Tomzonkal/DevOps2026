# Rola Contributor na poziomie subskrypcji — umozliwia tworzenie i usuwanie
# dowolnych zasobow Azure (resource group, AKS, itp.).
#
# UWAGA BEZPIECZENSTWA: W srodowisku produkcyjnym nalez ograniczyc zakres
# do konkretnej resource group zamiast calej subskrypcji. Na potrzeby labu
# subskrypcja jest akceptowalnym kompromisem miedzy prostota a kontrola.
resource "azurerm_role_assignment" "gha_contributor" {
  scope                = data.azurerm_subscription.current.id
  role_definition_name = "Contributor"
  principal_id         = azurerm_user_assigned_identity.gha.principal_id
}
