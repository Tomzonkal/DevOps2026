#!/usr/bin/env bash
# stress.sh — generator obciazenia HTTP dla testu HPA
#
# Uzycie:
#   chmod +x stress.sh
#   ./stress.sh http://<INGRESS-IP>.nip.io
#   ./stress.sh http://<INGRESS-IP>.nip.io 120   # czas trwania w sekundach (domyslnie 90)
#
# Podczas dzialania skryptu obserwuj w drugim terminalu:
#   kubectl get hpa -w
#   kubectl get pods -w

set -euo pipefail

INGRESS_URL="${1:?Blad: podaj URL jako pierwszy argument. Przyklad: ./stress.sh http://20.10.5.3.nip.io}"
DURATION="${2:-90}"
CONCURRENCY=15

echo "============================================="
echo " Stress test podinfo"
echo "============================================="
echo " URL:          $INGRESS_URL"
echo " Czas trwania: ${DURATION}s"
echo " Wspolbieznosc: $CONCURRENCY requestow"
echo ""
echo " Obserwuj w drugim terminalu:"
echo "   kubectl get hpa -w"
echo "   kubectl get pods -w"
echo ""
echo " Nacisnij Ctrl+C aby zatrzymac wczesniej"
echo "============================================="

# Weryfikacja czy URL odpowiada przed startem
if ! curl -sf --max-time 5 "$INGRESS_URL" -o /dev/null; then
  echo ""
  echo "BLAD: $INGRESS_URL nie odpowiada."
  echo "Sprawdz czy:"
  echo "  1. terraform apply zostal wykonany z ustawionym ingress_host"
  echo "  2. kubectl get ingress pokazuje poprawny host"
  echo "  3. curl http://<INGRESS-IP>/ (bez hosta) dziala"
  exit 1
fi

echo ""
echo "Generowanie ruchu..."
echo ""

end_time=$((SECONDS + DURATION))
request_count=0

while [ $SECONDS -lt $end_time ]; do
  for _ in $(seq 1 $CONCURRENCY); do
    curl -sf "$INGRESS_URL" -o /dev/null &
  done
  request_count=$((request_count + CONCURRENCY))

  # Co 10 sekund pokazuj statystyki
  if [ $((request_count % 150)) -eq 0 ]; then
    echo "[$(date +%H:%M:%S)] Wyslano ~${request_count} requestow | Pozostalo: $((end_time - SECONDS))s"
  fi

  sleep 0.2
done

wait
echo ""
echo "============================================="
echo " Stress test zakonczony. Wyslano ~${request_count} requestow."
echo ""
echo " Sprawdz wynik:"
echo "   kubectl get hpa podinfo-hpa"
echo "   kubectl get pods -l app=podinfo"
echo ""
echo " Jesli HPA nie zaskalow:"
echo "   kubectl describe hpa podinfo-hpa"
echo "   (szukaj linii Conditions i Events)"
echo "============================================="
