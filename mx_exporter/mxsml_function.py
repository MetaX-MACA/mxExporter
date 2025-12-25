#!/usr/bin/env python3

"""
Copyright © 2025 MetaX Integrated Circuits (Shanghai) Co., Ltd. All Rights Reserved.

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

import os.path
import sys
import importlib


sys.path.append("/opt/maca/include/mxsml")
sys.path.append("/opt/mxn100/include/mxsml")
sys.path.append(os.path.dirname(__file__))
from mxsmlBindings import *


_module = importlib.import_module("mxsmlBindings")


def mxsml_get_error_string(ret):
    return mxSmlGetErrorString(ret).decode('ASCII')


def mxsml_get_device_die_count(device_id): # ret: (MxSmlReturn, int)
    if hasattr(_module, "mxSmlGetDeviceDieCount"):
        die_count = c_uint()
        ret = mxSmlGetDeviceDieCount(device_id, byref(die_count))
        return (ret, die_count.value)
    else:
        return (MxSmlReturn.MXSML_Success, 1)


def mxsml_get_die_version(device_id, die_id, unit): # ret: (MxSmlReturn, string)
    if hasattr(_module, "mxSmlGetDeviceDieVersion"):
        size = c_uint(64)
        entrylist = []
        version = (c_char * 64)(*entrylist)
        ret = mxSmlGetDeviceDieVersion(device_id, die_id, unit, version, size)
        return (ret, version.value.decode('ASCII'))
    else:
        size = c_uint(64)
        entrylist = []
        version = (c_char * 64)(*entrylist)
        ret = mxSmlGetDeviceVersion(device_id, unit, version, size)
        return (ret, version.value.decode('ASCII'))


def mxsml_get_die_memory_info(device_id, die_id): # ret: (MxSmlReturn, MxSmlMemoryInfo)
    if hasattr(_module, "mxSmlGetDieMemoryInfo"):
        info = MxSmlMemoryInfo()
        ret = mxSmlGetDieMemoryInfo(device_id, die_id, byref(info))
        return (ret, info)
    else:
        info = MxSmlMemoryInfo()
        ret = mxSmlGetMemoryInfo(device_id, byref(info))
        return (ret, info)


def mxsml_get_device_metaxlink_info(device_id): # ret: (MxSmlReturn, MxSmlMetaXLinkInfo)
    mxlk_info = MxSmlMetaXLinkInfo()
    ret = mxSmlGetMetaXLinkInfo(device_id, byref(mxlk_info))
    return(ret, mxlk_info)


def mxsml_get_device_temperature_info(device_id, sensor): # ret: (MxSmlReturn, int)
    temp = c_int(0)
    ret = mxSmlGetTemperatureInfo(device_id, sensor, temp)
    return (ret, temp.value)


def mxsml_get_die_temperature_info(device_id, die_id, sensor): # ret: (MxSmlReturn, int)
    if hasattr(_module, "mxSmlGetDieTemperatureInfo"):
        temp = c_int(0)
        ret = mxSmlGetDieTemperatureInfo(device_id, die_id, sensor, temp)
        return (ret, temp.value)
    else:
        return mxsml_get_device_temperature_info(device_id, sensor)


def mxsml_get_device_ip_usage(device_id, ip): # ret: (MxSmlReturn, int)
    usage = c_int(0)
    ret = mxSmlGetDeviceIpUsage(device_id, ip, usage)
    return (ret, usage.value)


def mxsml_get_die_ip_usage(device_id, die_id, ip): # ret: (MxSmlReturn, int)
    if hasattr(_module, "mxSmlGetDieIpUsage"):
        usage = c_int(0)
        ret = mxSmlGetDieIpUsage(device_id, die_id, ip, usage)
        return (ret, usage.value)
    else:
        return mxsml_get_device_ip_usage(device_id, ip)


def mxsml_get_device_clocks(device_id, ip): # ret: (MxSmlReturn, List[int])
    clocksSize = c_uint(8)
    clocksMhz = (c_uint * 8)()
    ret = mxSmlGetClocks(device_id, ip, clocksSize, clocksMhz)
    return (ret, [clockMhz for clockMhz in clocksMhz])


def mxsml_get_die_clocks(device_id, die_id, ip): # ret: (MxSmlReturn, List[int])
    if hasattr(_module, "mxSmlGetDieClocks"):
        clocksSize = c_uint(8)
        clocksMhz = (c_uint * 8)()
        ret = mxSmlGetDieClocks(device_id, die_id, ip, clocksSize, clocksMhz)
        return (ret, [clockMhz for clockMhz in clocksMhz])
    else:
        return mxsml_get_device_clocks(device_id, ip)


def mxsml_get_device_metaxlink_bandwidth(device_id, mxlk_type): # ret: (MxSmlReturn, int, MxSmlMetaXLinkBandwidth*)
    entryList = []
    bandwidth = (MxSmlMetaXLinkBandwidth* METAX_LINK_NUM)(*entryList)
    linkSize = c_uint(8)
    ret = mxSmlGetMetaXLinkBandwidth(device_id, mxlk_type, linkSize, bandwidth)
    return (ret, linkSize.value, bandwidth)


def mxsml_get_device_metaxlink_traffic_stat(device_id, mxlk_type): # ret: (MxSmlReturn, int, MxSmlMetaXLinkTrafficStat*)
    if hasattr(_module, "mxSmlGetMetaXLinkTrafficStat"):
        entryList = []
        stat = (MxSmlMetaXLinkTrafficStat* METAX_LINK_NUM)(*entryList)
        linkSize = c_uint(METAX_LINK_NUM)
        ret = mxSmlGetMetaXLinkTrafficStat(device_id, mxlk_type, byref(linkSize), stat)
        return (ret, linkSize.value, stat)
    else:
        return (MxSmlReturn.MXSML_OperationNotSupport, 0, [])


def mxsml_get_device_metaxlink_aer(device_id): # ret: (MxSmlReturn, int, mxlkAer*)
    if hasattr(_module, "mxSmlGetMetaXLinkAer"):
        entryList = []
        mxlkAer = (MxSmlMetaXLinkAer* METAX_LINK_NUM)(*entryList)
        linkSize = c_uint(METAX_LINK_NUM)
        ret = mxSmlGetMetaXLinkAer(device_id, linkSize, mxlkAer)
        return (ret, linkSize.value, mxlkAer)
    else:
        return (MxSmlReturn.MXSML_OperationNotSupport, 0, None)


def mxsml_get_current_clocks_throttle_reason(device_id, die_id): # ret: (MxSmlReturn, int)
    if hasattr(_module, "mxSmlGetDieCurrentClocksThrottleReason"):
        clocksThrottleReason = c_ulonglong(0)
        ret = mxSmlGetDieCurrentClocksThrottleReason(device_id, die_id, byref(clocksThrottleReason))
        return (ret, clocksThrottleReason.value)
    if hasattr(_module, "mxSmlGetCurrentClocksThrottleReason"):
        clocksThrottleReason = c_ulonglong(0)
        ret = mxSmlGetCurrentClocksThrottleReason(device_id, byref(clocksThrottleReason))
        return (ret, clocksThrottleReason.value)
    else:
        return (MxSmlReturn.MXSML_OperationNotSupport, 0)


def mxsml_get_die_total_ecc_errors(device_id, die_id): # ret: (MxSmlReturn, MxSmlEccErrorCount)
    if hasattr(_module, "mxSmlGetDieTotalEccErrors"):
        eccCounts = MxSmlEccErrorCount()
        ret = mxSmlGetDieTotalEccErrors(device_id, die_id, byref(eccCounts))
        return (ret, eccCounts)
    else:
        return (MxSmlReturn.MXSML_OperationNotSupport, None)


def mxsml_get_device_metaxlink_topo(device_id): # ret: (MxSmlReturn, MxSmlMetaXLinkTopo)
    if hasattr(_module, "mxSmlGetMetaXLinkTopo"):
        topoInfo = MxSmlMetaXLinkTopo()
        ret = mxSmlGetMetaXLinkTopo(device_id, byref(topoInfo))
        return (ret, topoInfo)
    else:
        return (MxSmlReturn.MXSML_OperationNotSupport, None)


def mxsml_get_sgpu_count(device_id): # ret: sgpu count
    if hasattr(_module, "mxSmlGetSgpuCount"):
        sgpu_count = mxSmlGetSgpuCount(device_id)
        return sgpu_count
    else:
        return -1


def mxsml_get_sgpu_info(device_id, sgpu_id): # ret: (MxSmlReturn, MxSmlSgpuInfo)
    sgpuInfo = MxSmlSgpuInfo()
    ret = mxSmlGetSgpuInfo(device_id, sgpu_id, byref(sgpuInfo))
    return (ret, sgpuInfo)


def mxsml_get_sgpu_annotations_id(device_id, sgpu_id): # ret: annotations id
    size = c_uint(96)
    entrylist = []
    annotations_id = (c_char * 96)(*entrylist)
    ret = mxSmlGetSgpuAnnotationsId(device_id, sgpu_id, annotations_id, byref(size))
    return annotations_id.value.decode('ASCII')


def mxsml_get_local_and_multiple_remote_uuid(): # ret: (MxSmlReturn, string, string, string)
    if hasattr(_module, "mxSmlGetLocalAndMultipleRemoteUuid"):
        entrylist = []
        localUuid = (c_char * 64)(*entrylist)
        remoteUuid1 = (c_char * 64)(*entrylist)
        remoteUuid2 = (c_char * 64)(*entrylist)
        remotes = (POINTER(c_char)*2)(*[remoteUuid1, remoteUuid2])
        remotesSize = c_uint(2)
        uuidSize = c_uint(64)
        ret = mxSmlGetLocalAndMultipleRemoteUuid(localUuid, remotes, byref(remotesSize), byref(uuidSize))
        return (ret, localUuid.value.decode('ASCII'), remoteUuid1.value.decode('ASCII'), remoteUuid2.value.decode('ASCII'))
    else:
        return (MxSmlReturn.MXSML_OperationNotSupport, "", "", "")


def mxsml_init(): # ret: MxSmlReturn
    if hasattr(_module, "mxSmlInitWithFlags"):
        return mxSmlInitWithFlags(1)
    else:
        return mxSmlInit()


def mxsml_get_device_pci_event(device_id, event_type): # ret: (MxSmlReturn, MxSmlPciEventInfo*, int)
    if hasattr(_module, "mxSmlGetPciEventInfo"):
        entrylist = []
        eventInfo = (MxSmlPciEventInfo*32)(*entrylist)
        size = c_uint(32)
        ret = mxSmlGetPciEventInfo(device_id, event_type, eventInfo, byref(size))
        return (ret, eventInfo, size.value)
    else:
        return (MxSmlReturn.MXSML_OperationNotSupport, None, 0)


ras_register_name_map = {
    MxSmlRasIp.MXSML_Ras_mc: "MC", MxSmlRasIp.MXSML_Ras_pcie: "PCIE",
    MxSmlRasIp.MXSML_Ras_fuse: "FUSE", MxSmlRasIp.MXSML_Ras_g2d: "G2D",
    MxSmlRasIp.MXSML_Ras_int: "INT", MxSmlRasIp.MXSML_Ras_hag: "HAG",
    MxSmlRasIp.MXSML_Ras_metalk: "METALK",
    MxSmlRasIp.MXSML_Ras_smp0: "SMP0", MxSmlRasIp.MXSML_Ras_smp1: "SMP1",
    MxSmlRasIp.MXSML_Ras_ccx0: "CCX0", MxSmlRasIp.MXSML_Ras_ccx1: "CCX1",
    MxSmlRasIp.MXSML_Ras_ccx2: "CCX2", MxSmlRasIp.MXSML_Ras_ccx3: "CCX3",
    MxSmlRasIp.MXSML_Ras_dla0: "DLA0", MxSmlRasIp.MXSML_Ras_dla1: "DLA1",
    MxSmlRasIp.MXSML_Ras_vpue0: "VPUE0", MxSmlRasIp.MXSML_Ras_vpue1: "VPUE1",
    MxSmlRasIp.MXSML_Ras_vpud0: "VPUD0", MxSmlRasIp.MXSML_Ras_vpud1: "VPUD1",
    MxSmlRasIp.MXSML_Ras_vpud2: "VPUD2", MxSmlRasIp.MXSML_Ras_vpud3: "VPUD3",
    MxSmlRasIp.MXSML_Ras_vpud4: "VPUD4", MxSmlRasIp.MXSML_Ras_vpud5: "VPUD5",
    MxSmlRasIp.MXSML_Ras_vpud6: "VPUD6", MxSmlRasIp.MXSML_Ras_vpud7: "VPUD7",
    MxSmlRasIp.MXSML_Ras_dma0: "DMA0", MxSmlRasIp.MXSML_Ras_dma1: "DMA1",
    MxSmlRasIp.MXSML_Ras_dma2: "DMA2", MxSmlRasIp.MXSML_Ras_dma3: "DMA3",
    MxSmlRasIp.MXSML_Ras_dma4: "DMA4",
    MxSmlRasIp.MXSML_Ras_mcctl0: "MCCTL0", MxSmlRasIp.MXSML_Ras_mcctl1: "MCCTL1",
    MxSmlRasIp.MXSML_Ras_mcctl2: "MCCTL2", MxSmlRasIp.MXSML_Ras_mcctl3: "MCCTL3",
    MxSmlRasIp.MXSML_Ras_dhub1: "DHUB1", MxSmlRasIp.MXSML_Ras_dhub2: "DHUB2",
    MxSmlRasIp.MXSML_Ras_dhub3: "DHUB3", MxSmlRasIp.MXSML_Ras_dhub4: "DHUB4",
    MxSmlRasIp.MXSML_Ras_dhub5: "DHUB5", MxSmlRasIp.MXSML_Ras_dhub6: "DHUB6",
    MxSmlRasIp.MXSML_Ras_dhub7: "DHUB7",
    MxSmlRasIp.MXSML_Ras_ath: "ATH", MxSmlRasIp.MXSML_Ras_atul20: "ATUL20",
    MxSmlRasIp.MXSML_Ras_atul21: "ATUL21",
    MxSmlRasIp.MXSML_Ras_xsc: "XSC", MxSmlRasIp.MXSML_Ras_ce: "CE",
    MxSmlRasIp.MXSML_Ras_eth: "ETH", MxSmlRasIp.MXSML_Ras_ethsc: "ETHSC"
}


def __parse_ras_error_data(ras_data):
    ras_error_data = []
    for index in range(ras_data.showRasErrorSize):
        if ras_data.rasErrorRegister[index].rasErrorUe != 0:
            ras_register_name = (str(ras_register_name_map[ras_data.rasErrorRegister[index].rasIp.value])
                                 + " reg" + str(ras_data.rasErrorRegister[index].registerIndex) + " ue")
            ras_error_data += [(ras_register_name, ras_data.rasErrorRegister[index].rasErrorUe)]

        if ras_data.rasErrorRegister[index].rasErrorCe != 0:
            ras_register_name = (str(ras_register_name_map[ras_data.rasErrorRegister[index].rasIp.value])
                                 + " reg" + str(ras_data.rasErrorRegister[index].registerIndex) + " ce")
            ras_error_data += [(ras_register_name, ras_data.rasErrorRegister[index].rasErrorCe)]
    return ras_error_data


def mxsml_get_die_ras_count(device_id, die_id): # ret: (MxSmlReturn, List[Tuple[str, int]])
    if hasattr(_module, "mxSmlGetDieRasErrorData"):
        device_RasErrorData = MxSmlRasErrorData()
        ret = mxSmlGetDieRasErrorData(device_id, die_id, byref(device_RasErrorData))
        if ret == MxSmlReturn.MXSML_Success:
            return (ret, __parse_ras_error_data(device_RasErrorData))
        else:
            return (ret, [])
    elif hasattr(_module, "mxSmlGetRasErrorData"):
        device_RasErrorData = MxSmlRasErrorData()
        ret = mxSmlGetRasErrorData(device_id, byref(device_RasErrorData))
        if ret == MxSmlReturn.MXSML_Success:
            return (ret, __parse_ras_error_data(device_RasErrorData))
        else:
            return (ret, [])
    else:
        return (MxSmlReturn.MXSML_OperationNotSupport, None)


def mxsml_get_die_ras_status(device_id, die_id): # ret: (MxSmlReturn, List[Tuple[str, int]])
    if hasattr(_module, "mxSmlGetDieRasStatusData"):
        device_RasStatusData = MxSmlRasStatusData()
        ret = mxSmlGetDieRasStatusData(device_id, die_id, byref(device_RasStatusData))
        ras_status = []
        if ret == MxSmlReturn.MXSML_Success:
            for index in range(device_RasStatusData.showRasStatusSize):
                ras_register_name = (str(ras_register_name_map[device_RasStatusData.rasStatusRegister[index].rasIp.value])
                                     + " reg" + str(device_RasStatusData.rasStatusRegister[index].registerIndex))
                ras_status += [(ras_register_name, device_RasStatusData.rasStatusRegister[index].registerData)]
        return (ret, ras_status)
    elif hasattr(_module, "mxSmlGetRasStatusData"):
        device_RasStatusData = MxSmlRasStatusData()
        ret = mxSmlGetRasStatusData(device_id, byref(device_RasStatusData))
        ras_status = []
        if ret == MxSmlReturn.MXSML_Success:
            for index in range(device_RasStatusData.showRasStatusSize):
                ras_register_name = (str(ras_register_name_map[device_RasStatusData.rasStatusRegister[index].rasIp.value])
                                     + " reg" + str(device_RasStatusData.rasStatusRegister[index].registerIndex))
                ras_status += [(ras_register_name, device_RasStatusData.rasStatusRegister[index].registerData)]
        return (ret, ras_status)
    else:
        return (MxSmlReturn.MXSML_OperationNotSupport, None)


def mxsml_get_die_unavailable_reason(device_id, die_id): # ret: (MxSmlReturn, str)
    if hasattr(_module, "mxSmlGetDieUnavailableReason"):
        unavailable_reason = ""
        sml_unavailable_reason = MxSmlDeviceUnavailableReasonInfo()
        ret = mxSmlGetDieUnavailableReason(device_id, die_id, byref(sml_unavailable_reason))
        if ret == MxSmlReturn.MXSML_Success:
            unavailable_reason = sml_unavailable_reason.unavailableReason.decode('ASCII')
        return (ret, unavailable_reason)
    else:
        return (MxSmlReturn.MXSML_OperationNotSupport, unavailable_reason)


def mxsml_get_device_current_dpm_ip_perf_level(device_id, ip): # ret: (MxSmlReturn, int)
    dpmIpPerfLevel = c_uint(0)
    ret = mxSmlGetCurrentDpmIpPerfLevel(device_id, ip, byref(dpmIpPerfLevel))
    return (ret, dpmIpPerfLevel.value)


def mxsml_get_die_current_dpm_ip_perf_level(device_id, die_id, ip): # ret: (MxSmlReturn, int)
    if hasattr(_module, "mxSmlGetCurrentDieDpmIpPerfLevel"):
        dpmIpPerfLevel = c_uint(0)
        ret = mxSmlGetCurrentDieDpmIpPerfLevel(device_id, die_id, ip, byref(dpmIpPerfLevel))
        return (ret, dpmIpPerfLevel.value)
    else:
        return mxsml_get_device_current_dpm_ip_perf_level(device_id, ip)


def mxsml_get_device_pmbus_info(device_id, unit): # ret: (MxSmlReturn, MxSmlPmbusInfo)
    pmbusPowerInfo = MxSmlPmbusInfo()
    ret = mxSmlGetPmbusInfo(device_id, unit, byref(pmbusPowerInfo))
    return (ret, pmbusPowerInfo)


def mxsml_get_die_pmbus_info(device_id, die_id, unit): # ret: (MxSmlReturn, MxSmlPmbusInfo)
    if hasattr(_module, "mxSmlGetDiePmbusInfo"):
        pmbusPowerInfo = MxSmlPmbusInfo()
        ret = mxSmlGetDiePmbusInfo(device_id, die_id, unit, byref(pmbusPowerInfo))
        return (ret, pmbusPowerInfo)
    else:
        return mxsml_get_device_pmbus_info(device_id, unit)
