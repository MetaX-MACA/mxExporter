# mx-exporter - MetaX Prometheus Data Exporter
The mx-exporter is a standalone app that can be run as a daemon, written in Python Language, that exports MetaX GPU metrics to the Prometheus server.

## Run as Docker

### Use script
```
$ sudo bash start_mxexporter.sh --name=mx-exporter
```
Use `bash start_mxexporter.sh -h` to see more details

### Use docker command
```
$ sudo docker run -d --name=mx-exporter --device=/dev/dri -p 0.0.0.0:<host port>:8000 <image name>
```
<host port>: http port on host

Add "-v /var/lib/kubelet/pod-resources:/var/lib/kubelet/pod-resources" to support export k8s pod resources.

## Settings
if you want to change port and process interval settings, use this:
```
$ sudo docker run -d --name=mx-exporter --device=/dev/dri -p 0.0.0.0:<host port>:<http port> <image name> -p <http port> -i <interval>
```
<http port>: http port on docker
<interval>: mx-exporter process interval in ms

if you want to use self defined counter configuration file on host, here's an example:
```
$ sudo docker run -d --name=mx-exporter --device=/dev/dri -p 0.0.0.0:<host port>:<http port> -v <new config file>:/work/counters.csv <image name> -c /work/counters.csv
```
<new config file>: modify 'config/default-counters.csv' as your need

## helm chart deployment
Helm install local package as example:
    ```
    helm install metax-mx-exporter ./mx-exporter-0.1.0.tgz \
        --create-namespace -n metax-monitor \
        --set image.repository=xxxx \
        --set image.tag=x.x.x \
    ```
Options:
    service.port - set container port, default is 8000
    gatherInterval - set gather metrics data interval, unit: ms, default is 10000ms

