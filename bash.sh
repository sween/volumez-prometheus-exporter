docker build -t volumez-prometheus-exporter .
docker image tag volumez-prometheus-exporter sween/volumez-prometheus-exporter:latest
docker push sween/volumez-prometheus-exporter:latest
