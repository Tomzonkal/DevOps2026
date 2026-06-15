terraform {
  backend "azurerm" {
    resource_group_name  = "rg-tf-state"
    storage_account_name = "stlab05tfstate422379"
    container_name       = "tfstate"
    key                  = "lab05.terraform.tfstate"
  }
}

