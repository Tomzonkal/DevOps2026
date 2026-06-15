# ConfigMap — przechowuje konfiguracje aplikacji jako klucz-wartosc.
# Dzieki oddzieleniu konfiguracji od obrazu mozna zmieniac ustawienia
# bez przebudowania kontenera (wystarczy kubectl rollout restart).
#
# Klucze z ConfigMap sa wstrzykiwane jako zmienne srodowiskowe do kontenera
# (patrz: env_from -> config_map_ref w app.tf).

resource "kubernetes_config_map_v1" "app_config" {
  metadata {
    name = "podinfo-config"
  }

  data = {
    # Wiadomosc wyswietlana przez podinfo na stronie glownej.
    # Sprawdz efekt: curl http://<APP-IP>/ | grep message
    # ← TODO: wpisz dowolna wiadomosc (np. "Czesc z AGH DevOps 2026!")
    PODINFO_UI_MESSAGE = "Czesc z AGH DevOps 2026!"

    # Poziom logowania aplikacji.
    # Dostepne wartosci: debug | info | warn | error
    # ← TODO: wybierz poziom logowania
    PODINFO_LOG_LEVEL = "info"
  }
}

# Secret — przechowuje dane wrazliwe (hasla, tokeny, klucze).
# W odrozneniu od ConfigMap, Kubernetes przechowuje Secret zakodowany
# w base64 i ogranicza dostep przez RBAC.
#
# WAZNE: provider Terraform automatycznie koduje wartosci do base64.
# Wpisz plain text — NIE koduj recznie przez echo -n "x" | base64.

resource "kubernetes_secret_v1" "app_secret" {
  metadata {
    name = "podinfo-secret"
  }

  type = "Opaque"

  data = {
    # ← TODO: wpisz dowolne haslo (plain text, min. 8 znakow)
    password = "haslo123"
  }
}
