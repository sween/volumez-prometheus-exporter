# Volumez Prometheus Exporter
Export [Volumez](https://volumez.com/) API Data as prometheus metrics.

<img src="https://github.com/sween/volumez-prometheus-exporter/raw/main/assets/volumez-prometheus-exporter.png" alt="Volumez Metrics">

Uses the [Volumez Rest API](https://volumez.com/static/swagger.html) 


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
kubectl apply -f deploy/* -n volumez
```

You should see the deployment running on the cluster, explore the services to see how to reach the prometheus endpoint, in this case MetalLB.

<pic1>

### Metric Exported
At this point, not the most exhaustive list, but now we iterate.

<pic2>




## Author
Ron Sweeney [sween](https://www.github.com/sween)

