terraform {
  required_version = ">= 1.5"

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.110"
    }
  }
}

provider "azurerm" {
  features {}
}

# Dane biezacej subskrypcji i tenanta — uzywane w outputach i role assignment.
data "azurerm_subscription" "current" {}
data "azurerm_client_config" "current" {}

# Dedykowana resource group dla tożsamosci GHA.
# Oddzielona od zasobow labu zeby mozna ja bylo zachowac po terraform destroy labu.
resource "azurerm_resource_group" "gha" {
  name     = "${var.prefix}-gha-rg"
  location = var.location
}
