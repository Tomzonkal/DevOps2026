# Horizontal Pod Autoscaler (HPA) — automatyczne skalowanie liczby replik
# na podstawie zuzycia zasobow (tu: CPU).
#
# Jak dziala HPA:
# 1. Metrics Server zbiera zuzycie CPU z kubelet co 15 sekund
# 2. HPA controller porownuje srednie zuzycie z targetem co 15 sekund
# 3. Gdy srednie zuzycie > target: HPA zwieksza replicas (scale up)
# 4. Gdy srednie zuzycie < target przez 5 minut: HPA zmniejsza replicas (scale down)
#
# WAZNE: HPA wymaga zdefiniowanego resources.requests.cpu w Deployment!
# Bez tego pola zobaczysz: <unknown>/50% i HPA nie bedzie skalowac.
# (patrz: resources.requests.cpu w app.tf)

resource "kubernetes_horizontal_pod_autoscaler_v2" "podinfo" {
  metadata {
    name = "podinfo-hpa"
  }

  spec {
    scale_target_ref {
      api_version = "apps/v1"
      kind        = "Deployment"
      name        = kubernetes_deployment_v1.podinfo.metadata[0].name
    }

    # ← TODO: podaj minimalna liczbe replik (min. 1)
    # Nawet przy braku ruchu HPA nie zejdzie ponizej tej wartosci
    min_replicas = 1

    # ← TODO: podaj maksymalna liczbe replik (max. 5 dla tego labu)
    # HPA nie przekroczy tej wartosci nawet przy bardzo duzym obciazeniu
    max_replicas = 1

    metric {
      type = "Resource"

      resource {
        name = "cpu"

        target {
          type = "Utilization"

          # ← TODO: podaj prog zuzycia CPU w procentach (wartosc 1-100)
          # Gdy srednie zuzycie CPU przekroczy ten prog, HPA doda repliki.
          # Zbyt wysoki prog (np. 90) = HPA reaguje pozno
          # Zbyt niski prog (np. 10) = HPA reaguje na kazdy request
          # Wskazowka: dobra wartosc dla tych labow to ok. 10%
          average_utilization = 0
        }
      }
    }
  }
}
