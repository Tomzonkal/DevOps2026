variable "prefix" {
  description = "Prefiks dla nazw zasobow — uzyj swojego numeru indeksu (tylko litery i cyfry, max 12 znakow, np. devops123456)"
  type        = string

  validation {
    condition     = can(regex("^[a-z0-9]{3,12}$", var.prefix))
    error_message = "Prefix moze zawierac tylko male litery i cyfry, dlugosc 3-12 znakow."
  }
}

variable "location" {
  description = "Region Azure"
  type        = string
  default     = "polandcentral"
}

variable "admin_username" {
  description = "Nazwa uzytkownika SSH dla VM"
  type        = string
  default     = "azureuser"
}

variable "ssh_public_key" {
  description = "Klucz publiczny SSH (zawartosc pliku ~/.ssh/id_lab10.pub)"
  type        = string
  sensitive   = true
}
