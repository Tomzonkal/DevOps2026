variable "prefix" {
  description = "Prefiks dla nazw zasobow — uzyj swojego numeru indeksu (tylko litery i cyfry, max 12 znakow)"
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

variable "github_org" {
  description = "Nazwa uzytkownika lub organizacji GitHub (np. JanKowalski)"
  type        = string
}

variable "github_repo" {
  description = "Nazwa repozytorium GitHub (np. DevOps2026)"
  type        = string
  default     = "DevOps2026"
}

variable "github_environment" {
  description = "Nazwa srodowiska GitHub Actions — uzyj swojego numeru indeksu (np. 123456)"
  type        = string
}
