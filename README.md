# CLOUD-06: Kubernetes Cluster with Helm + GitOps with ArgoCD

![Kubernetes](https://img.shields.io/badge/Kubernetes-v1.28.8-326CE5?logo=kubernetes&logoColor=white)
![Helm](https://img.shields.io/badge/Helm-v3.21-0F1689?logo=helm&logoColor=white)
![ArgoCD](https://img.shields.io/badge/ArgoCD-v3.4.2-EF7B4D?logo=argo&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?logo=fastapi&logoColor=white)
![Tests](https://img.shields.io/badge/Tests-5%2F5%20passing-brightgreen)
![CI](https://github.com/CarlosRolo/cloud-k8s-gitops/actions/workflows/ci.yml/badge.svg)

Production-grade Kubernetes cluster running locally with k3s, a custom Helm chart for a FastAPI application, and full GitOps automation with ArgoCD. Every push to GitHub triggers an automatic deployment to the cluster.

## Architecture

    GitHub Repository
           │
           │  git push
           ▼
       ArgoCD (watches repo every 3 min)
           │
           │  auto-sync
           ▼
      k3s Cluster (WSL2)
           │
      ┌────┴────┐
      │ teleops │  namespace
      │         │
      │  3 Pods │  FastAPI (HPA: 2-5 replicas)
      │ Service │  ClusterIP
      │ Ingress │  traefik / teleops.local
      │   HPA   │  CPU target: 70%
      └─────────┘

## Stack

| Tool | Version | Purpose |
|------|---------|---------|
| k3s | v1.28.8 | Lightweight Kubernetes on WSL2 |
| Helm | v3.21 | Package manager — custom chart |
| ArgoCD | v3.4.2 | GitOps continuous delivery |
| FastAPI | 0.111 | Network device management API |
| Docker | latest | Multi-stage image build |
| metrics-server | built-in | HPA CPU metrics |

## Key Concepts Demonstrated

**Kubernetes Resources:**
- `Deployment` — declarative pod management with rolling updates
- `Service` — stable ClusterIP endpoint for the deployment
- `Ingress` — HTTP routing via Traefik ingress controller
- `HorizontalPodAutoscaler` — auto-scaling based on CPU utilization
- `Namespace` — environment isolation

**Helm Templating:**
- `_helpers.tpl` — reusable template functions
- `values.yaml` — environment-specific configuration
- Conditional blocks with `{{- if .Values.autoscaling.enabled }}`
- Label standardization with `include`

**GitOps Flow:**
- ArgoCD Application manifest defines source (GitHub) and destination (cluster)
- `automated.prune: true` — removes resources deleted from Git
- `automated.selfHeal: true` — reverts manual cluster changes
- Any `git push` to `helm/` triggers automatic re-sync

## Project Structure

    cloud-k8s-gitops/
    ├── app/
    │   ├── src/
    │   │   ├── main.py          # FastAPI endpoints
    │   │   └── models.py        # Pydantic models
    │   ├── tests/
    │   │   └── test_main.py     # 5 pytest tests
    │   ├── Dockerfile           # Multi-stage build
    │   └── requirements.txt
    ├── helm/
    │   └── fastapi-app/
    │       ├── Chart.yaml
    │       ├── values.yaml      # Replica count, image, HPA config
    │       └── templates/
    │           ├── _helpers.tpl
    │           ├── deployment.yaml
    │           ├── service.yaml
    │           ├── ingress.yaml
    │           └── hpa.yaml
    ├── gitops/
    │   └── applications/
    │       └── fastapi-app.yaml # ArgoCD Application manifest
    └── k8s/
        └── base/
            └── namespace.yaml

## Quick Start

    # 1. Install k3s
    curl -sfL https://get.k3s.io | INSTALL_K3S_VERSION="v1.28.8+k3s1" sh -

    # 2. Configure kubectl
    mkdir -p ~/.kube && sudo cp /etc/rancher/k3s/k3s.yaml ~/.kube/config
    sudo chown $USER:$USER ~/.kube/config

    # 3. Install Helm
    curl -fsSL https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

    # 4. Build and load image
    docker build -t teleops-api:latest app/
    docker save teleops-api:latest | sudo k3s ctr images import -

    # 5. Deploy with Helm
    kubectl apply -f k8s/base/namespace.yaml
    helm install teleops helm/fastapi-app/ --namespace teleops

    # 6. Install ArgoCD
    kubectl create namespace argocd
    kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

    # 7. Apply GitOps application
    kubectl apply -f gitops/applications/fastapi-app.yaml

    # 8. Access ArgoCD UI
    kubectl port-forward svc/argocd-server 8443:443 -n argocd
    # Open https://localhost:8443
    kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check + cluster name |
| GET | `/devices` | List all network devices |
| GET | `/devices/{id}` | Get device by ID |
| POST | `/devices` | Create new device |
| DELETE | `/devices/{id}` | Delete device |
| GET | `/metrics` | Prometheus metrics |

## GitOps Demo

    # Scale replicas via Git (GitOps way — never kubectl scale)
    sed -i 's/replicaCount: 3/replicaCount: 4/' helm/fastapi-app/values.yaml
    git add helm/fastapi-app/values.yaml
    git commit -m "scale: increase to 4 replicas"
    git push origin main
    # ArgoCD detects change and applies automatically within 3 minutes

## Results

| Component | Status |
|-----------|--------|
| k3s cluster | ✅ Running (1 node, Ready) |
| FastAPI pods | ✅ 3/3 Running |
| HPA | ✅ Active (3%/70% CPU) |
| ArgoCD sync | ✅ Synced from GitHub |
| Tests | ✅ 5/5 passing |

## Author

**Carlos David Rodriguez Lopez**  
Telematic Engineer — ESPOCH  
Riobamba, Chimborazo, Ecuador  
Manta, Manabí, Ecuador  
GitHub: [github.com/CarlosRolo](https://github.com/CarlosRolo)  
LinkedIn: [linkedin.com/in/carlosdrodriguezl](https://linkedin.com/in/carlosdrodriguezl)

## License

MIT License — see [LICENSE](LICENSE)
