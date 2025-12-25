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

import re
import os.path
import time
import threading
from copy import deepcopy
from datetime import datetime


old_print = print
def timestamp_print(*args, **kwargs):
    old_print(datetime.now(), "LogMonitor", *args, **kwargs)
print = timestamp_print


class KernelErrorInfo:

    def __init__(self, module, bdf_id, die_id, submodule, log_level, content):
        self.module = module
        self.bdf_id = self.convertBdf(bdf_id)
        if die_id:
            self.die_id = int(die_id)
        else:
            self.die_id = 0
        self.submodule = submodule
        self.log_level = log_level
        self.content = content

    def __str__(self):
        return "KernelLog:{ %s, %s, %d, %s, %s, %s }" \
                % (self.module, self.bdf_id, self.die_id, self.submodule, self.log_level, self.content)

    def __repr__(self):
        return self.__str__()

    def __hash__(self):
        return hash((self.bdf_id, self.die_id, self.submodule, self.log_level))

    def __eq__(self, other):
        return (self.bdf_id, self.die_id, self.submodule, self.log_level) == (other.bdf_id, other.die_id, other.submodule, other.log_level)

    def convertBdf(self, src):
        bdfInt = int(src, 16)
        return "%04x:%02x:%02x.%x" \
                % (bdfInt>>16, (bdfInt&0xffff)>>8, (bdfInt&0xff)>>3, bdfInt&0x7)


class DriverEidErrorInfo:

    def __init__(self, die_id, bdf_id, eid, eid_info):
        if die_id:
            self.die_id = int(die_id)
        else:
            self.die_id = 0
        self.bdf_id = bdf_id
        self.eid = int(eid, 16)
        self.eid_info = eid_info

    def __str__(self):
        return "DriverEidErrorInfo:{ %d, %s, %d, %s }" \
                % (self.die_id, self.bdf_id, self.eid, self.eid_info)

    def __repr__(self):
        return self.__str__()

    def __hash__(self):
        return hash((self.die_id, self.bdf_id, self.eid))

    def __eq__(self, other):
        return (self.die_id, self.bdf_id, self.eid) == (other.die_id, other.bdf_id, other.eid)


class LogHandler:
    def __init__(self, regex, data_type):
        self.regex = regex
        self.regex_obj = re.compile(regex)
        self.data_type = data_type
        self.dataset = []
        self.lock = threading.Lock()

    def handle(self, log):
        content = self.regex_obj.findall(log)
        for row in content:
            self.append_dataset(self.data_type(*row))

    def get(self):
        self.lock.acquire()
        data = deepcopy(self.dataset)
        self.lock.release()
        return data

    def clear(self):
        self.lock.acquire()
        self.dataset.clear()
        self.lock.release()

    def get_then_clear(self):
        self.lock.acquire()
        data = deepcopy(self.dataset)
        self.dataset.clear()
        self.lock.release()
        return data

    def append_dataset(self, data):
        self.lock.acquire()
        self.dataset.append(data)
        self.lock.release()


class LogMonitor:

    def __init__(self, handlers, interval=5):
        self.handlers = handlers
        self.interval = interval

    def start(self, log_file):
        if not os.path.exists(log_file):
            print("%s Invalid log file: %s" % (self.__class__.__name__, log_file))
            return False

        self.log_file = log_file
        t = threading.Thread(target=self.monitor, args=(), daemon=True)
        t.start()

        time.sleep(0.1)
        if t.is_alive():
            print("%s log monitor thread start successfully" % (self.__class__.__name__))
            return True

        print("%s log monitor thread start failed" % (self.__class__.__name__))
        return False

    def monitor(self):
        log_file_size = os.path.getsize(self.log_file)

        try:
            with open(self.log_file, 'r', encoding="utf-8") as f:
                f.seek(log_file_size)

                while True:
                    new_log = f.read()
                    if new_log:
                        log_file_size += len(new_log)
                        for handler in self.handlers:
                            handler.handle(new_log)

                    if os.path.getsize(self.log_file) < log_file_size:
                        print("%s log file rotate" % self.log_file)
                        f.close()
                        f = open(self.log_file, 'r', encoding="utf-8")
                        log_file_size = 0
                        f.seek(log_file_size)

                    time.sleep(self.interval)
        except Exception as e:
            print("Open %s exception error: %s" % (self.log_file, e))

        return

    def check_log_file(self, file):
        return os.path.exists(file) and os.path.getsize(file) > 0


class KernelLogMonitor(LogMonitor):
    def __init__(self, interval=5):
        """
            METAX.B4F00.SMI.ERROR xxxxxxxxxx
            METAX.B4F00.V0.SMI.ERROR xxxxxxxxxx
            METAX.B4F00.D0.SMI.ERROR xxxxxxxxxx
            METAX.B4F00.D0.V0.SMI.ERROR xxxxxxxxxx
        """
        self.kernel_error_regex = r'(METAX|MXGVM|MXCD)\.B([0-9A-F]{3,8})\.(?:D([0-9])\.)?(?:V[0-9]+\.)?([A-Z]{1,20})\.(ERROR|ALERT) (.+)'
        self.kernel_error_handler = LogHandler(self.kernel_error_regex, KernelErrorInfo)
        """
            MXCD.B4F00.D0.IOCTL.ERROR EID (0000:01:01.0): 0x2202, device arrary empty, xxxx, xxxx
            xxxx is optional
        """
        self.eid_error_regex = r'(?:\w+\.B\w+)(?:\.D([0-9]))?\.(?:.+) EID \((.+)\): ([^\W]+), (.+)'
        self.eid_error_handler = LogHandler(self.eid_error_regex, DriverEidErrorInfo)

        super().__init__([self.kernel_error_handler, self.eid_error_handler], interval)

    def start(self, mount_point='', log_file=''):
        if len(log_file) == 0:
            self.log_file = self.get_kernel_log_file(mount_point)
        else:
            self.log_file = os.path.join('/', mount_point, log_file)

        return super().start(self.log_file)

    def get_kernel_log_file(self, mount_point):
        if not mount_point:
            if super().check_log_file('/var/log/messages'):
                return '/var/log/messages'
            elif super().check_log_file('/var/log/kern.log'):
                return '/var/log/kern.log'
            else:
                return ''
        else:
            if super().check_log_file(os.path.join('/', mount_point, 'var/log/messages')):
                return os.path.join('/', mount_point, 'var/log/messages')
            elif super().check_log_file(os.path.join('/', mount_point, 'var/log/kern.log')):
                return os.path.join('/', mount_point, 'var/log/kern.log')
            else:
                return ''

    def get_supported_metrics(self):
        return ['driver_eid_errors', 'driver_log_errors']

    def get_kernel_error_info(self):
        return self.kernel_error_handler.get_then_clear()

    def get_eid_error_info(self):
        return self.eid_error_handler.get_then_clear()


class SdkEidErrorInfo:

    def __init__(self, sdk_version, module, bdf_id, eid, eid_info):
        self.sdk_version = int(sdk_version)
        self.module = module
        self.bdf_id = bdf_id
        self.eid = int(eid, 16)
        self.eid_info = eid_info

    def __str__(self):
        return "SdkEidErrorInfo:{ %d, %s, %s, %d, %s }" \
                % (self.sdk_version, self.module, self.bdf_id, self.eid, self.eid_info)

    def __repr__(self):
        return self.__str__()

    def __hash__(self):
        return hash((self.sdk_version, self.bdf_id, self.eid))

    def __eq__(self, other):
        return (self.pocess_id, self.bdf_id, self.eid) == (other.sdk_version, other.bdf_id, other.eid)


class SysLogMonitor(LogMonitor):

    def __init__(self, interval=5):
        """
            SDK.20250619.UMD.FATAL EID (0000:01:01.0): 0x3104, Xnack Error, xxxx, xxxx
            xxxx is optional
        """
        self.eid_error_regex = r'SDK\.([0-9]+)\.([^\.\n]+)\.(?:.+) EID \((.+)\): ([^\W]+), (.+)'
        self.eid_error_handler = LogHandler(self.eid_error_regex, SdkEidErrorInfo)

        super().__init__([self.eid_error_handler], interval)

    def start(self, mount_point='', log_file=''):
        if len(log_file) == 0:
            self.log_file = self.get_sys_log_file(mount_point)
        else:
            self.log_file = os.path.join('/', mount_point, log_file)

        return super().start(self.log_file)

    def get_sys_log_file(self, mount_point):
        if not mount_point:
            if super().check_log_file('/var/log/syslog'):
                return '/var/log/syslog'
            elif super().check_log_file('/var/log/messages'):
                return '/var/log/messages'
            else:
                return ''
        else:
            if super().check_log_file(os.path.join('/', mount_point, 'var/log/syslog')):
                return os.path.join('/', mount_point, 'var/log/syslog')
            elif super().check_log_file(os.path.join('/', mount_point, 'var/log/messages')):
                return os.path.join('/', mount_point, 'var/log/messages')
            else:
                return ''

    def get_supported_metrics(self):
        return ['sdk_eid_errors']

    def get_eid_error_info(self):
        return self.eid_error_handler.get_then_clear()


if __name__ == "__main__":
    import sys
    monitor = KernelLogMonitor()
    sys_monitor = SysLogMonitor()
    if not monitor.start(sys.argv[1], sys.argv[2]) or not sys_monitor.start(sys.argv[1], sys.argv[2]):
        print("Start failed")
        exit(-1)

    while True:
        logs = monitor.get_kernel_error_info()
        logs += monitor.get_eid_error_info()
        logs += sys_monitor.get_eid_error_info()
        for log in logs:
            print(log)
        time.sleep(5)
