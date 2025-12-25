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

import grpc
from mx_exporter import podresourcev1alpha1_pb2
from mx_exporter import podresourcev1alpha1_pb2_grpc


class PodInfo:

    def __init__(self, pod_name='', pod_namespace='', container_name='', device_uuid=''):
        self.pod_name = pod_name
        self.pod_namespace = pod_namespace
        self.container_name = container_name
        self.device_uuid = device_uuid

    def __str__(self):
        return "PodInfo:{ pod_name:%s, pod_namespace:%s, container_name:%s, device_uuid:%s }" \
                % (self.pod_name, self.pod_namespace, self.container_name, self.device_uuid)

    def __repr__(self):
        return self.__str__()


def get_pod_resource():
    device_pod_map = {}

    with grpc.insecure_channel('unix:///var/lib/kubelet/pod-resources/kubelet.sock') as channel:
        stub = podresourcev1alpha1_pb2_grpc.PodResourcesListerStub(channel)
        try:
            response = stub.List(podresourcev1alpha1_pb2.ListPodResourcesRequest())
        except grpc.RpcError as rpc_error:
#            print("grpc error: %s" % rpc_error.details())
            return device_pod_map

    for pod in response.pod_resources:
        for container in pod.containers:
            for device in container.devices:
                if not "metax-tech" in device.resource_name:
                    continue

                for device_id in device.device_ids:
                    device_pod_map[device_id] = PodInfo(pod.name, pod.namespace, container.name, device_id)

    return device_pod_map


if __name__ == "__main__":
    device_pod = get_pod_resource()
    print(device_pod)
