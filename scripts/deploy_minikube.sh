#!/usr/bin/env bash
# Automates build ➜ deploy ➜ test on an *existing* Minikube cluster.

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CI_MODE=false
if [[ "${1-}" == "--ci" ]]; then CI_MODE=true ; fi

log() { echo -e "\033[1;34m▶ $*\033[0m" ; }

# ------------------------------------------------------------
# 0. Use Minikube’s Docker daemon so images go straight in‑cluster
# ------------------------------------------------------------
eval "$(minikube -p minikube docker-env)"

# ------------------------------------------------------------
# 1. Build service images
# ------------------------------------------------------------
for svc in hash-service length-service; do
  log "Building $svc ..."
  docker build -t "$svc:latest" "$ROOT_DIR/k8s/$svc"
done

# ------------------------------------------------------------
# 2. Helm repos & charts
# ------------------------------------------------------------
log "Adding / updating Helm repos"
helm repo add jaegertracing https://jaegertracing.github.io/helm-charts
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo add open-telemetry https://open-telemetry.github.io/opentelemetry-helm-charts
helm repo update

log "Installing Jaeger"
helm upgrade --install jaeger jaegertracing/jaeger \
  -f "$ROOT_DIR/helm/jaeger.yaml" --wait

log "Installing OpenTelemetry Collector"
helm upgrade --install otel-collector open-telemetry/opentelemetry-collector \
  -f "$ROOT_DIR/helm/open-telemetry.yaml" --wait

log "Installing Prometheus"
helm upgrade --install prometheus prometheus-community/prometheus \
  -f "$ROOT_DIR/helm/prometheus.yaml" --wait

# ------------------------------------------------------------
# 3. Apply k8s manifests
# ------------------------------------------------------------
log "Applying Hash & Length service manifests"
kubectl apply -f "$ROOT_DIR/k8s/hash-service/k8s"
kubectl apply -f "$ROOT_DIR/k8s/length-service/k8s"

log "Waiting for Deployments to be ready"
kubectl rollout status deployment/hash-service    --timeout=120s
kubectl rollout status deployment/length-service  --timeout=120s

# ------------------------------------------------------------
# 4. Annotate the Collector service for Prometheus
# ------------------------------------------------------------

kubectl annotate service otel-collector-opentelemetry-collector \
  prometheus.io/scrape="true" \
  prometheus.io/port="8889" \
  --overwrite

# ------------------------------------------------------------
# 5. Integration tests
# ------------------------------------------------------------
if $CI_MODE; then
  log "Port‑forwarding"
  kubectl port-forward svc/hash-service   8080:8080  >/tmp/hash.log 2>&1 &
  kubectl port-forward svc/length-service 8081:8081  >/tmp/len.log  2>&1 &
  kubectl port-forward svc/jaeger-query 16686:16686  >/tmp/jaeger.log  2>&1 &
  kubectl port-forward svc/prometheus-server 8000:80 >/tmp/prometheus.log  2>&1 &
  

  sleep 3
  python3 -q "$ROOT_DIR/tests/test_services.py"
  pkill -f "port-forward svc/hash-service"   || true
  pkill -f "port-forward svc/length-service" || true
fi

log "✅  Microservices deployed & tests passed!"