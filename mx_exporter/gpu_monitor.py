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
import threading
from functools import partial
from datetime import datetime
from copy import deepcopy

from mx_exporter.mxsml_function import *


old_print = print
def timestamp_print(*args, **kwargs):
    old_print(datetime.now(), "GpuMonitor", *args, **kwargs)
print = timestamp_print


class Metric:
    def __init__(self, id, for_native, for_pf, for_vf, for_sgpu, for_mxn, for_mxc, func):
        self.id = id
        self.for_native = for_native
        self.for_pf = for_pf
        self.for_vf = for_vf
        self.for_sgpu = for_sgpu
        self.for_mxn = for_mxn
        self.for_mxc = for_mxc
        self.func = func


class DeviceInfo:
    def __init__(self, device_info, driver_version, bios_version, topo_id, socket_id, die_id):
        self.device_name_suffix_map = {
            MxSmlDeviceVirtualizationMode.MXSML_Virtualization_Mode_None : "",
            MxSmlDeviceVirtualizationMode.MXSML_Virtualization_Mode_Pf : " PF",
            MxSmlDeviceVirtualizationMode.MXSML_Virtualization_Mode_Vf : " VF",
        }

        self.id = device_info.deviceId
        self.mode = device_info.mode
        self.uuid = device_info.uuid.decode('ASCII')
        self.bdfid = device_info.bdfId.decode('ASCII')
        self.name = device_info.deviceName.decode('ASCII') + self.device_name_suffix_map[self.mode]
        self.driver_version = driver_version
        self.bios_version = bios_version
        self.topo_id = topo_id
        self.socket_id = socket_id
        self.die_id = die_id


class ServerInfo:
    def __init__(self, local_uuid, remote_uuids, conn_status):
        self.local_uuid = local_uuid
        self.remote_uuids = remote_uuids
        self.conn_status = conn_status


class GpuMonitor:
    def __init__(self, gather_interval = 10):
        self.init_members(gather_interval)
        self.initialize()
        self.generate_supported_metrics()


    def start(self, metrics_required):
        for metric_id in metrics_required:
            if metric_id not in self.metrics_supported:
                print("Skip not support metric %s" % metric_id)
            else:
                if self.metric_map[metric_id].for_sgpu == 1:
                    self.sgpu_metrics_required.append(metric_id)
                else:
                    self.metrics_required_original.append(metric_id)

        self.metrics_required = deepcopy(self.metrics_required_original)

        t = threading.Thread(target=self.monitor, args=(), daemon=True)
        t.start()


    def monitor(self):
        while True:
            start = time.time()

            self.monitor_native_devices()
            self.monitor_pf_devices()
            self.monitor_vf_devices()
            self.monitor_sgpu_devices()
            self.monitor_server()

            elapsed_time = time.time() - start

            if elapsed_time < self.gather_interval:
                time.sleep(self.gather_interval - elapsed_time)
            else:
                print("error elapsed_time %d" % elapsed_time)

            if self.need_init == True:
                self.initialize()


    def get_server_data(self):
        with self.lock:
            data = deepcopy(self.server_data)
        return data


    def get_gpu_data(self):
        with self.lock:
            data = deepcopy(self.gpu_data)
        return data


    def get_sgpu_data(self):
        with self.lock:
            data = deepcopy(self.sgpu_data)
        return data


    def update_server_data(self, metric_id, data):
        with self.lock:
            self.server_data[metric_id] = data


    def update_die_data(self, device_id, die_id, metric_id, data):
        with self.lock:
            self.gpu_data[(device_id, die_id)][metric_id] = data


    def update_gpu_data(self, device_id, metric_id, data):
        with self.lock:
            self.gpu_data[device_id][metric_id] = data


    def update_sgpu_data(self, device_id, sgpu_id, metric_id, data):
        with self.lock:
            if (device_id, sgpu_id) not in self.sgpu_data:
                self.sgpu_data[(device_id, sgpu_id)] = ({metric_id : data})
            else:
                self.sgpu_data[(device_id, sgpu_id)].update({metric_id : data})


    def generate_supported_metrics(self):
        for metric_id,metric in self.metric_map.items():
            if (self.product == "MXN" and metric.for_mxn == 1) \
               or (self.product == "MXC" and metric.for_mxc == 1):
                self.metrics_supported.append(metric_id)

    def remove_notsupported_metrics(self, metric_id):
        if metric_id in self.metrics_required:
            print("Remove not supported metric %s" % metric_id)
            self.metrics_required.remove(metric_id)

    def get_supported_metrics(self):
        return self.metrics_supported

    def get_device_info_map(self):
        return self.device_info_map

    def get_sgpu_info_dict(self):
        return self.all_sgpu_info, self.sgpu_pod_uuid_map

    def get_bdf_device_map(self):
        return self.bdf_device_map

    def initialize(self):
        self.clear()

        while True:
            ret = mxsml_init()
            if ret != MxSmlReturn.MXSML_Success:
                print("first mxSmlInit failed: %s" % (mxsml_get_error_string(ret)))
                time.sleep(30)
            else:
                print("first mxSmlInit success")
                gpu_num1 = mxSmlGetDeviceCount()
                print("Device number1: %d" % (gpu_num1))

                time.sleep(30)

                ret = mxsml_init()
                if ret != MxSmlReturn.MXSML_Success:
                    print("second mxSmlInit failed: %s" % (mxsml_get_error_string(ret)))
                    time.sleep(30)
                else:
                    print("second mxSmlInit success")
                    gpu_num2 = mxSmlGetDeviceCount()
                    print("Device number2: %d" % (gpu_num2))
                    if gpu_num1 == gpu_num2:
                        print("initialize success")
                        break
                    else:
                        print("initialize failed, gpu number is not equal")
                        time.sleep(30)

        self.need_init = False
        self.metrics_required = deepcopy(self.metrics_required_original)
        self.find_all_devices()

    def clear(self):
        self.gpu_data.clear()
        self.native_ids.clear()
        self.pf_ids.clear()
        self.vf_ids.clear()
        self.bdf_device_map.clear()
        self.device_info_map.clear()
        self.metrics_required.clear()
        self.clear_sgpu()
        self.clear_server_data()

    def clear_sgpu(self): # sgpu is dynamic
        self.sgpu_data.clear()
        self.all_sgpu_info.clear()
        self.sgpu_pod_uuid_map.clear()
        self.sgpu_memory_info.clear()

    def clear_server_data(self):
        self.server_data.clear()
        self.mxlk_status = 1

    def monitor_native_devices(self):
        for id in self.native_ids:
            print("Get data GPU#%d " %(id))
            self.get_memory_info(id)
            self.get_pcie_info(id)
            self.get_pcie_bridge_info(id)
            self.get_mxlk_info(id)

            for metric_id in self.metrics_required:
                if self.metric_map[metric_id].for_native == 1:
                    self.metric_map[metric_id].func(id, metric_id)


    def monitor_pf_devices(self):
        for id in self.pf_ids:
            print("Get data GPU#%d" %(id))
            self.get_pcie_info(id)
            self.get_pcie_bridge_info(id)

            for metric_id in self.metrics_required:
                if self.metric_map[metric_id].for_pf == 1:
                    self.metric_map[metric_id].func(id, metric_id)


    def monitor_vf_devices(self):
        for id in self.vf_ids:
            print("Get data VGPU#%d" %(id))
            self.get_memory_info(id)

            for metric_id in self.metrics_required:
                if self.metric_map[metric_id].for_vf == 1:
                    self.metric_map[metric_id].func(id, metric_id)


    def monitor_sgpu_devices(self):
        self.clear_sgpu()
        sgpu_memory_toggle = 0
        if any(map(lambda metric: metric in self.sgpu_metrics_required,
            ['sgpu_memory_total', 'sgpu_memory_used', 'sgpu_memory_free'])):
            sgpu_memory_toggle = 1

        if len(self.sgpu_metrics_required) != 0:
            for id in self.native_ids:
                sgpu_count = mxsml_get_sgpu_count(id)
                if sgpu_count == -1 or sgpu_count == 0:
                    # Skip if the version of mxsmlBindings.py and libmxsml.so is too low for sgpu mode
                    continue

                print("Get sgpu data GPU#%d(sgpu count:%d)" %(id, sgpu_count))
                self.get_sgpu_info(id, sgpu_count)
                if sgpu_memory_toggle:
                    self.get_sgpu_memory_info(id)

                for metric_id in self.sgpu_metrics_required:
                    self.metric_map[metric_id].func(id, metric_id)

    def monitor_server(self):
        server_metrics = ['server_info', 'server_conn_status']

        is_required = False
        for metric_id in server_metrics:
            if metric_id in self.metrics_required:
                is_required = True
                break

        if not is_required:
            return

        ret = self.get_server_info()
        if ret != MxSmlReturn.MXSML_Success:
            return

        for metric_id in server_metrics:
            if metric_id in self.metrics_required:
                self.metric_map[metric_id].func(metric_id)

        self.mxlk_status = 1 # init in each period


    def init_members(self, gather_interval):
        self.server_data = {}

        # (device id, die id) : {metric id : value}
        self.gpu_data = {}

        # (device id, sgpu id) : {metric id : value}
        self.sgpu_data = {}

        self.lock = threading.Lock()

        self.metrics_supported = []  # supported metrics per product
        self.metrics_required_original = [] # store original required metrics, must not update
        self.metrics_required = []  # user required metrics, remove if not support
        self.sgpu_metrics_required = []  # user required sgpu metrics

        self.gather_interval = gather_interval  # seconds

        # store device ids
        self.native_ids = []
        self.pf_ids = []
        self.vf_ids = []

        # bdfid : device id
        self.bdf_device_map = {}
        # (device id, die id) : device info
        self.device_info_map = {}
        # device id : die count
        self.device_die_count_map = {}
        # server mxlk status, 1 - health, 0 - unhealthy, set as 0 if any mxlk link is abnormal
        # need initialized with 1 in each period
        self.mxlk_status = 1

        # store device info each time to avoid calling apis repeatedly
        self.memory_info_map = {} # {die_id : MxSmlMemoryInfo()}
        self.mxlk_info = MxSmlMetaXLinkInfo()
        self.pcie_info = MxSmlPcieInfo()
        self.pcie_bridge_info = MxSmlPcieInfo()
        self.all_sgpu_info = {} # { (device_id, sgpu_id) : MxSmlSgpuInfo() }
        self.sgpu_pod_uuid_map = {} # { (device_id, sgpu_id) : pod_register_uuid }
        self.sgpu_memory_info = {} # { (device_id, sgpu_id) : MxSmlSgpuMemoryInfo() }

        self.metric_map = {
            # metric id  : (id, for_native, for_pf, for_vf, for_sgpu, for_mxn, for_mxc, func)
            # Temperature
            "chip_hotspot_temp"   : Metric("chip_hotspot_temp",    1, 1, 0, 0, 1, 1, partial(self.get_temperature, MxSmlTemperatureSensors.MXSML_Temperature_Hotspot)),
            "chip_hbm_temp"       : Metric("chip_hbm_temp",        1, 1, 0, 0, 0, 1, partial(self.get_temperature, MxSmlTemperatureSensors.MXSML_Temperature_Hbm)),
            "board_soc_temp"      : Metric("board_soc_temp",       1, 1, 0, 0, 1, 1, partial(self.get_temperature, MxSmlTemperatureSensors.MXSML_Temperature_Soc)),
            "board_core_temp"     : Metric("board_core_temp",      1, 1, 0, 0, 1, 1, partial(self.get_temperature, MxSmlTemperatureSensors.MXSML_Temperature_Core)),
            "optical_module_temp" : Metric("optical_module_temp",  1, 1, 0, 0, 0, 1, self.get_om_temperature),
            # Usage
            "dla_usage"    : Metric("dla_usage",     1, 1, 1, 0, 1, 0, partial(self.get_gpu_usage, MxSmlUsageIp.MXSML_Usage_Dla)),
            "g2d_usage"    : Metric("g2d_usage",     1, 1, 1, 0, 1, 0, partial(self.get_gpu_usage, MxSmlUsageIp.MXSML_Usage_G2d)),
            "gpu_usage"    : Metric("gpu_usage",     1, 1, 1, 0, 0, 1, partial(self.get_gpu_usage, MxSmlUsageIp.MXSML_Usage_Xcore)),
            "vpue_usage"   : Metric("vpue_usage",    1, 1, 1, 0, 1, 1, partial(self.get_gpu_usage, MxSmlUsageIp.MXSML_Usage_Vpue)),
            "vpud_usage"   : Metric("vpud_usage",    1, 1, 1, 0, 1, 1, partial(self.get_gpu_usage, MxSmlUsageIp.MXSML_Usage_Vpud)),
            "memory_usage" : Metric("memory_usage",  1, 0, 1, 0, 1, 1, self.get_memory_usage),
            "memory_total" : Metric("memory_total",  1, 0, 1, 0, 1, 1, self.get_memory_total),
            "memory_used"  : Metric("memory_used",   1, 0, 1, 0, 1, 1, self.get_memory_used),
            # Power
            "board_power"  : Metric("board_power",   1, 1, 0, 0, 1, 1, self.get_board_power),
            "pmbus_power"  : Metric("pmbus_power",   1, 1, 0, 0, 1, 1, self.get_pmbus_power),
            # Clocks
            "dla_clock"    : Metric("dla_clock",     1, 1, 0, 0, 1, 0, partial(self.get_clocks, MxSmlClockIp.MXSML_Clock_Dla)),
            "g2d_clock"    : Metric("g2d_clock",     1, 1, 0, 0, 1, 0, partial(self.get_clocks, MxSmlClockIp.MXSML_Clock_G2D)),
            "gpu_clock"    : Metric("gpu_clock",     1, 1, 0, 0, 0, 1, partial(self.get_clocks, MxSmlClockIp.MXSML_Clock_Xcore)),
            "vpue_clock"   : Metric("vpue_clock",    1, 1, 0, 0, 1, 1, partial(self.get_clocks, MxSmlClockIp.MXSML_Clock_Vpue)),
            "vpud_clock"   : Metric("vpud_clock",    1, 1, 0, 0, 1, 1, partial(self.get_clocks, MxSmlClockIp.MXSML_Clock_Vpud)),
            "mem_clock"    : Metric("mem_clock",     1, 1, 0, 0, 1, 1, self.get_mem_clock),
            # Bandwidth
            "pcie_bw"      : Metric("pcie_bw",       1, 1, 0, 0, 1, 1, self.get_pcie_throughput),
            "mxlk_bw"      : Metric("mxlk_bw",       1, 0, 0, 0, 0, 1, self.get_mxlk_bandwidth),
            "hbm_bw"       : Metric("hbm_bw",        1, 1, 0, 0, 1, 1, self.get_hbm_throughput),
            "eth_bw"       : Metric("eth_bw",        1, 1, 0, 0, 0, 1, self.get_eth_throughput),
            # Dpm
            "dla_dpm_level"  : Metric("dla_dpm_level",   1, 1, 0, 0, 1, 0, partial(self.get_dpm_level, MxSmlDpmIp.MXSML_Dpm_Dla)),
            "xcore_dpm_level": Metric("xcore_dpm_level", 1, 1, 0, 0, 0, 1, partial(self.get_dpm_level, MxSmlDpmIp.MXSML_Dpm_Xcore)),
            # pcie and mxlk info
            "pcie_speed"        : Metric("pcie_speed",        1, 1, 0, 0, 1, 1, self.get_pcie_speed),
            "pcie_width"        : Metric("pcie_width",        1, 1, 0, 0, 1, 1, self.get_pcie_width),
            "pcie_bridge_speed" : Metric("pcie_bridge_speed", 1, 1, 0, 0, 1, 1, self.get_pcie_bridge_speed),
            "pcie_bridge_width" : Metric("pcie_bridge_width", 1, 1, 0, 0, 1, 1, self.get_pcie_bridge_width),
            "mxlk_speed"        : Metric("mxlk_speed",        1, 0, 0, 0, 0, 1, self.get_mxlk_speed),
            "mxlk_width"        : Metric("mxlk_width",        1, 0, 0, 0, 0, 1, self.get_mxlk_width),
            "mxlk_traffic_total_bytes" : Metric("mxlk_traffic_total_bytes", 1, 0, 0, 0, 0, 1, self.get_mxlk_traffic_total_bytes),
            "mxlk_aer_count"           : Metric("mxlk_aer_count",           1, 0, 0, 0, 0, 1, self.get_mxlk_aer_count),
            "topo_info"    : Metric("topo_info",     0, 0, 0, 0, 0, 1, self.get_topo_info),
            # Process
            "process"      : Metric("process",       1, 0, 1, 0, 1, 1, self.get_process_info),
            # GPU state
            "gpu_state"    : Metric("gpu_state",     1, 0, 1, 0, 1, 1, self.get_gpu_state),
            # clock throttle reason
            "clk_thr"      : Metric("clk_thr",       1, 1, 0, 0, 0, 1, self.get_clock_throttle_reason),
            # ECC error counts
            "ecc_error_count": Metric("ecc_error_count", 1, 1, 0, 0, 0, 1, self.get_ecc_count),
            # sgpu info
            "sgpu_compute_quota" : Metric("sgpu_compute_quota",  0, 0, 0, 1, 0, 1, self.get_sgpu_compute_quota),
            "sgpu_usage"         : Metric("sgpu_usage",          0, 0, 0, 1, 0, 1, self.get_sgpu_usage),
            "sgpu_memory_total"  : Metric("sgpu_memory_total",   0, 0, 0, 1, 0, 1, self.get_sgpu_memory_total),
            "sgpu_memory_used"   : Metric("sgpu_memory_used",    0, 0, 0, 1, 0, 1, self.get_sgpu_memory_used),
            "sgpu_memory_free"   : Metric("sgpu_memory_free",    0, 0, 0, 1, 0, 1, self.get_sgpu_memory_free),
            # server info
            "server_info"        : Metric("server_info",        0, 0, 0, 0, 0, 1, self.get_server_uuid),
            "server_conn_status" : Metric("server_conn_status", 0, 0, 0, 0, 0, 1, self.get_server_conn_status),
            # pcie event aer_ue/aer_ce/synfld/dbe/mmio
            "pci_event"  : Metric("pci_event",   1, 1, 0, 0, 0, 1, self.get_pci_event),
            # ras
            "ras_count"  : Metric("ras_count",   1, 1, 0, 0, 0, 1, self.get_ras_count),
            "ras_status" : Metric("ras_status",  1, 1, 0, 0, 0, 1, self.get_ras_status)
        }


    def find_all_devices(self):
        gpu_num = mxSmlGetDeviceCount()
        print("mxSmlGetDeviceCount number: %d" % (gpu_num))

        if gpu_num > 64:
            self.need_init = True
            return

        for gpu_id in range(0, gpu_num):
            self.get_device_base_info(gpu_id)

        pf_num = mxSmlGetPfDeviceCount()
        print("mxSmlGetPfDeviceCount number: %d" %(pf_num))

        if pf_num > 16:
            self.need_init = True
            return

        for gpu_id in range(100, 100+pf_num):
            self.get_device_base_info(gpu_id)


    def get_device_base_info(self, gpu_id):
        device_info = MxSmlDeviceInfo()
        ret = mxSmlGetDeviceInfo(gpu_id, byref(device_info))
        if ret != MxSmlReturn.MXSML_Success:
            print("mxSmlGetDeviceInfo for GPU#%d failed: %s" % (gpu_id, mxsml_get_error_string(ret)))
            return

        print("mxSmlGetDeviceInfo for GPU#%d device name: %s" % (gpu_id, device_info.deviceName.decode('ASCII')))
        if device_info.mode == MxSmlDeviceVirtualizationMode.MXSML_Virtualization_Mode_None:
            self.native_ids.append(gpu_id)
        elif device_info.mode == MxSmlDeviceVirtualizationMode.MXSML_Virtualization_Mode_Pf:
            self.pf_ids.append(gpu_id)
        else:
            self.vf_ids.append(gpu_id)

        ret, die_count = mxsml_get_device_die_count(gpu_id)
        if ret != MxSmlReturn.MXSML_Success:
            print("mxSmlGetDeviceDieCount for GPU#%d failed: %s" % (gpu_id, mxsml_get_error_string(ret)))
            die_count = 0
        self.device_die_count_map[gpu_id] = die_count

        self.bdf_device_map[device_info.bdfId.decode('ASCII')] = gpu_id
        self.gpu_data[gpu_id] = {}

        for die_id in range(0, die_count):
            self.gpu_data[(gpu_id, die_id)] = {}
            self.store_device_info(device_info, die_id)
            self.set_product_type(device_info.brand)


    def set_product_type(self, device_brand):
        if device_brand == MxSmlDeviceBrand.MXSML_Brand_N:
            self.product = "MXN"
        else:
            self.product = "MXC"


    def store_device_info(self, device_info, die_id):
        self.device_info_map[(device_info.deviceId, die_id)] = DeviceInfo(
            device_info,
            self.get_version(device_info.deviceId, die_id, MxSmlVersionUnit.MXSML_Version_Driver),
            self.get_version(device_info.deviceId, die_id, MxSmlVersionUnit.MXSML_Version_Bios),
            *self.get_topo_info(device_info.deviceId, die_id),
        )


    def get_version(self, gpu_id, die_id, unit):
        ret, version = mxsml_get_die_version(gpu_id, die_id, unit)
        if ret != MxSmlReturn.MXSML_Success:
            print("mxSmlGetDeviceVersion for %d unit %d failed: %s" % (gpu_id, unit, mxsml_get_error_string(ret)))
            return 'unknown'
        return version


    def get_topo_info(self, device_id, die_id):
        ret, topo_info = mxsml_get_device_metaxlink_topo(device_id)
        if ret != MxSmlReturn.MXSML_Success:
            print("mxSmlGetMetaXLinkTopo failed: %s" % (mxsml_get_error_string(ret)))
            return -1,-1,-1

        return topo_info.topologyId, topo_info.socketId, die_id


    def get_device_die_range(self, device_id):
        return range(0, self.device_die_count_map[device_id])


    def get_memory_info(self, device_id):
        self.memory_info_map.clear()
        if any(map(lambda metric: metric in self.metrics_required, ['memory_usage', 'memory_total', 'memory_used'])):
            for die_id in self.get_device_die_range(device_id):
                ret, info = mxsml_get_die_memory_info(device_id, die_id)
                if ret != MxSmlReturn.MXSML_Success:
                    print("mxSmlGetMemoryInfo failed: %s" % (mxsml_get_error_string(ret)))
                    self.need_init = True
                    break
                self.memory_info_map[die_id] = info


    def get_pcie_info(self, id):
        if any(map(lambda metric: metric in self.metrics_required, ['pcie_speed', 'pcie_width'])):
            ret = mxSmlGetPcieInfo(id, byref(self.pcie_info))
            if ret != MxSmlReturn.MXSML_Success:
                print("mxSmlGetPcieInfo failed: %s" % (mxsml_get_error_string(ret)))
                self.need_init = True


    def get_pcie_bridge_info(self, id):
        if any(map(lambda metric: metric in self.metrics_required, ['pcie_bridge_speed', 'pcie_bridge_width'])):
            ret = mxSmlGetPcieMaxLinkInfo(id, byref(self.pcie_bridge_info))
            if ret != MxSmlReturn.MXSML_Success:
                print("mxSmlGetPcieMaxLinkInfo failed: %s" % (mxsml_get_error_string(ret)))
                self.need_init = True


    def get_mxlk_info(self, device_id):
        if any(map(lambda metric: metric in self.metrics_required, ['mxlk_speed', 'mxlk_width', 'server_conn_status'])):
            ret, mxlk_info = mxsml_get_device_metaxlink_info(device_id)
            if ret != MxSmlReturn.MXSML_Success:
                print("mxSmlGetMetaXLinkInfo failed: %s" % (mxsml_get_error_string(ret)))
                self.need_init = True
                self.mxlk_status = 0
            else:
                self.mxlk_info = mxlk_info
                self.check_mxlk_status(mxlk_info)


    def check_mxlk_status(self, mxlk_info):
        for idx in range(METAX_LINK_NUM):
            if mxlk_info.speed[idx] == 0 and mxlk_info.width[idx] == 0:
                continue

            if mxlk_info.width[idx] != 16 or mxlk_info.speed[idx] not in [32, 2.5]:
                self.mxlk_status = 0
                return


    def get_temperature(self, sensor, device_id, metric_id):
        if(sensor == MxSmlTemperatureSensors.MXSML_Temperature_Soc):
            ret, temp = mxsml_get_device_temperature_info(device_id, sensor)
            if ret != MxSmlReturn.MXSML_Success:
                print("mxSmlGetTemperatureInfo for sensor %d failed: %s" % (sensor, mxsml_get_error_string(ret)))
            else:
                self.update_gpu_data(device_id, metric_id, temp/100)
            return

        for die_id in self.get_device_die_range(device_id):
            ret, temp = mxsml_get_die_temperature_info(device_id, die_id, sensor)
            if ret != MxSmlReturn.MXSML_Success:
                if ret == MxSmlReturn.MXSML_OperationNotSupport:
                    self.remove_notsupported_metrics(metric_id)
                else:
                    print("mxSmlGetTemperatureInfo for sensor %d failed: %s" % (sensor, mxsml_get_error_string(ret)))
            else:
                self.update_die_data(device_id, die_id, metric_id, temp/100)


    def get_om_temperature(self, device_id, metric_id):
        entryList = []
        omInfo = (MxSmlOpticalModuleStatus*3)(*entryList)
        omInfoSize = c_uint(3)
        ret = mxSmlGetOpticalModuleStatus(device_id, omInfo, byref(omInfoSize))
        if ret == MxSmlReturn.MXSML_Success:
            data = {}
            for i in range(omInfoSize.value):
                data[i] = omInfo[i].temperature/100
            self.update_gpu_data(device_id, metric_id, data)
        elif ret == MxSmlReturn.MXSML_OperationNotSupport:
            self.remove_notsupported_metrics(metric_id)
        else:
            print("mxSmlGetOpticalModuleStatus failed: %s" % (mxsml_get_error_string(ret)))
            self.need_init = True


    # All native, pf and vf devices can access GPU usage
    def get_gpu_usage(self, ip, device_id, metric_id):
        if ip in [MxSmlUsageIp.MXSML_Usage_Dla, MxSmlUsageIp.MXSML_Usage_G2d]:
            ret, usage = mxsml_get_device_ip_usage(device_id, ip)
            if ret != MxSmlReturn.MXSML_Success:
                print("mxSmlGetDeviceIpUsage for %d failed: %s" % (ip, mxsml_get_error_string(ret)))
                self.need_init = True
            else:
                self.update_gpu_data(device_id, metric_id, usage)
            return

        for die_id in self.get_device_die_range(device_id):
            ret, usage = mxsml_get_die_ip_usage(device_id, die_id, ip)
            if ret == MxSmlReturn.MXSML_Success:
                self.update_die_data(device_id, die_id, metric_id, usage)
            elif ret == MxSmlReturn.MXSML_OperationNotSupport:
                self.remove_notsupported_metrics(metric_id)
            else:
                print("mxSmlGetDeviceIpUsage for %d failed: %s" % (ip, mxsml_get_error_string(ret)))
                self.need_init = True


    def get_memory_usage(self, device_id, metric_id):
        for die_id, memory_info in self.memory_info_map.items():
            data = {"vram":0, "xtt":0}
            if memory_info.vramTotal != 0:
                data["vram"] = memory_info.vramUse*100/memory_info.vramTotal

            if memory_info.xttTotal != 0:
                data["xtt"] = memory_info.xttUse*100/memory_info.xttTotal

            self.update_die_data(device_id, die_id, metric_id, data)


    def get_memory_total(self, device_id, metric_id):
        for die_id, memory_info in self.memory_info_map.items():
            self.update_die_data(device_id, die_id, metric_id, {"vram":memory_info.vramTotal, "xtt":memory_info.xttTotal})


    def get_memory_used(self, device_id, metric_id):
        for die_id, memory_info in self.memory_info_map.items():
            self.update_die_data(device_id, die_id, metric_id, {"vram":memory_info.vramUse, "xtt":memory_info.xttUse})


    def get_pmbus_power(self, device_id, metric_id):
        for die_id in self.get_device_die_range(device_id):
            data = {}
            for unit, name in [
                (MxSmlPmbusUnit.MXSML_Pmbus_Soc, "soc"),
                (MxSmlPmbusUnit.MXSML_Pmbus_Core, "core"),
                (MxSmlPmbusUnit.MXSML_Pmbus_Hbm, "hbm"),
                (MxSmlPmbusUnit.MXSML_Pmbus_Pcie, "pcie"),
                (MxSmlPmbusUnit.MXSML_Pmbus_Hbm2, "hbm2"),
                (MxSmlPmbusUnit.MXSML_Pmbus_Pcie2, "pcie2")
            ]:
                ret, pmbusPowerInfo = mxsml_get_die_pmbus_info(device_id, die_id, unit)
                if ret == MxSmlReturn.MXSML_Success:
                    data[name] = pmbusPowerInfo.power
                elif ret == MxSmlReturn.MXSML_OperationNotSupport:
                    continue
                else:
                    print("mxSmlGetPmbusInfo for unit %d failed: %s" % (unit, mxsml_get_error_string(ret)))
                self.update_die_data(device_id, die_id, metric_id, data)


    def get_board_power(self, device_id, metric_id):
        entryBoardInfo = []
        boardPowerInfo = (MxSmlBoardWayElectricInfo* 3)(*entryBoardInfo)
        BoardWaySize = c_uint(3)
        ret = mxSmlGetBoardPowerInfo(device_id, byref(BoardWaySize), boardPowerInfo)
        if ret != MxSmlReturn.MXSML_Success:
            print("mxSmlGetBoardElectricInfo failed: %s" % (mxsml_get_error_string(ret)))
        else:
            i = 0
            power_total = 0
            while i < BoardWaySize.value:
                power_total += boardPowerInfo[i].power
                i += 1
            self.update_gpu_data(device_id, metric_id, power_total)


    def get_clocks(self, ip, device_id, metric_id):
        if ip in [MxSmlClockIp.MXSML_Clock_Dla, MxSmlClockIp.MXSML_Clock_G2D]:
            ret, clocksMhz = mxsml_get_device_clocks(device_id, ip)
            if ret != MxSmlReturn.MXSML_Success:
                print("mxSmlGetClocks for ip %d failed: %s" % (ip, mxsml_get_error_string(ret)))
            else:
                self.update_gpu_data(device_id, metric_id, clocksMhz[0])
            return

        for die_id in self.get_device_die_range(device_id):
            ret, clocksMhz = mxsml_get_die_clocks(device_id, die_id, ip)
            if ret == MxSmlReturn.MXSML_Success:
                self.update_die_data(device_id, die_id, metric_id, clocksMhz[0])
            elif ret == MxSmlReturn.MXSML_OperationNotSupport:
                self.remove_notsupported_metrics(metric_id)
            else:
                print("mxSmlGetClocks for ip %d failed: %s" % (ip, mxsml_get_error_string(ret)))


    def get_mem_clock(self, device_id, metric_id):
        ip = MxSmlClockIp.MXSML_Clock_Mc0
        if self.product == "MXN":
            ip = MxSmlClockIp.MXSML_Clock_Mc

        self.get_clocks(ip, device_id, metric_id)


    def get_pcie_throughput(self, device_id, metric_id):
        pcieThroughput = MxSmlPcieThroughput()
        ret = mxSmlGetPcieThroughput(device_id, byref(pcieThroughput))
        if ret != MxSmlReturn.MXSML_Success:
            print("mxSmlGetPcieThroughput failed: %s" % mxsml_get_error_string(ret))
        else:
            self.update_gpu_data(device_id, metric_id, {"tx":pcieThroughput.tx, "rx":pcieThroughput.rx})


    def get_mxlk_bandwidth(self, device_id, metric_id):
        data = {"rx":{}, "tx":{}}
        for typeCode, typeName in [(MxSmlMetaXLinkType.MXSML_MetaXLink_Input, "rx"), (MxSmlMetaXLinkType.MXSML_MetaXLink_Target, "tx")]:
            ret, linkSize, mxlkBw = mxsml_get_device_metaxlink_bandwidth(device_id, typeCode)
            if ret == MxSmlReturn.MXSML_Success:
                targetData = data[typeName]
                for i in range(linkSize):
                    targetData[i + 1] = mxlkBw[i].requestBandwidth

            elif ret == MxSmlReturn.MXSML_OperationNotSupport:
                self.remove_notsupported_metrics(metric_id)
                return

            else:
                print("mxSmlGetMetaXLinkBandwidth failed: %s" % mxsml_get_error_string(ret))
                self.need_init = True
                return

        self.update_gpu_data(device_id, metric_id, data)


    def get_mxlk_traffic_total_bytes(self, device_id, metric_id):
        data = {"rx":{}, "tx":{}}
        for typeCode, typeName in [(MxSmlMetaXLinkType.MXSML_MetaXLink_Input, "rx"), (MxSmlMetaXLinkType.MXSML_MetaXLink_Target, "tx")]:
            ret, linkSize, mxlkTrafficStats = mxsml_get_device_metaxlink_traffic_stat(device_id, typeCode)
            if ret == MxSmlReturn.MXSML_Success:
                targetData = data[typeName]
                for i in range(linkSize):
                    targetData[i + 1] = mxlkTrafficStats[i].requestTrafficStat

            elif ret == MxSmlReturn.MXSML_OperationNotSupport:
                self.remove_notsupported_metrics(metric_id)
                return

            else:
                print("mxSmlGetMetaXLinkTrafficStat failed: %s" % mxsml_get_error_string(ret))
                self.need_init = True
                return

        self.update_gpu_data(device_id, metric_id, data)


    def get_mxlk_aer_count(self, device_id, metric_id):
        data = {"ce":{}, "ue":{}}
        ret, linkSize, mxlkAer = mxsml_get_device_metaxlink_aer(device_id)
        if ret == MxSmlReturn.MXSML_Success:
            for i in range(linkSize):
                data["ce"][i + 1] = mxlkAer[i].ceAer
                data["ue"][i + 1] = mxlkAer[i].ueAer

        elif ret == MxSmlReturn.MXSML_OperationNotSupport:
            self.remove_notsupported_metrics(metric_id)
            return

        else:
            print("mxSmlGetMetaXLinkAer failed: %s" % mxsml_get_error_string(ret))
            self.need_init = True
            return

        self.update_gpu_data(device_id, metric_id, data)


    def get_hbm_throughput(self, device_id, metric_id):
        for die_id in self.get_device_die_range(device_id):
            hbmThroughput = MxSmlHbmBandwidth()
            ret = mxSmlGetDieHbmBandWidth(device_id, die_id, byref(hbmThroughput))
            if ret != MxSmlReturn.MXSML_Success:
                print("mxSmlGetHbmBandWidth failed: %s" % mxsml_get_error_string(ret))
            else:
                self.update_die_data(device_id, die_id, metric_id, hbmThroughput.hbmBandwidthRespTotal)


    def get_dpm_level(self, ip, device_id, metric_id):
        if ip == MxSmlDpmIp.MXSML_Dpm_Dla:
            ret, dpmLevel = mxsml_get_device_current_dpm_ip_perf_level(device_id, ip)
            if ret != MxSmlReturn.MXSML_Success:
                if ret != MxSmlReturn.MXSML_OperationNotSupport:
                    print("mxSmlGetCurrentDpmIpPerfLevel failed: " + mxsml_get_error_string(ret))
            else:
                self.update_gpu_data(device_id, metric_id, dpmLevel)
            return

        for die_id in self.get_device_die_range(device_id):
            ret, dpmLevel = mxsml_get_die_current_dpm_ip_perf_level(device_id, die_id, ip)
            if ret != MxSmlReturn.MXSML_Success:
                if ret != MxSmlReturn.MXSML_OperationNotSupport:
                    print("mxSmlGetCurrentDpmIpPerfLevel failed: " + mxsml_get_error_string(ret))
            else:
                self.update_die_data(device_id, die_id, metric_id, dpmLevel)


    def get_pcie_speed(self, device_id, metric_id):
        self.update_gpu_data(device_id, metric_id, self.pcie_info.speed)

    def get_pcie_width(self, device_id, metric_id):
        self.update_gpu_data(device_id, metric_id, self.pcie_info.width)

    def get_pcie_bridge_speed(self, device_id, metric_id):
        self.update_gpu_data(device_id, metric_id, self.pcie_bridge_info.speed)

    def get_pcie_bridge_width(self, device_id, metric_id):
        self.update_gpu_data(device_id, metric_id, self.pcie_bridge_info.width)

    def get_mxlk_speed(self, device_id, metric_id):
        data = {}
        for idx in range(METAX_LINK_NUM):
            data[idx+1] = self.mxlk_info.speed[idx]
        self.update_gpu_data(device_id, metric_id, data)

    def get_mxlk_width(self, device_id, metric_id):
        data = {}
        for idx in range(METAX_LINK_NUM):
            data[idx+1] = self.mxlk_info.width[idx]
        self.update_gpu_data(device_id, metric_id, data)


    def get_process_info(self, device_id, metric_id):
        entrylist = []
        processNumber = c_uint(32)
        processInfo = (MxSmlProcessInfo_v2*32)(*entrylist)
        ret = mxSmlGetSingleGpuProcess_v2(device_id, processNumber, processInfo)
        if ret != MxSmlReturn.MXSML_Success:
            print("mxSmlGetSingleGpuProcess failed: " + mxsml_get_error_string(ret))
        else:
            for die_id in self.get_device_die_range(device_id):
                number = 0
                for idx, process in enumerate(processInfo):
                    if idx == processNumber.value:
                        break
                    for gpu_idx, gpu_info in enumerate(process.processGpuInfo):
                        if gpu_idx == process.gpuNumber:
                            break
                        if gpu_info.gpuId == device_id and gpu_info.dieId == die_id:
                            number += 1
                            break
                self.update_die_data(device_id, die_id, metric_id, number)

    def get_gpu_state(self, device_id, metric_id):
        for die_id in self.get_device_die_range(device_id):
            unavailable_reason = ""
            deviceState = c_int(0)
            ret = mxSmlGetDeviceState(device_id, byref(deviceState))
            if ret != MxSmlReturn.MXSML_Success:
                print("mxSmlGetDeviceState failed: " + mxsml_get_error_string(ret))
            else:
                if deviceState.value == 0:
                    ret, unavailable_reason = mxsml_get_die_unavailable_reason(device_id, die_id)
                self.update_die_data(device_id, die_id, metric_id, {unavailable_reason: deviceState.value})


    def get_clock_throttle_reason(self, device_id, metric_id):
        for die_id in self.get_device_die_range(device_id):
            ret, clocksThrottleReason = mxsml_get_current_clocks_throttle_reason(device_id, die_id)
            if ret == MxSmlReturn.MXSML_Success:
                self.update_die_data(device_id, die_id, metric_id, clocksThrottleReason)
            elif ret == MxSmlReturn.MXSML_OperationNotSupport:
                self.remove_notsupported_metrics(metric_id)
                return
            else:
                print("mxSmlGetCurrentClocksThrottleReason failed: " + mxsml_get_error_string(ret))
                self.need_init = True
                return


    def get_ecc_count(self, device_id, metric_id):
        for die_id in self.get_device_die_range(device_id):
            ret, eccCounts = mxsml_get_die_total_ecc_errors(device_id, die_id)
            if ret == MxSmlReturn.MXSML_Success:
                self.update_die_data(
                    device_id,
                    die_id,
                    metric_id,
                    {
                        "sram_ce": eccCounts.sramCE,
                        "sram_ue": eccCounts.sramUE,
                        "dram_ce": eccCounts.dramCE,
                        "dram_ue": eccCounts.dramUE,
                        "retired_page": eccCounts.retiredPage,
                    }
                )
            elif ret == MxSmlReturn.MXSML_OperationNotSupport:
                self.remove_notsupported_metrics(metric_id)
                return
            else:
                print("mxSmlGetDieTotalEccErrors failed: %s" % mxsml_get_error_string(ret))
                self.need_init = True
                return


    def get_sgpu_info(self, device_id, sgpu_count):
        count = 0
        for sgpu_id in range(0, 16): # max sgpu count = 16
            if count >= sgpu_count:
                break

            ret, sgpu_info = mxsml_get_sgpu_info(device_id, sgpu_id)
            if ret == MxSmlReturn.MXSML_Success:
                count = count + 1
                self.all_sgpu_info[(device_id, sgpu_id)] = sgpu_info
                pod_register_uuid = mxsml_get_sgpu_annotations_id(device_id, sgpu_id)
                self.sgpu_pod_uuid_map[(device_id, sgpu_id)] = pod_register_uuid
            elif ret != MxSmlReturn.MXSML_OperationNotSupport:
                print("mxSmlGetSgpuInfo failed: %s" % (mxsml_get_error_string(ret)))
                self.need_init = True
                break


    def get_sgpu_usage(self, device_id, metric_id):
        for (device_id, sgpu_id) in self.all_sgpu_info:
            usage = c_int(0)
            ret = mxSmlGetSgpuUsage(device_id, sgpu_id, byref(usage))
            if ret != MxSmlReturn.MXSML_Success and ret != MxSmlReturn.MXSML_OperationNotSupport:
                print(f"Device {device_id} Sgpu {sgpu_id} mxSmlGetSgpuUsage failed: "
                        + mxSmlGetErrorString(ret).decode('ASCII'))
            else:
                self.update_sgpu_data(device_id, sgpu_id, metric_id, usage.value/100)


    def get_sgpu_memory_info(self, device_id):
        for (device_id, sgpu_id) in self.all_sgpu_info:
            memory = MxSmlSgpuMemoryInfo()
            ret = mxSmlGetSgpuMemory(device_id, sgpu_id, byref(memory))
            if ret != MxSmlReturn.MXSML_Success and ret != MxSmlReturn.MXSML_OperationNotSupport:
                print(f"Device {device_id} Sgpu {sgpu_id} mxSmlGetSgpuMemory failed: "
                        + mxSmlGetErrorString(ret).decode('ASCII'))
                self.need_init = True
                break
            self.sgpu_memory_info[(device_id, sgpu_id)] = memory


    def get_sgpu_memory_total(self, device_id, metric_id):
        for (device_id, sgpu_id) in self.sgpu_memory_info:
            memory = self.sgpu_memory_info[(device_id, sgpu_id)]
            self.update_sgpu_data(device_id, sgpu_id, metric_id, memory.total/1024)


    def get_sgpu_memory_used(self, device_id, metric_id):
        for (device_id, sgpu_id) in self.sgpu_memory_info:
            memory = self.sgpu_memory_info[(device_id, sgpu_id)]
            self.update_sgpu_data(device_id, sgpu_id, metric_id, memory.used/1024)


    def get_sgpu_memory_free(self, device_id, metric_id):
        for (device_id, sgpu_id) in self.sgpu_memory_info:
            memory = self.sgpu_memory_info[(device_id, sgpu_id)]
            self.update_sgpu_data(device_id, sgpu_id, metric_id, memory.free/1024)


    def get_sgpu_compute_quota(self, device_id, metric_id):
        for (device_id, sgpu_id) in self.all_sgpu_info:
            sgpuInfo = self.all_sgpu_info[(device_id, sgpu_id)]
            self.update_sgpu_data(device_id, sgpu_id, metric_id, sgpuInfo.computeQuota)

    def get_server_info(self):
        ret, local_uuid, remote_uuid1, remote_uuid2 = mxsml_get_local_and_multiple_remote_uuid()
        self.server_info = ServerInfo(local_uuid, [remote_uuid1, remote_uuid2], self.mxlk_status)

        if ret != MxSmlReturn.MXSML_Success and ret != MxSmlReturn.MXSML_OperationNotSupport:
             print("mxSmlGetLocalAndMultipleRemoteUuid failed: " + mxsml_get_error_string(ret))
             self.need_init = True

        return ret


    def get_server_uuid(self, metric_id):
        data = {}
        data['local'] = {}
        data['remote'] = {}

        data['local'][self.server_info.local_uuid] = 1
        for idx, remote_uuid in enumerate(self.server_info.remote_uuids):
            if remote_uuid:
                data["remote"][remote_uuid] = idx + 1

        self.update_server_data(metric_id, data)


    def get_server_conn_status(self, metric_id):
        data = {}
        data[self.server_info.local_uuid] = self.server_info.conn_status
        self.update_server_data(metric_id, data)
        return


    def get_pci_event(self, device_id, metric_id):
        pcie_event_name_array = ["aer_ue", "aer_ce", "synfld", "dbe", "mmio"]
        data = {"aer_ue":{}, "aer_ce":{}, "synfld":{}, "dbe":{}, "mmio":{}}
        for event_idx, event_name in enumerate(pcie_event_name_array):
            event_type = event_idx
            ret, event, size = mxsml_get_device_pci_event(device_id, event_type)
            if ret == MxSmlReturn.MXSML_Success:
                for i in range(size):
                    data[event_name][event[i].name.decode('ASCII')] = event[i].count

            elif ret == MxSmlReturn.MXSML_OperationNotSupport:
                self.remove_notsupported_metrics(metric_id)
                break

            else:
                print("mxSmlGetPciEventInfo device %d type %d failed: %s" % (device_id, event_type, mxsml_get_error_string(ret)))
                continue

        self.update_gpu_data(device_id, metric_id, data)

    def get_ras_count(self, device_id, metric_id):
        for die_id in self.get_device_die_range(device_id):
            ret, ras_error_data = mxsml_get_die_ras_count(device_id, die_id)
            data = {}
            if ret == MxSmlReturn.MXSML_Success:
                for item in ras_error_data:
                    data[item[0]] = item[1]

            elif ret == MxSmlReturn.MXSML_OperationNotSupport:
                self.remove_notsupported_metrics(metric_id)
                break

            else:
                print("mxSmlGetRasErrorData device %d failed: %s" % (device_id, mxsml_get_error_string(ret)))

            self.update_die_data(device_id, die_id, metric_id, data)

    def get_ras_status(self, device_id, metric_id):
        for die_id in self.get_device_die_range(device_id):
            ret, ras_status = mxsml_get_die_ras_status(device_id, die_id)

            data = {}
            if ret == MxSmlReturn.MXSML_Success:
                for item in ras_status:
                    data[item[0]] = item[1]

            elif ret == MxSmlReturn.MXSML_OperationNotSupport:
                self.remove_notsupported_metrics(metric_id)

            else:
                print("mxSmlGetRasStatusData device %d failed: %s" % (device_id, mxsml_get_error_string(ret)))

            self.update_die_data(device_id, die_id, metric_id, data)

    def get_eth_throughput(self, device_id, metric_id):
        ethThroughput = MxSmlEthThroughput()
        ret = mxSmlGetEthThroughput(device_id, byref(ethThroughput))
        if ret != MxSmlReturn.MXSML_Success:
            if ret == MxSmlReturn.MXSML_OperationNotSupport:
                self.remove_notsupported_metrics(metric_id)
            else:
                print("mxSmlGetEthThroughput failed: %s" % mxsml_get_error_string(ret))
        else:
            self.update_gpu_data(device_id, metric_id, {"tx":ethThroughput.tx, "rx":ethThroughput.rx})

if __name__ == "__main__":
    metrics_required_mxc = [
        "chip_hotspot_temp", "board_soc_temp", "board_core_temp", "optical_module_temp",
        "gpu_usage", "vpue_usage", "vpud_usage", "memory_usage", "memory_total", "memory_used",
        "pmbus_soc", "pmbus_core", "pmbus_hbm", "pmbus_pcie", "board_power",
        "gpu_clock", "vpue_clock", "vpud_clock", "mem_clock", "pcie_bw", "mxlk_bw", "hbm_bw",
        "xcore_dpm_level", "pcie_speed", "pcie_width", "pcie_bridge_speed", "pcie_bridge_width",
        "mxlk_speed", "mxlk_width", "process", "gpu_state", "dla_clock", "g2d_clock", "clk_thr",
        "sgpu_alias", "sgpu_compute_quota", "sgpu_usage", "sgpu_memory_total",
        "sgpu_memory_used", "sgpu_memory_free", "server_info"
    ]

    monitor = GpuMonitor(10)
    monitor.start(metrics_required_mxc)

    while True:
        print(monitor.get_gpu_data())
        time.sleep(5)

