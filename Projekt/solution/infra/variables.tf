variable "resource_group_name" {
  type    = string
  default = "devops422385-gha-rg"
}

variable "location" {
  type    = string
  default = "polandcentral"
}

variable "acr_name" {
  type = string
}

variable "aks_name" {
  type    = string
  default = "aks-lab04"
}