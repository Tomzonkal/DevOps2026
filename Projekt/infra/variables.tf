variable "resource_group_name" {
  type    = string
  default = "rg-lab05_422379"
}

variable "location" {
  type    = string
  default = "polandcentral"
}

variable "acr_name" {
  type    = string
  default = "acrlab05422379"
}

variable "aks_name" {
  type    = string
  default = "aks-lab05_422379"
}

variable "aks_dns_prefix" {
  type    = string
  default = "aks-lab05-422379"
}

variable "aks_node_vm_size" {
  type    = string
  default = "Standard_B2s_v2"
}
