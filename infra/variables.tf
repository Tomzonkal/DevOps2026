variable "resource_group_name" {
  type        = string
  description = "Nazwa grupy zasobów Azure"
  default     = "rg-devops-419534"
}

variable "location" {
  type        = string
  description = "Region Azure"
  default     = "polandcentral"
}

variable "acr_name" {
  type        = string
  description = "Globalnie unikalna nazwa Azure Container Registry"
}

variable "aks_name" {
  type        = string
  description = "Nazwa klastra Azure Kubernetes Service"
  default     = "aks-devops-419534"
}
