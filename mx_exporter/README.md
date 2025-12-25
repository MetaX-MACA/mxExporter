# mx-exporter - MetaX Prometheus Data Exporter
The mx-exporter is a standalone app that can be run as a daemon, written in Python Language, that exports MetaX GPU metrics to the Prometheus server. The mx-exporter uses MXSML C-Library for its data acquisition. The exporter and the MXSML library have a [PYTHON binding] that provides an interface between the MXSML C,C++ library and the PYTHON exporter code.

## Run as python application

```
$ python3 -m mx_exporter -p <port> -i <interval> -c <config_file>
```
port: http listen port, default:8000
interval: Metrics gathering interval, default:10000ms
config_file: Metrics configuration file in CSV format

if config file is not set, the program will try to search `default-counters.csv` from following path:
    "/opt/maca/etc", "/opt/mxn100/etc", current working dir, python file dir

## Access Kubelet pod resources
if you want to export pod resources, you need to run as root.
