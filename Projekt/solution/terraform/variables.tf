variable "resource_group_name" {
  description = "Name of the Azure Resource Group"
  type        = string
  default     = "devops2026-rg"
}

variable "location" {
  description = "Azure region"
  type        = string
  default     = "westeurope"
}

variable "acr_name" {
  description = "Azure Container Registry name (globally unique, lowercase, no hyphens)"
  type        = string
  # Example: "devops2026acr" – override in terraform.tfvars
}

variable "aks_name" {
  description = "Azure Kubernetes Service cluster name"
  type        = string
  default     = "devops2026-aks"
}

variable "node_count" {
  description = "Number of nodes in the default node pool"
  type        = number
  default     = 1
}

variable "environment" {
  description = "Environment tag (dev / staging / prod)"
  type        = string
  default     = "dev"
}
