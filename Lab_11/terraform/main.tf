terraform {
  required_version = ">= 1.5"

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.110"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.30"
    }
  }
}

provider "azurerm" {
  features {}
}

# Provider kubernetes uzywa lokalnego kubeconfig.
# Przed uruchomieniem pelnego "terraform apply" wykonaj:
#   az aks get-credentials --resource-group <prefix>-rg --name <prefix>-aks
# Kontekst zostanie dodany do ~/.kube/config automatycznie.
provider "kubernetes" {
  config_path    = "~/.kube/config"
  config_context = "${var.prefix}-aks"
}

resource "azurerm_resource_group" "rg" {
  name     = "${var.prefix}-rg"
  location = var.location
}
