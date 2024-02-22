# Volumez Prometheus Exporter
Export [Volumez](https://volumez.com/) API Data as prometheus metrics.

<img src="https://github.com/sween/volumez-prometheus-exporter/raw/main/assets/volumez-prometheus-exporter.png" alt="Volumez Metrics">

Uses the [Volumez Rest API](https://volumez.com/static/swagger.html) 

## Overview
<img src="https://github.com/sween/volumez-prometheus-exporter/raw/main/assets/volumez-metrics-overview.png" alt="Volumez Metrics Overview">

## Quick Start

- Build Container
- Deploy on Kubernetes
- Scrape The Metrics
- Inspect

### Container
Build it and push it, real good.

```
docker build -t volumez-prometheus-exporter .
docker image tag volumez-prometheus-exporter sween/volumez-prometheus-exporter:latest
docker push sween/volumez-prometheus-exporter:latest
```

### Kubernetes

Secrets:

```
kubectl create ns volumez
kubectl create secret generic volumez-api-key -n volumez \
    --from-literal=volumez_token='eyJraWQiOiJoUEhDVWNDOXVqeHp4eCthUXdHalFDaDlhYVB......'
```

Apply Deployment:

```
kubectl apply -f deploy/deployment.yaml -n volumez
kubectl apply -f deploy/service.yaml -n volumez
```

You should see the deployment running on the cluster, explore the services to see how to reach the prometheus endpoint, in this case MetalLB.

Pod:
<img src="https://github.com/sween/volumez-prometheus-exporter/raw/main/assets/volumez-prometheus-pod.png" alt="Volumez Metrics">

Service:
<img src="https://github.com/sween/volumez-prometheus-exporter/raw/main/assets/volumez-prometheus-service.png" alt="Volumez Metrics">

k8sviz:
<img src="https://github.com/sween/volumez-prometheus-exporter/raw/main/assets/volumez-kviz.png" alt="Volumez Metrics">


### Metric Exported
At this point, not the most exhaustive list of one, but now we iterate.

<img src="https://github.com/sween/volumez-prometheus-exporter/raw/main/assets/volumez-prometheus-metrics.png" alt="Volumez Metrics">





## Author
Ron Sweeney [sween](https://www.github.com/sween)

