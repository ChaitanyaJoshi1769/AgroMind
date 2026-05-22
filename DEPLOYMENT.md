# AgroMind Deployment Guide

Comprehensive guide for deploying AgroMind across different environments.

## Table of Contents

1. [Local Development](#local-development)
2. [Docker Compose (Staging)](#docker-compose-staging)
3. [Kubernetes (Production)](#kubernetes-production)
4. [Cloud Deployment (AWS/GCP)](#cloud-deployment)
5. [Edge Devices (Jetson)](#edge-devices-jetson)
6. [Monitoring & Operations](#monitoring--operations)

---

## Local Development

### Prerequisites

```bash
# macOS (using Homebrew)
brew install docker docker-compose node python@3.11 postgresql@16

# Ubuntu/Debian
sudo apt update
sudo apt install -y docker.io docker-compose nodejs python3.11 postgresql

# Verify installations
docker --version
node --version
python3 --version
```

### Initial Setup

```bash
# Clone repository
git clone https://github.com/ChaitanyaJoshi1769/AgroMind.git
cd AgroMind

# Copy environment file
cp .env.example .env.local

# Install dependencies
npm install

# Start all services
npm run docker:up

# Wait for services to be healthy (30-60 seconds)
npm run docker:logs
```

### Access Services

| Service | URL | Credentials |
|---------|-----|-------------|
| Frontend | http://localhost:3000 | - |
| API | http://localhost:8000 | - |
| API Docs | http://localhost:8000/docs | - |
| PgAdmin | http://localhost:5050 | admin@admin.com / admin |
| Grafana | http://localhost:3001 | admin / admin |
| Prometheus | http://localhost:9090 | - |
| Kafka UI | http://localhost:8080 | - |

### Development Workflow

```bash
# Terminal 1: Frontend
cd apps/web
npm run dev

# Terminal 2: Backend
cd apps/api
poetry run uvicorn src.main:app --reload

# Terminal 3: Infrastructure (keep docker-compose running)
npm run docker:up
```

---

## Docker Compose (Staging)

### Build Custom Images

```bash
# Build all images
docker-compose build

# Build specific service
docker-compose build api web

# Build with no cache
docker-compose build --no-cache
```

### Scale Services

```bash
# Scale API to 3 replicas
docker-compose up -d --scale api=3

# Scale workers
docker-compose up -d --scale worker=2
```

### Database Migrations

```bash
# Connect to database
docker exec -it agromind-postgres psql -U agromind -d agromind

# Run migrations (from container)
docker exec agromind-api poetry run alembic upgrade head
```

### Persistent Data

```bash
# Backup database
docker exec agromind-postgres pg_dump -U agromind agromind > backup.sql

# Restore database
docker exec -i agromind-postgres psql -U agromind agromind < backup.sql

# View volumes
docker volume ls | grep agromind
```

### Cleanup

```bash
# Stop all containers
npm run docker:down

# Remove all containers and volumes
docker-compose down -v

# Clean everything (use with caution!)
npm run clean
```

---

## Kubernetes (Production)

### Prerequisites

```bash
# Install kubectl
brew install kubectl

# Install helm
brew install helm

# Create cluster (using Docker Desktop)
# Enable Kubernetes in Docker Desktop settings
# Or use: minikube start

# Verify cluster
kubectl cluster-info
kubectl get nodes
```

### Deploy to Kubernetes

```bash
# Create namespace
kubectl create namespace agromind

# Create secrets
kubectl create secret generic database-credentials \
  --from-literal=postgres-url=postgresql://user:pass@host/db \
  -n agromind

kubectl create secret generic redis-credentials \
  --from-literal=url=redis://user:pass@host:6379 \
  -n agromind

# Deploy infrastructure
kubectl apply -f infrastructure/kubernetes/

# Verify deployment
kubectl get pods -n agromind
kubectl get services -n agromind

# Check logs
kubectl logs -f deployment/agromind-api -n agromind

# Access services
kubectl port-forward service/agromind-api 8000:80 -n agromind
kubectl port-forward service/agromind-web 3000:80 -n agromind
```

### Kubernetes Best Practices

```bash
# Health checks
kubectl describe pod <pod-name> -n agromind

# Check resource usage
kubectl top nodes
kubectl top pods -n agromind

# Scale deployment
kubectl scale deployment agromind-api --replicas=5 -n agromind

# Rolling update
kubectl set image deployment/agromind-api \
  api=agromind/api:v0.1.0 -n agromind

# Check rollout status
kubectl rollout status deployment/agromind-api -n agromind

# Rollback if needed
kubectl rollout undo deployment/agromind-api -n agromind
```

### Monitoring in Kubernetes

```bash
# Port-forward to Prometheus
kubectl port-forward svc/prometheus 9090:9090 -n agromind

# Port-forward to Grafana
kubectl port-forward svc/grafana 3001:3000 -n agromind

# View events
kubectl get events -n agromind --sort-by='.lastTimestamp'
```

---

## Cloud Deployment

### AWS EKS

```bash
# Create cluster
eksctl create cluster --name agromind --region us-east-1 --nodes 3

# Get credentials
aws eks update-kubeconfig --name agromind --region us-east-1

# Deploy
kubectl apply -f infrastructure/kubernetes/

# Create load balancer
kubectl apply -f infrastructure/kubernetes/ingress-aws.yaml

# Get external IP
kubectl get svc -n agromind
```

### GCP GKE

```bash
# Create cluster
gcloud container clusters create agromind \
  --zone us-central1-a \
  --num-nodes 3 \
  --machine-type n1-standard-2

# Get credentials
gcloud container clusters get-credentials agromind --zone us-central1-a

# Deploy
kubectl apply -f infrastructure/kubernetes/

# Create ingress
kubectl apply -f infrastructure/kubernetes/ingress-gcp.yaml

# Get external IP
kubectl get ingress -n agromind
```

### Terraform (AWS)

```bash
# Initialize
cd infrastructure/terraform
terraform init

# Plan
terraform plan -out=tfplan

# Apply
terraform apply tfplan

# Outputs
terraform output
```

---

## Edge Devices (Jetson)

### Setup Jetson Device

```bash
# SSH into Jetson
ssh agromind@jetson-hostname

# Install Docker
curl https://get.docker.com | sh
sudo usermod -aG docker agromind

# Install Docker Compose
sudo apt install python3-pip
sudo pip install docker-compose

# Install dependencies
sudo apt install -y python3-opencv libjpeg-dev zlib1g-dev

# Clone repository
git clone https://github.com/ChaitanyaJoshi1769/AgroMind.git
cd AgroMind
```

### Deploy Edge Runtime

```bash
# Build edge-specific images
docker build -f Dockerfile.edge-runtime -t agromind-edge:latest .

# Run edge container
docker run -d \
  --name agromind-edge \
  --restart always \
  -v /data:/data \
  -v /models:/models \
  --gpus all \
  agromind-edge:latest

# Monitor
docker logs -f agromind-edge

# Check GPU usage
nvidia-smi
```

### Model Optimization for Jetson

```bash
# Convert PyTorch to ONNX
python3 scripts/export_onnx.py --model yolov11m --output /models/yolov11m.onnx

# Quantize for TensorRT
python3 scripts/quantize_tensorrt.py --onnx /models/yolov11m.onnx --output /models/yolov11m.trt

# Test inference
python3 scripts/test_inference.py --model /models/yolov11m.trt --image test.jpg
```

---

## Monitoring & Operations

### Health Checks

```bash
# API health
curl http://localhost:8000/health

# Database connection
curl http://localhost:8000/api/health/database

# Redis connection
curl http://localhost:8000/api/health/redis

# Kafka connectivity
curl http://localhost:8000/api/health/kafka
```

### Performance Monitoring

```bash
# CPU/Memory usage
docker stats agromind-api

# Database query performance
psql -h localhost -U agromind -d agromind -c "
  SELECT query, calls, mean_time
  FROM pg_stat_statements
  ORDER BY mean_time DESC
  LIMIT 10;"

# Check slow queries
tail -f /var/log/postgres/slowquery.log
```

### Backup & Recovery

```bash
# Daily backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
docker exec agromind-postgres pg_dump -U agromind agromind | \
  gzip > /backups/agromind_$DATE.sql.gz

# Cron job for automated backups
# 0 2 * * * /scripts/backup.sh

# Restore from backup
gunzip < /backups/agromind_20260523_020000.sql.gz | \
  docker exec -i agromind-postgres psql -U agromind agromind
```

### Log Management

```bash
# Centralized logging (ELK Stack)
docker-compose -f infrastructure/docker/docker-compose.elastic.yml up -d

# View logs in Kibana
# http://localhost:5601

# Rotate logs
# Add to /etc/logrotate.d/agromind
# /var/log/agromind/*.log {
#   daily
#   rotate 14
#   compress
#   delaycompress
#   notifempty
# }
```

### Alerting

```bash
# Configure Prometheus alerts
# infrastructure/prometheus/alerts.yml

# Webhook for Slack notifications
# POST to: https://hooks.slack.com/services/YOUR/WEBHOOK

# Key alerts:
# - API response time > 500ms
# - Database connection pool exhausted
# - Disk usage > 80%
# - Memory usage > 90%
# - Pod restart count > 0
```

---

## Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| Port already in use | `lsof -i :3000` then `kill -9 <PID>` |
| Database connection refused | Check `DATABASE_URL` in `.env` |
| Out of disk space | `docker system prune` and `docker volume prune` |
| Pod pending | `kubectl describe pod <name>` to check resources |
| Image pull failed | Check container registry credentials |

### Debugging

```bash
# Enter container shell
docker exec -it agromind-api bash

# Check environment
env | grep AGROMIND

# Test database connection
psql $DATABASE_URL -c "SELECT 1"

# Check network connectivity
nc -zv database-host 5432

# View container logs
docker logs -f --tail=100 agromind-api
```

---

## Performance Tuning

### Database

```sql
-- Analyze table
ANALYZE farms;

-- Create indices
CREATE INDEX idx_fields_farm_status ON fields(farm_id, status);

-- Vacuum
VACUUM FULL ANALYZE;

-- Connection pooling
-- Update pgBouncer config for optimal performance
```

### Redis

```bash
# Monitor Redis
redis-cli MONITOR

# Check memory usage
redis-cli INFO memory

# Optimize configuration
# maxmemory-policy: allkeys-lru
```

### API

```python
# Enable caching
from functools import lru_cache

@lru_cache(maxsize=1000)
def expensive_operation():
    pass

# Use async operations
async def handle_request():
    results = await asyncio.gather(
        db_query(),
        cache_query(),
        external_api_call()
    )
```

---

## CI/CD Pipeline

### GitHub Actions

```yaml
# .github/workflows/deploy.yml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Build images
        run: docker-compose build
      - name: Push to registry
        run: docker push agromind/api:latest
      - name: Deploy to K8s
        run: kubectl apply -f infrastructure/kubernetes/
```

---

## Maintenance

### Regular Tasks

- **Daily**: Monitor dashboards, check alerts
- **Weekly**: Review logs, test backups
- **Monthly**: Analyze performance, plan scaling
- **Quarterly**: Security audit, dependency updates
- **Annually**: Disaster recovery drill, capacity planning

### Update Procedures

```bash
# Minor updates (backwards compatible)
git pull origin main
npm run build
docker-compose down
docker-compose up -d

# Major updates (requires migration)
npm run db:migrate
# Test thoroughly before deploying to production
```

---

For additional support, see README.md or ARCHITECTURE.md
