# mx-exporter - MetaX Prometheus Data Exporter
The mx-exporter is a standalone app that can be run as a daemon, written in Python Language, that exports MetaX GPU metrics to the Prometheus server. The mx-exporter uses MXSML C-Library for its data acquisition. The exporter and the MXSML library have a [PYTHON binding] that provides an interface between the MXSML C,C++ library and the PYTHON exporter code.

## Build docker image

```
$ sudo make mxc MACAVER=xxxx ARCH_L=amd64
```

## Run as Docker

```
$ sudo docker run -d --name=mx-exporter --device=/dev/dri -p 0.0.0.0:<host port>:8000 <image name>
```
Add "-v /var/lib/kubelet/pod-resources:/var/lib/kubelet/pod-resources" to support export pod resources.

if you want to change port and process interval settings, use this:
```
$ sudo docker run -d --name=mx-exporter --device=/dev/dri -p 0.0.0.0:<host port>:<http port> <image name> -p <http port> -i <interval>
```

if you want to use self defined counter configuration file on host, here's an example:
```
$ sudo docker run -d --name=mx-exporter --device=/dev/dri -p 0.0.0.0:<host port>:<http port> -v <new config file>:/work/counters.csv <image name> -c /work/counters.csv
```

## Run as python application

```
$ python3 -m mx_exporter -p <port> -i <interval> -c <config_file>
```
port: http listen port, default:8000
interval: Metrics gathering interval, default:10000ms
config_file: Metrics configuration file in CSV format, default: ./default-counters.csv

## Deployment

## Deploy with kubernetes
All the deployment configuration files stored in the `deployment` folder
1. Create Namespace
   ```
   kubectl apply -f namespace.yaml
   ```
2. Startup Data Exporter as Daemonset
    ```
    cd mx-data-exporter
    kubectl apply -f .
    ```
3. Startup Prometheus
    ```
    cd prometheus
    kubectl apply -f .
    ```
4. Startup Grafana
    ```
    cd grafana
    kubectl apply -f .
    ```

## Deploy with Helm
Helm install using package
    ```
    cd mx-exporter/deployment/mx-exporter/helm; helm install metax-mx-exporter mx-exporter \
        --create-namespace -n metax-monitor \
        --set image.repository=xxxx \
        --set image.tag=x.x.x \
    ```
Options:
    service.port - set container port, default is 8000
    gatherInterval - unit: ms, default is 10000

