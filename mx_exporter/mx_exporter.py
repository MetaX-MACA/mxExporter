#!/usr/bin/env python3

"""
Copyright © 2024 MetaX Integrated Circuits (Shanghai) Co., Ltd. All Rights Reserved.

This software and associated documentation files (hereinafter collectively referred to as
"Software") is a proprietary commercial software developed by MetaX Integrated Circuits
(Shanghai) Co., Ltd. and/or its affiliates (hereinafter collectively referred to as “MetaX”).
The information presented in the Software belongs to MetaX. Without prior written permission
from MetaX, no entity or individual has the right to obtain a copy of the Software to deal in
the Software, including but not limited to use, copy, modify, merge, disclose, publish,
distribute, sublicense, and/or sell copies of the Software or substantial portions of the Software.

The Software is provided for reference only, without warranty of any kind, either express or
implied, including but not limited to the warranty of merchantability, fitness for any purpose
and/or noninfringement. In no case shall MetaX be liable for any claim, damage or other liability
arising from, out of or in connection with the Software.

If the Software need to be used in conjunction with any third-party software or open source
software, the rights to the third-party software or open source software still belong to the
copyright owners. For details, please refer to the respective notices or licenses. Please comply
with the provisions of the relevant notices or licenses. If the open source software licenses
additionally require the disposal of rights related to this Software, please contact MetaX
immediately and obtain MetaX 's written consent.

MetaX reserves the right, at its sole discretion, to change, modify, add or remove portions of the
Software, at any time. MetaX reserves all the right for the final explanation.
"""

import time
import os.path
import csv
import socket
import threading
from typing import Optional
from datetime import datetime
from prometheus_client import CollectorRegistry, Gauge
from mx_exporter.gpu_monitor import GpuMonitor
from mx_exporter.ib_metrics import IBMonitor, BnxtMonitor
from mx_exporter.kubernetes import get_pod_resource, PodInfo
from mx_exporter.log_monitor import KernelLogMonitor,SysLogMonitor
from collections import defaultdict

old_print = print
def timestamp_print(*args, **kwargs):
    old_print(datetime.now(), "MxCollector", *args, **kwargs)
print = timestamp_print


class MxCollector(object):

    def __init__(self, config_file, registry: Optional[CollectorRegistry] = None, gather_interval = 10,
            ib_monitor_flag = 0, mount_point = ""):

        if registry is not None:
            registry.register(self)

        self.lock = threading.Lock()
        self.init_members(gather_interval, ib_monitor_flag)
        self.init_required_metrics(config_file, self.metrics_supported)

        self.gpu_monitor.start(self.metrics_required.keys())

        if any(metric in self.metrics_required for metric in self.kernel_log_monitor.get_supported_metrics()):
            self.kernel_log_monitor.start(mount_point)

        if any(metric in self.metrics_required for metric in self.sys_log_monitor.get_supported_metrics()):
            self.sys_log_monitor.start(mount_point)

    def describe(self):
        return []

    def init_members(self, gather_interval, ib_monitor_flag):
        self.ib_monitor_flag = ib_monitor_flag

        # device uuid : pod info
        self.device_pod_map = {}
        # bdfid : device id
        self.bdf_device_map = {}
        # (device id, die id) : device info
        self.device_info_map = {}

        # K8S-745, common labels number is greater than 1 when over-subscription
        # 1. (device id, die id) : [[common labels1], [common lables2], ...]
        # 2. (device id) : [[common labels1], [common lables2], ...]
        self.common_labels = defaultdict(list)

        # (device id, sgpu id) : sgpu info
        self.all_sgpu_info = {}
        # (device id, sgpu id) : sgpu pod register id
        self.sgpu_pod_register_id = {}

        self.sgpu_labels = {}

        # required metrics in config file
        self.metrics_required = {}

        self.metric_types = ["Gauge", "Counter", "Summary", "Histogram", "Info"]

        self.gpu_monitor = GpuMonitor(gather_interval)
        self.kernel_log_monitor = KernelLogMonitor()
        self.sys_log_monitor = SysLogMonitor()

        self.metrics_supported = self.gpu_monitor.get_supported_metrics() \
                + self.kernel_log_monitor.get_supported_metrics() + self.sys_log_monitor.get_supported_metrics()

        if self.ib_monitor_flag:
            self.ib_monitor = IBMonitor()
            self.bnxt_monitor = BnxtMonitor()

        self.host_name = self.get_host_name()

        # basic metrics : device type, bios version, driver version
        self.devType = Gauge("mx_device_type", "Device type", ["deviceId", "dieId", "deviceType", "uuid"])
        self.biosVersion = Gauge("mx_bios_ver", "Bios version", ["deviceId", "dieId", "bios"])
        self.driverVersion = Gauge("mx_driver_ver", "Driver version", ["deviceId", "dieId", "driver"])


    def collect(self):
        with self.lock:
            print("Export metrics")
            time.sleep(0.05) # avoid 2nd thread clear metrics before 1st send response
            self.device_pod_map = get_pod_resource()
            self.device_info_map = self.gpu_monitor.get_device_info_map()
            self.all_sgpu_info, self.sgpu_pod_register_id = self.gpu_monitor.get_sgpu_info_dict()

            self.generate_common_labels()
            gpu_data = self.gpu_monitor.get_gpu_data()
            self.generate_sgpu_labels()
            sgpu_data = self.gpu_monitor.get_sgpu_data()

            for metric_id, metric in self.metrics_required.items():
                metric.clear()
                for device_key, value in gpu_data.items():
                    if metric_id in value:
                        self.export_common(device_key, metric, value[metric_id])

                for (device_id, sgpu_id), value in sgpu_data.items():
                    if metric_id in value:
                        self.export_sgpu_info(device_id, sgpu_id, metric, value[metric_id])

            self.export_device_basic_metrics()
            self.export_server_info()
            self.export_log_info()

            if self.ib_monitor_flag:
                self.ib_monitor.export(self.host_name)
                self.bnxt_monitor.export(self.host_name)

            return []


    def init_required_metrics(self, config_file, metrics_supported):
        with open(config_file, 'r') as file_handle:
            reader=csv.reader(file_handle)
            for row in reader:
                print(row)
                if not self.is_row_valid(row, metrics_supported):
                    continue

                # metric id,metric type,metric name,metric description,label1,label2,...
                # metric type is also metric function, eg, Gauge
                metric_id = row[0]
                metric_func = globals()[row[1]]
                metric_name = row[2]
                metric_description = row[3]
                metric_labels = row[4:]
                try:
                    self.metrics_required[metric_id] = metric_func(metric_name, metric_description, metric_labels)
                except Exception as e:
                    print("Create metric exception: %s" % (e))


    def is_row_valid(self, row, metrics_supported):
        if len(row) == 0:
            print("Skip empty line")
            return False

        if row[0][0] == '#':
            print("Skip comment line")
            return False

        if len(row) < 4:
            print("Skip invalid row len")
            return False

        if row[1] not in self.metric_types:
            print("Skip invalid metric type: %s" % row[0])
            return False

        metric_id = row[0]
        if metric_id not in metrics_supported:
            print("Skip not support metric id: %s" % metric_id)
            return False

        return True


    def export_device_basic_metrics(self):
        self.devType.clear()
        self.biosVersion.clear()
        self.driverVersion.clear()
        for (device_id, die_id), device_info in self.device_info_map.items():
            self.devType.labels(device_id, die_id, device_info.name, device_info.uuid).set(1)
            self.biosVersion.labels(device_id, die_id, device_info.bios_version).set(1)
            self.driverVersion.labels(device_id, die_id, device_info.driver_version).set(1)

        if 'topo_info' in self.metrics_required:
            for (device_id, die_id), device_info in self.device_info_map.items():
                for common_labels in self.common_labels[(device_id, die_id)]:
                    self.gauge_labels_set(self.metrics_required['topo_info'], [device_info.topo_id,
                        device_info.socket_id, device_info.die_id, *common_labels], 1)


    def get_sgpu_register_id(self, uuid):
        sgpu_target_dir = "/run/metax/device-plugin/sgpu/"
        sgpu_target_file = os.path.join(sgpu_target_dir, uuid)
        if not os.path.exists(sgpu_target_file):
                return ""

        try:
            with open(sgpu_target_file, "r") as f:
                content = f.read().strip()
        except:
            return ""

        pairs = content.split(";")
        for pair in pairs:
            if "=" in pair:
                key, value = pair.split("=", 1)
                if key.strip() == "id":
                    return value.strip()

        return ""


    def get_oversubscription_register_id(self, uuid):
        register_ids = []
        for key in self.device_pod_map:
            key_str = str(key)
            if uuid in key_str: # pod register_id format: "${native gpu uuid}::${index}"
                register_ids.append(key)

        return register_ids

    def generate_common_labels(self):
        self.common_labels.clear()
        for (device_id, die_id), device_info in self.device_info_map.items():
            pod_info_list = []
            if device_info.uuid in self.device_pod_map.keys():
                pod_info = self.device_pod_map.get(device_info.uuid, PodInfo())
                pod_info_list.append(pod_info)
            elif device_info.uuid: # k8s-480, try to get device-plugin register
                register_ids = self.get_sgpu_register_id(device_info.uuid)
                # k8s-745 support gpu oversubscription
                if not register_ids:
                    register_ids = self.get_oversubscription_register_id(device_info.uuid)

                for register_id in register_ids:
                    pod_info = self.device_pod_map.get(register_id, PodInfo())
                    if pod_info:
                        pod_info_list.append(pod_info)

            if not pod_info_list:
                pod_info_list.append(PodInfo("", "", "", device_id))

            for pod_info in pod_info_list:
                new_element = [device_id, device_info.uuid, pod_info.pod_name, pod_info.pod_namespace,
                    pod_info.container_name, self.host_name, device_info.driver_version, device_info.bios_version, device_info.name, die_id]

                if new_element not in self.common_labels[(device_id, die_id)]:
                    self.common_labels[(device_id, die_id)].append([device_id, device_info.uuid, pod_info.pod_name, pod_info.pod_namespace,
                    pod_info.container_name, self.host_name, device_info.driver_version, device_info.bios_version, device_info.name, die_id])

            # label for pcie, board power, etc.
            if not device_id in self.common_labels:
                for pod_info in pod_info_list:
                    self.common_labels[device_id].append([device_id, device_info.uuid, pod_info.pod_name, pod_info.pod_namespace,
                        pod_info.container_name, self.host_name, device_info.driver_version, device_info.bios_version, device_info.name])


    def export_server_info(self):
        server_data = self.gpu_monitor.get_server_data()
        metric_id = 'server_info'
        if metric_id in self.metrics_required:
            metric_gauge = self.metrics_required[metric_id]
            for kind, value in server_data.get(metric_id, {}).items():
                for uuid, vvalue in value.items():
                    self.gauge_labels_set(metric_gauge, [kind, uuid, self.host_name], vvalue)

        metric_id = 'server_conn_status'
        if metric_id in self.metrics_required:
            metric_gauge = self.metrics_required[metric_id]
            for uuid,conn_status in server_data.get(metric_id, {}).items():
                self.gauge_labels_set(metric_gauge, [uuid, self.host_name], conn_status)


    def export_log_info(self):
        self.bdf_device_map = self.gpu_monitor.get_bdf_device_map()

        if 'driver_log_errors' in self.metrics_required:
            self.export_kernel_log_info(self.metrics_required['driver_log_errors'])

        if 'driver_eid_errors' in self.metrics_required:
            self.export_driver_eid_errors(self.metrics_required['driver_eid_errors'])

        if 'sdk_eid_errors' in self.metrics_required:
            self.export_sdk_eid_errors(self.metrics_required['sdk_eid_errors'])

        return


    def export_common(self, device_key, metric_gauge, metric_data):
        for common_labels in self.common_labels[device_key]:
            if isinstance(metric_data, dict):
                for key, value in metric_data.items():
                    if isinstance(value, dict):  # mxlk bw / pcie event
                        for vkey,vvalue in value.items():
                            self.gauge_labels_set(metric_gauge, [key, vkey, *common_labels], vvalue)
                    else:
                        self.gauge_labels_set(metric_gauge, [key, *common_labels], value)
            else:
                self.gauge_labels_set(metric_gauge, common_labels, metric_data)


    def generate_sgpu_labels(self):
        for (device_id, sgpu_id), sgpu_info in self.all_sgpu_info.items():
            uuid = sgpu_info.uuid.decode('ASCII')
            pod_uuid = self.sgpu_pod_register_id[(device_id, sgpu_id)]
            pod_info = self.device_pod_map.get(pod_uuid, PodInfo())
            for (id, _), device_info in self.device_info_map.items():
                if device_id != id:
                    continue
                self.sgpu_labels[(device_id, sgpu_id)] = [device_id, sgpu_id, sgpu_info.minor, uuid, pod_info.pod_name,
                    pod_info.pod_namespace, pod_info.container_name, self.host_name,
                    device_info.driver_version, device_info.bios_version, device_info.name]


    def export_sgpu_info(self, device_id, sgpu_id, metric_gauge, metric_data):
        self.gauge_labels_set(metric_gauge, self.sgpu_labels[(device_id, sgpu_id)], metric_data)


    def export_kernel_log_info(self, metric):
        metric.clear()
        logs = self.kernel_log_monitor.get_kernel_error_info()
        for log in logs:
            device_id = self.bdf_device_map.get(log.bdf_id, -1)
            if device_id in self.common_labels:
                for common_labels in self.common_labels[(device_id, log.die_id)]:
                    self.gauge_labels_inc(metric, [log.submodule, log.log_level, *common_labels])
            else:
                print("export_kernel_log_info Invalid device_id %d" % device_id)
                print(log)


    def export_driver_eid_errors(self, metric):
        metric.clear()
        driver_eid_errors = self.kernel_log_monitor.get_eid_error_info()
        for err in driver_eid_errors:
            device_id = self.bdf_device_map.get(err.bdf_id, -1)
            if device_id in self.common_labels:
                for common_labels in self.common_labels[(device_id, err.die_id)]:
                    self.gauge_labels_set(metric, [err.eid_info, *common_labels], err.eid)
            else:
                print("export_driver_eid_errors Invalid device_id %d" % device_id)
                print(err)


    def export_sdk_eid_errors(self, metric):
        metric.clear()
        sdk_eid_errors = self.sys_log_monitor.get_eid_error_info()
        for err in sdk_eid_errors:
            device_id = self.bdf_device_map.get(err.bdf_id, -1) # ToDo inaccurate for double die device
            if device_id in self.common_labels:
                for common_labels in self.common_labels[(device_id,0)]:
                    self.gauge_labels_set(metric, [err.sdk_version, err.eid_info, *common_labels], err.eid)
            else:
                print("export_sdk_eid_errors Invalid device_id %d" % device_id)
                print(err)


    def get_host_name(self):
        if "NODE_NAME" in os.environ:
            return os.environ.get("NODE_NAME")
        else:
            host_name = os.environ.get("HOSTNAME")
            if host_name != None:
                return host_name

            try:
                host_name = socket.gethostname()
            except Exception as e:
                print("socket.gethostname exception %s" % (e))
                host_name = ""

            return host_name

    def gauge_labels_set(self, gauge, labels, value):
        configured_label_count = len(gauge._labelnames)
        current_label_count = len(labels)

        if(current_label_count >= configured_label_count):
            gauge.labels(*labels[:configured_label_count]).set(value)
        else:
            support_labels = labels + ["NA" for _ in range(configured_label_count - current_label_count)]
            gauge.labels(*support_labels).set(value)

    def gauge_labels_inc(self, gauge, labels):
        configured_label_count = len(gauge._labelnames)
        current_label_count = len(labels)

        if(current_label_count >= configured_label_count):
            gauge.labels(*labels[:configured_label_count]).inc()
        else:
            support_labels = labels + ["NA" for _ in range(configured_label_count - current_label_count)]
            gauge.labels(*support_labels).inc()
