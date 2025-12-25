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

import os
import time
from datetime import datetime
from prometheus_client import Gauge


old_print = print
def timestamp_print(*args, **kwargs):
    old_print(datetime.now(), "IBMonitor", *args, **kwargs)
print = timestamp_print


class IBNic:
    def __init__(self, ib_path, nic_name):
        self.ib_path = ib_path
        self.nic_name = nic_name
        self.ports = set()
        self.counters_export = set()
        self.hw_counters_export = set()

    def get_nic_name(self):
        return self.nic_name

    def set_ports(self, ports):
        self.ports = ports

    def get_ports(self):
        return self.ports

    def get_counters_export(self):
        return self.counters_export

    def get_hw_counters_export(self):
        return self.hw_counters_export

    def check_counter_file(self, counter_file):
        if not os.path.exists(counter_file):
            print("check_counter_file %s not exist" % counter_file)
            return False

        try:
            with open(counter_file, 'r') as f:
                value = f.read().strip()
        except Exception as e:
            print("check_counter_file read %s error %s" % (counter_file, e))
            return False

        return True

    def filter_counters(self, counters, hw_counters):
        for port in self.ports:
            port_dir = os.path.join(self.ib_path, self.nic_name, "ports", port)

            counter_dir = os.path.join(port_dir, "counters")
            for counter in counters:
                if self.check_counter_file(os.path.join(counter_dir, counter)):
                    self.counters_export.add(counter)

            hw_counter_dir = os.path.join(port_dir, "hw_counters")
            for hw_counter in hw_counters:
                if self.check_counter_file(os.path.join(hw_counter_dir, hw_counter)):
                    self.hw_counters_export.add(hw_counter)

        return


class IBMonitor:

    def __init__(self):
        self.counters = [
                "port_rcv_constraint_errors", "port_rcv_switch_relay_errors",
                "port_rcv_data", "port_rcv_errors", "port_rcv_packets", "port_rcv_remote_physical_errors",
                "port_xmit_data", "port_xmit_discards", "port_xmit_wait", "port_xmit_packets", "port_xmit_constraint_errors",
                "excessive_buffer_overrun_errors", "symbol_error", "local_link_integrity_errors",
                "link_downed", "link_error_recovery"
                ]
        self.hw_counters = [
                "np_cnp_sent", "np_ecn_marked_roce_packets", "rp_cnp_handled", "rp_cnp_ignored",
                "out_of_buffer", "out_of_sequence",
                "duplicate_request", "implied_nak_seq_err", "local_ack_timeout_err", "packet_seq_err", "req_cqe_error",
                "req_cqe_flush_error", "req_remote_access_errors", "req_remote_invalid_request", "resp_cqe_error", "resp_cqe_flush_error",
                "resp_local_length_error", "resp_remote_access_errors", "rnr_nak_retry_err", "roce_adp_retrans", "roce_adp_retrans_to",
                "rx_read_requests", "rx_write_requests"
                ]
        self.port_counter = Gauge("port_counter", "Port Counters under the counters folder", ["nic_name", "port", "counter_name", "Hostname"])
        self.port_hw_counter = Gauge("port_hw_counter", "HW counters under the hw_counters folder", ["nic_name", "port", "counter_name", "Hostname"])
        self.ib_path = '/sys/class/infiniband/'
        self.ib_nics = []
        self.initialize()

    def initialize(self):
        print("start initialize")
        self.ib_nics.clear()
        self.find_ib_nics()
        self.filter_counters()

    def find_ib_nics(self):
        if not os.path.exists(self.ib_path):
            print("IB path not exist")
            return

        for nic in os.listdir(self.ib_path):
            if 'bnxt' in nic:
                continue

            ib_nic = IBNic(self.ib_path, nic)
            ports_dir = os.path.join(self.ib_path, nic, 'ports')
            ports = set()
            for port in os.listdir(ports_dir):
                counter_dir = os.path.join(ports_dir, port, "counters")
                hw_counter_dir = os.path.join(ports_dir, port, "hw_counters")
                if os.path.exists(counter_dir) and os.path.exists(hw_counter_dir):
                    ports.add(port)
                else:
                    print("find_ib_nics error %s port %s is not valid" % (nic, port))

            if len(ports) != 0:
                ib_nic.set_ports(ports)
                self.ib_nics.append(ib_nic)
            else:
                print("find_ib_nics error %s has no valid port" % nic)

        return

    def filter_counters(self):
        for ib_nic in self.ib_nics:
            ib_nic.filter_counters(self.counters, self.hw_counters)

        return

    def export(self, host_name):
        self.port_counter.clear()
        self.port_hw_counter.clear()

        if len(self.ib_nics) == 0:
            print("No valid nic found")
            self.initialize()
            return

        print("Export IB counters")
        need_init = False
        for ib_nic in self.ib_nics:
            nic = ib_nic.get_nic_name()
            if not os.path.exists(os.path.join(self.ib_path, nic)):
                print("Export Error %s not exist" % nic)
                need_init = True
                continue

            for port in ib_nic.get_ports():
                port_dir = os.path.join(self.ib_path, nic, "ports", port)

                counter_dir = os.path.join(port_dir, "counters")
                for counter in ib_nic.get_counters_export():
                    self.port_counter.labels(nic, port, counter, host_name).set(self.get_counter_value(counter_dir, counter))

                hw_counter_dir = os.path.join(port_dir, "hw_counters")
                for hw_counter in ib_nic.get_hw_counters_export():
                    self.port_hw_counter.labels(nic, port, hw_counter, host_name).set(self.get_counter_value(hw_counter_dir, hw_counter))

        if need_init:
            self.initialize()

        return

    def get_counter_value(self, counter_dir, counter_name):
        counter_file = os.path.join(counter_dir, counter_name)
        value = 0
        try:
            with open(counter_file, 'r') as f:
                value = f.read().strip()
        except Exception as e:
            print("Read %s error %s" % (counter_file, e))

        return value

    def get_all_counters(self):
        counters = []
        for ib_nic in self.ib_nics:
            nic = ib_nic.get_nic_name()
            for port in ib_nic.get_ports():
                port_dir = os.path.join(self.ib_path, nic, "ports", port)

                counter_dir = os.path.join(port_dir, "counters")
                for counter in ib_nic.get_counters_export():
                    counters.append((nic, port, counter, self.get_counter_value(counter_dir, counter)))

                hw_counter_dir = os.path.join(port_dir, "hw_counters")
                for hw_counter in ib_nic.get_hw_counters_export():
                    counters.append((nic, port, hw_counter, self.get_counter_value(hw_counter_dir, hw_counter)))
        return counters


class BnxtMonitor:

    def __init__(self):
        self.bnxt_counter = Gauge("bnxt_counter", "bnxt_re counters", ["nic_name", "counter_name", "Hostname"])
        self.bnxt_re_path = "/sys/kernel/debug/bnxt_re"

    def export(self, host_name):
        self.bnxt_counter.clear()

        if not os.path.exists(self.bnxt_re_path):
            return

        for bnxt_nic in os.listdir(self.bnxt_re_path):
            bnxt_nic_info = os.path.join(self.bnxt_re_path, bnxt_nic, "info")
            if not os.path.exists(bnxt_nic_info):
                continue

            print("BnxtMonitor export %s" % bnxt_nic)
            try:
                with open(bnxt_nic_info, 'r') as file:
                    for line in file:
                        line = line.strip()
                        if not (line and ':' in line):
                            continue

                        content = line.split(':', 1)
                        counter_name = content[0].strip()
                        value = content[1].strip()
                        if not counter_name or not value:
                            continue

                        ret,value_int = self.str_to_int(value)
                        if ret:
                            self.bnxt_counter.labels(bnxt_nic, counter_name, host_name).set(value_int)

            except Exception as e:
                print("Read %s error %s" % (bnxt_nic_info, e))

        return

    def str_to_int(self, src_str):
        try:
            dst_int = int(src_str, 0)
        except Exception as e:
            return False,-1

        return True,dst_int


if __name__ == "__main__":
    monitor = IBMonitor()

    while True:
        for counter in monitor.get_all_counters():
            print(counter)
        time.sleep(5)
