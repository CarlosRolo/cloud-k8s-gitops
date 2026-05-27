.PHONY: help build load deploy sync logs status clean test argocd

help:
	@echo "TeleOps K8s GitOps — available commands:"
	@echo "  make build    Build Docker image"
	@echo "  make load     Load image into k3s"
	@echo "  make deploy   Deploy with Helm"
	@echo "  make sync     Force ArgoCD sync"
	@echo "  make logs     Show pod logs"
	@echo "  make status   Show cluster status"
	@echo "  make test     Run pytest tests"
	@echo "  make argocd   Port-forward ArgoCD UI"
	@echo "  make api      Port-forward API"
	@echo "  make clean    Uninstall Helm release"

build:
	docker build -t teleops-api:latest app/

load:
	docker save teleops-api:latest | sudo k3s ctr images import -

deploy:
	kubectl apply -f k8s/base/namespace.yaml
	helm upgrade --install teleops helm/fastapi-app/ --namespace teleops

sync:
	kubectl patch app teleops-fastapi -n argocd --type merge -p '{"operation":{"initiatedBy":{"username":"admin"},"sync":{"revision":"HEAD"}}}'

logs:
	kubectl logs -l app.kubernetes.io/name=fastapi-app -n teleops --tail=50

status:
	@echo "=== Nodes ==="
	kubectl get nodes
	@echo "=== Pods ==="
	kubectl get pods -n teleops
	@echo "=== HPA ==="
	kubectl get hpa -n teleops
	@echo "=== ArgoCD ==="
	kubectl get applications -n argocd

test:
	cd app && python3 -m pytest tests/ -v

argocd:
	kubectl port-forward svc/argocd-server 8443:443 -n argocd

api:
	kubectl port-forward svc/teleops-fastapi-app 7070:80 -n teleops

clean:
	helm uninstall teleops --namespace teleops
