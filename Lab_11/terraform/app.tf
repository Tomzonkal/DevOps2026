# Deployment i Service dla aplikacji podinfo.
#
# podinfo to referencyjna aplikacja Go uzywana w spolecznosci Kubernetes.
# Zwraca w odpowiedzi m.in. hostname poda — dzieki temu mozna zobaczyc,
# ktory pod obsluguje dany request (przydatne przy skalowaniu).
#
# Dokumentacja podinfo: https://github.com/stefanprodan/podinfo

resource "kubernetes_deployment_v1" "podinfo" {
  metadata {
    name = "podinfo"
    labels = {
      app = "podinfo"
    }
  }

  spec {
    # ← TODO: podaj liczbe replik startowych (liczba calkowita, min. 1)
    replicas = 2

    selector {
      match_labels = {
        app = "podinfo"
      }
    }

    template {
      metadata {
        labels = {
          app = "podinfo"
        }
      }

      spec {
        container {
          name = "podinfo"

          # ← TODO: podaj obraz Docker z Docker Hub (format: <nazwa>:<tag>)
          # Uzyj oficjalnego obrazu podinfo w wersji 6.6.0
          image             = "stefanprodan/podinfo:6.6.0"
          image_pull_policy = "IfNotPresent"

          port {
            container_port = 9898
          }

          resources {
            requests = {
              # ← TODO: podaj minimalne zasoby CPU dla kontenera
              # Jednostka "m" oznacza millicores (1000m = 1 vCPU)
              # UWAGA: bez tego pola HPA nie bedzie mogl mierzyc zuzycia CPU!
              cpu = "50m"
            }
            limits = {
              # ← TODO: podaj maksymalne zasoby CPU dla kontenera
              # Powinno byc wieksze niz requests (np. 4x wiecej)
              cpu = "200m"
            }
          }

          # Zmienne srodowiskowe z ConfigMap (zdefiniowanego w config.tf)
          env_from {
            config_map_ref {
              name = kubernetes_config_map_v1.app_config.metadata[0].name
            }
          }

          liveness_probe {
            http_get {
              path = "/healthz"
              port = 9898
            }
            initial_delay_seconds = 5
            period_seconds        = 10
          }
        }
      }
    }
  }

  depends_on = [azurerm_kubernetes_cluster.aks]
}

# Service typu LoadBalancer — AKS automatycznie tworzy Azure Load Balancer
# z publicznym adresem IP. Mozna sie polaczyc bezposrednio przez ten IP.
resource "kubernetes_service_v1" "podinfo" {
  metadata {
    name = "podinfo"
  }

  spec {
    selector = {
      app = "podinfo"
    }

    port {
      port        = 80
      target_port = 9898
    }

    type = "LoadBalancer"
  }
}
