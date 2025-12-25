#!/usr/bin/env python3

"""
Copyright © 2022 MetaX Integrated Circuits (Shanghai) Co., Ltd. All Rights Reserved.

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

from ctypes import *
import os

path_libmxsml = ""
path_libmxsml_array = [
    os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "libmxsml.so"
    ),
    "/opt/mxdriver/lib/libmxsml.so",
    "/opt/maca/lib/libmxsml.so",
    "/opt/mxn100/lib/libmxsml.so"
]
for file in path_libmxsml_array:
    if os.path.isfile(file):
        print("Using lib from %s" % file)
        path_libmxsml = file
        break

if not path_libmxsml:
    print("Unable to find mxsml library.")
    exit(1)

try:
    mxsml = cdll.LoadLibrary(path_libmxsml)
except OSError:
    print("Unable to load mxsml library.")
    exit(1)

DeviceId = c_uint
DieId = c_uint
SgpuId = c_uint

class MxSmlReturn(c_uint):
    MXSML_Success = 0
    MXSML_Failure = 1
    MXSML_NoDevice = 2
    MXSML_OperationNotSupport = 3
    MXSML_SysfsError = 4
    MXSML_SysfsWriteError = 5
    MXSML_InvalidDeviceId = 6
    MXSML_InvalidDieId = 7
    MXSML_PermissionDenied = 8
    MXSML_InvalidInput = 9
    MXSML_InsufficientSize = 10
    MXSML_Reserved3 = 11
    MXSML_IOControlFailure = 12
    MXSML_MmapFailure = 13
    MXSML_UnMmapFailure = 14
    MXSML_InvalidInputForMmap = 15
    MXSML_Reserved1 = 16
    MXSML_Reserved2 = 17
    MXSML_TargetVfNotFound = 18
    MXSML_InvalidFrequency = 19
    MXSML_FlrNotReady = 20
    MXSML_OpenDeviceFileFailure = 21
    MXSML_CloseDeviceFileFailure = 22
    MXSML_BusyDevice = 23
    MXSML_MmioNotEnough = 24
    MXSML_GetPciBridgeFailure = 25
    MXSML_LoadDllFailure = 26

class MxSmlDeviceBrand(c_uint):
    MXSML_Brand_Unknown = 0
    MXSML_Brand_N = 1
    MXSML_Brand_C = 2
    MXSML_Brand_G = 3

class MxSmlDeviceVirtualizationMode(c_uint):
    MXSML_Virtualization_Mode_None = 0
    MXSML_Virtualization_Mode_Pf = 1
    MXSML_Virtualization_Mode_Vf = 2

class MxSmlRasIp(c_uint):
    MXSML_Ras_mc = 0
    MXSML_Ras_pcie = 1
    MXSML_Ras_fuse = 2
    MXSML_Ras_g2d = 3
    MXSML_Ras_int = 4
    MXSML_Ras_hag = 5
    MXSML_Ras_metalk = 6
    MXSML_Ras_smp0 = 7
    MXSML_Ras_smp1 = 8
    MXSML_Ras_ccx0 = 9
    MXSML_Ras_ccx1 = 10
    MXSML_Ras_ccx2 = 11
    MXSML_Ras_ccx3 = 12
    MXSML_Ras_dla0 = 13
    MXSML_Ras_dla1 = 14
    MXSML_Ras_vpue0 = 15
    MXSML_Ras_vpue1 = 16
    MXSML_Ras_vpud0 = 17
    MXSML_Ras_vpud1 = 18
    MXSML_Ras_vpud2 = 19
    MXSML_Ras_vpud3 = 20
    MXSML_Ras_vpud4 = 21
    MXSML_Ras_vpud5 = 22
    MXSML_Ras_vpud6 = 23
    MXSML_Ras_vpud7 = 24
    MXSML_Ras_dma0 = 25
    MXSML_Ras_dma1 = 26
    MXSML_Ras_dma2 = 27
    MXSML_Ras_dma3 = 28
    MXSML_Ras_dma4 = 29
    MXSML_Ras_mcctl0 = 30
    MXSML_Ras_mcctl1 = 31
    MXSML_Ras_mcctl2 = 32
    MXSML_Ras_mcctl3 = 33
    MXSML_Ras_dhub1 = 34
    MXSML_Ras_dhub2 = 35
    MXSML_Ras_dhub3 = 36
    MXSML_Ras_dhub4 = 37
    MXSML_Ras_dhub5 = 38
    MXSML_Ras_dhub6 = 39
    MXSML_Ras_dhub7 = 40
    MXSML_Ras_ath = 41
    MXSML_Ras_atul20 = 42
    MXSML_Ras_atul21 = 43
    MXSML_Ras_xsc = 44
    MXSML_Ras_ce = 45
    MXSML_Ras_eth = 46
    MXSML_Ras_ethsc = 47

class MxSmlVersionUnit(c_uint):
    MXSML_Version_Bios = 0
    MXSML_Version_Driver = 1
    MXSML_Version_Smp0 = 2
    MXSML_Version_Smp1 = 3
    MXSML_Version_Ccx0 = 4
    MXSML_Version_Ccx1 = 5
    MXSML_Version_Ccx2 = 6
    MXSML_Version_Ccx3 = 7        # only valid for N-class device

class MxSmlUsageIp(c_uint):
    MXSML_Usage_Dla = 0           # only valid for N-class device
    MXSML_Usage_Vpue = 1
    MXSML_Usage_Vpud = 2
    MXSML_Usage_G2d = 3           # only valid for N-class device
    MXSML_Usage_Xcore = 4         # only valid for C-class device

class MxSmlDeviceInfo(Structure):
    _fields_ = [
        ("deviceId", DeviceId),
        ("type", c_uint),         # deprecated, do not use
        ("bdfId", c_char*32),
        ("gpuId", c_uint),
        ("nodeId", c_uint),
        ("uuid", c_char*96),
        ("brand", c_uint),
        ("mode", c_uint),
        ("deviceName", c_char*32)
    ]

class MxSmlRasErrorRegister(Structure):
    _fields_ = [
        ("rasIp", MxSmlRasIp),
        ("registerIndex", c_uint),
        ("rasErrorUe", c_int),
        ("rasErrorCe", c_int)
    ]

class MxSmlRasErrorData(Structure):
    _fields_ = [
        ("rasErrorRegister", MxSmlRasErrorRegister*128),
        ("showRasErrorSize", c_int)
    ]

class MxSmlRasRegister(Structure):
    _fields_ = [
        ("rasIp", MxSmlRasIp),
        ("registerIndex", c_uint),
        ("registerData", c_int)
    ]

class MxSmlRasStatusData(Structure):
    _fields_ = [
        ("rasStatusRegister", MxSmlRasRegister*128),
        ("showRasStatusSize", c_int)
    ]

class MxSmlVirtualDeviceIds(Structure):
    _fields_ = [
        ("number", c_int),
        ("deviceId", c_int*128)
    ]

class MxSmlTemperatureSensors(c_uint):
    MXSML_Temperature_Hotspot = 0
    MXSML_Temperature_HotLimit = 1
    MXSML_Temperature_Soc = 2
    MXSML_Temperature_Core = 3
    MXSML_Temperature_Ccx_Dnoc = 4
    MXSML_Temperature_Csc_Fuse = 5
    MXSML_Temperature_Ccx_Dla_Vpue1_Ath = 6
    MXSML_Temperature_Vpue1 = 7
    MXSML_Temperature_Vpue0 = 8
    MXSML_Temperature_Atul2 = 9
    MXSML_Temperature_Dla1 = 10
    MXSML_Temperature_Dla0 = 11
    MXSML_Temperature_Emc0 = 12
    MXSML_Temperature_Emc1 = 13
    MXSML_Temperature_Sgm = 14
    MXSML_Temperature_Hbm = 15

class MxSmlHbmBandwidth(Structure):
    _fields_ = [
        ("hbmBandwidthReqTotal", c_int),
        ("hbmBandwidthRespTotal", c_int)
    ]

class MxSmlMemoryInfo(Structure):
    _fields_ = [
        ("visVramTotal", c_long),
        ("visVramUse", c_long),
        ("vramTotal", c_long),
        ("vramUse", c_long),
        ("xttTotal", c_long),
        ("xttUse", c_long)
    ]

class MxSmlPmbusUnit(c_uint):
    MXSML_Pmbus_Soc = 0
    MXSML_Pmbus_Core = 1
    MXSML_Pmbus_Hbm = 2
    MXSML_Pmbus_Pcie = 3
    MXSML_Pmbus_Hbm2 = 4
    MXSML_Pmbus_Pcie2 = 5

class MxSmlPmbusInfo(Structure):
    _fields_ = [
        ("voltage", c_uint),
        ("current", c_uint),
        ("power", c_uint)
    ]

class MxSmlBoardWayElectricInfo(Structure):
    _fields_ = [
        ("voltage", c_uint),
        ("current", c_uint),
        ("power", c_uint)
    ]

class MxSmlClockIp(c_uint):
    MXSML_Clock_Csc = 0
    MXSML_Clock_Dla = 1
    MXSML_Clock_Mc = 2
    MXSML_Clock_Mc0 = 3
    MXSML_Clock_Mc1 = 4
    MXSML_Clock_Vpue = 5
    MXSML_Clock_Vpud = 6
    MXSML_Clock_Soc = 7
    MXSML_Clock_Dnoc = 8
    MXSML_Clock_G2D = 9
    MXSML_Clock_Ccx = 10
    MXSML_Clock_Xcore = 11

class MxSmlFwIp(c_uint):
    MXSML_Fw_IpName_SMP0 = 0
    MXSML_Fw_IpName_SMP1 = 1
    MXSML_Fw_IpName_CCX0 = 2
    MXSML_Fw_IpName_CCX1 = 3
    MXSML_Fw_IpName_CCX2 = 4
    MXSML_Fw_IpName_CCX3 = 5

class MxSmlLoglevel(c_uint):
    MXSML_Loglevel_NONE = 0
    MXSML_Loglevel_FATAL = 1
    MXSML_Loglevel_ERROR = 2
    MXSML_Loglevel_WARN = 3
    MXSML_Loglevel_INFO = 4
    MXSML_Loglevel_DEBUG = 5
    MXSML_Loglevel_VERBOSE = 6
    MXSML_Loglevel_UNKNOWN = 7

class MxSmlDpmIp(c_uint):
    MXSML_Dpm_Dla = 0
    MXSML_Dpm_Xcore = 1
    MXSML_Dpm_Mc = 2
    MXSML_Dpm_Soc = 3
    MXSML_Dpm_Dnoc = 4
    MXSML_Dpm_Vpue = 5
    MXSML_Dpm_Vpud = 6
    MXSML_Dpm_Hbm = 7
    MXSML_Dpm_G2d = 8
    MXSML_Dpm_Ravs = 9
    MXSML_Dpm_Tdc = 10
    MXSML_Dpm_Pcc = 11
    MXSML_Dpm_HbmPower = 12
    MXSML_Dpm_Ccx = 13
    MXSML_Dpm_Ip_Group = 14
    MXSML_Dpm_Dma = 15
    MXSML_Dpm_Csc = 16

class MxSmlMetaXLinkState(c_uint):
    MXSML_MetaXLink_State_Enabled = 0
    MXSML_MetaXLink_State_Smi_Disabled = 1
    MXSML_MetaXLink_State_Vf_Disabled = 2
    MXSML_MetaXLink_State_GpuNum_Disabled = 3
    MXSML_MetaXLink_State_Training_Disabled = 4

class MxSmlMxlkPortState(c_uint):
    MXSML_Mxlk_Port_State_NoTraining = 0
    MXSML_Mxlk_Port_State_Up = 1
    MXSML_Mxlk_Port_State_Down_Optical_InPlace = 2
    MXSML_Mxlk_Port_State_Down_Optical_OutPlace = 3
    MXSML_Mxlk_Port_State_Down_Optical_NoUse = 4
    MXSML_Mxlk_Port_State_NoUse = 5

class MxSmlPcieThroughput(Structure):
    _fields_ = [
        ("rx", c_int),
        ("tx", c_int)
    ]

class MxSmlDmaEngineBandwidth(Structure):
    _fields_ = [
        ("readReqBandwidth", c_int),
        ("readRespBandwidth", c_int),
        ("writeReqBandwidth", c_int),
        ("writeRespBandwidth", c_int)
    ]

class MxSmlProcessGpuInfo(Structure):
    _fields_ = [
        ("bdfId", c_char*32),
        ("gpuId", c_uint),
        ("gpuMemoryUsage", c_ulong)
    ]

class MxSmlProcessInfo(Structure):
    _fields_ = [
        ("processId", c_uint),
        ("processName", c_char*64),
        ("gpuNumber", c_uint),
        ("processGpuInfo", MxSmlProcessGpuInfo*64)
    ]

class MxSmlProcessGpuInfo_v2(Structure):
    _fields_ = [
        ("bdfId", c_char*32),
        ("gpuId", c_uint),
        ("gpuMemoryUsage", c_ulong),
        ("dieId", c_uint)
    ]

class MxSmlProcessInfo_v2(Structure):
    _fields_ = [
        ("processId", c_uint),
        ("processName", c_char*64),
        ("gpuNumber", c_uint),
        ("processGpuInfo", MxSmlProcessGpuInfo_v2*64)
    ]

class MxSmlMetaXLinkType(c_uint):
    MXSML_MetaXLink_Input = 0
    MXSML_MetaXLink_Target = 1

class MxSmlMetaXLinkBandwidth(Structure):
    _fields_ = [
        ("requestBandwidth", c_int),
        ("reponseBandwidth", c_int)
    ]

class MxSmlMetaXLinkTrafficStat(Structure):
    _fields_ = [
        ("requestTrafficStat", c_long),
        ("reponseTrafficStat", c_long)
    ]

class MxSmlMetaXLinkAer(Structure):
    _fields_ = [
        ("ceAer", c_int),
        ("ueAer", c_int)
    ]

METAX_LINK_NUM=7
class MxSmlMetaXLinkInfo(Structure):
    _fields_ = [
        ("speed", c_float * METAX_LINK_NUM),
        ("width", c_uint * METAX_LINK_NUM)
    ]

class MxSmlPcieInfo(Structure):
    _fields_ = [
        ("speed", c_float),
        ("width", c_uint)
    ]

class MxSmlOpticalModuleStatus(Structure):
    _fields_ = [
        ("temperature", c_int),
        ("voltage", c_uint),
        ("moduleState", c_uint),
        ("dataPathState", c_uint),
        ("rxState", c_uint*2),
        ("version", c_uint*2)
    ]

class MxSmlPciEventType(c_uint):
    MXSML_Pci_Event_AER_UE = 0
    MXSML_Pci_Event_AER_CE = 1
    MXSML_Pci_Event_SYNFLD = 2
    MXSML_Pci_Event_DBE = 3
    MXSML_Pci_Event_MMIO = 4

class MxSmlPciEventInfo(Structure):
    _fields_ = [
        ("bitNumber", c_int),
        ("count", c_uint),
        ("firstTime", c_char*20),
        ("name", c_char*64)
    ]

class MxSmlSgpuInfo(Structure):
    _fields_ = [
        ("parentDeviceId", c_uint),
        ("sgpuId", c_uint),
        ("vramQuota", c_uint),
        ("swQueuePriority", c_uint),
        ("computeQuota", c_uint),
        ("minor", c_uint),
        ("deviceQueuePriority", c_uint),
        ("uuid", c_char*94)
    ]

class MxSmlSgpuMemoryInfo(Structure):
    _fields_ = [
        ("total", c_long),
        ("used", c_long),
        ("free", c_long)
    ]

class MxSmlEccErrorCount(Structure):
    _fields_ = [
        ("sramCE", c_uint),
        ("sramUE", c_uint),
        ("dramCE", c_uint),
        ("dramUE", c_uint),
        ("retiredPage", c_uint)
    ]

class MxSmlMetaXLinkTopo(Structure):
    _fields_ = [
        ("topologyId", c_uint),
        ("socketId", c_uint),
        ("dieId", c_uint)
    ]

class MxSmlDeviceUnavailableReasonInfo(Structure):
    _fields_ = [
        ("unavailableCode", c_int),
        ("unavailableReason", c_char*64)
    ]

class MxSmlEthThroughput(Structure):
    _fields_ = [
        ("rx", c_int),
        ("tx", c_int),
    ]

mxSmlInit = mxsml.mxSmlInit
mxSmlInit.restype = c_uint

mxSmlInitWithFlags = mxsml.mxSmlInitWithFlags
mxSmlInitWithFlags.argtypes = [c_uint]
mxSmlInitWithFlags.restype = c_uint

mxSmlGetMacaVersion = mxsml.mxSmlGetMacaVersion
mxSmlGetMacaVersion.argtypes = [POINTER(c_char), POINTER(c_uint)]
mxSmlGetMacaVersion.restype = c_uint

mxSmlGetDeviceCount = mxsml.mxSmlGetDeviceCount
mxSmlGetDeviceCount.restype = c_uint

mxSmlGetPfDeviceCount = mxsml.mxSmlGetPfDeviceCount
mxSmlGetPfDeviceCount.restype = c_uint

mxSmlGetDeviceDieCount = mxsml.mxSmlGetDeviceDieCount
mxSmlGetDeviceDieCount.argtypes = [DeviceId, POINTER(c_uint)]
mxSmlGetDeviceDieCount.restype = c_uint

mxSmlGetVirtualDevicesByPhysicalId = mxsml.mxSmlGetVirtualDevicesByPhysicalId
mxSmlGetVirtualDevicesByPhysicalId.argtypes = [DeviceId, POINTER(MxSmlVirtualDeviceIds)]
mxSmlGetVirtualDevicesByPhysicalId.restype = c_uint

mxSmlGetDeviceInfo = mxsml.mxSmlGetDeviceInfo
mxSmlGetDeviceInfo.argtypes = [DeviceId, POINTER(MxSmlDeviceInfo)]
mxSmlGetDeviceInfo.restype = c_uint

mxSmlGetRasErrorData = mxsml.mxSmlGetRasErrorData
mxSmlGetRasErrorData.argtypes = [DeviceId, POINTER(MxSmlRasErrorData)]
mxSmlGetRasErrorData.restype = c_uint

mxSmlGetDieRasErrorData = mxsml.mxSmlGetDieRasErrorData
mxSmlGetDieRasErrorData.argtypes = [DeviceId, DieId, POINTER(MxSmlRasErrorData)]
mxSmlGetDieRasErrorData.restype = c_uint

mxSmlGetRasStatusData = mxsml.mxSmlGetRasStatusData
mxSmlGetRasStatusData.argtypes = [DeviceId, POINTER(MxSmlRasStatusData)]
mxSmlGetRasStatusData.restype = c_uint

mxSmlGetDieRasStatusData = mxsml.mxSmlGetDieRasStatusData
mxSmlGetDieRasStatusData.argtypes = [DeviceId, DieId, POINTER(MxSmlRasStatusData)]
mxSmlGetDieRasStatusData.restype = c_uint

mxSmlGetTemperatureInfo = mxsml.mxSmlGetTemperatureInfo
mxSmlGetTemperatureInfo.argtypes = [DeviceId, MxSmlTemperatureSensors, POINTER(c_int)]
mxSmlGetTemperatureInfo.restype = c_uint

mxSmlGetDieTemperatureInfo = mxsml.mxSmlGetDieTemperatureInfo
mxSmlGetDieTemperatureInfo.argtypes = [DeviceId, DieId, MxSmlTemperatureSensors, POINTER(c_int)]
mxSmlGetDieTemperatureInfo.restype = c_uint

mxSmlGetHbmBandWidth = mxsml.mxSmlGetHbmBandWidth
mxSmlGetHbmBandWidth.argtypes = [DeviceId, POINTER(MxSmlHbmBandwidth)]
mxSmlGetHbmBandWidth.restype = c_uint

mxSmlGetDieHbmBandWidth = mxsml.mxSmlGetDieHbmBandWidth
mxSmlGetDieHbmBandWidth.argtypes = [DeviceId, DieId, POINTER(MxSmlHbmBandwidth)]
mxSmlGetDieHbmBandWidth.restype = c_uint

mxSmlGetMemoryInfo = mxsml.mxSmlGetMemoryInfo
mxSmlGetMemoryInfo.argtypes = [DeviceId, POINTER(MxSmlMemoryInfo)]
mxSmlGetMemoryInfo.restype = c_uint

mxSmlGetDieMemoryInfo = mxsml.mxSmlGetDieMemoryInfo
mxSmlGetDieMemoryInfo.argtypes = [DeviceId, DieId, POINTER(MxSmlMemoryInfo)]
mxSmlGetDieMemoryInfo.restype = c_uint

mxSmlGetPmbusInfo = mxsml.mxSmlGetPmbusInfo
mxSmlGetPmbusInfo.argtypes = [DeviceId, MxSmlPmbusUnit, POINTER(MxSmlPmbusInfo)]
mxSmlGetPmbusInfo.restype = c_uint

mxSmlGetDiePmbusInfo = mxsml.mxSmlGetDiePmbusInfo
mxSmlGetDiePmbusInfo.argtypes = [DeviceId, DieId, MxSmlPmbusUnit, POINTER(MxSmlPmbusInfo)]
mxSmlGetDiePmbusInfo.restype = c_uint

mxSmlGetBoardPowerInfo = mxsml.mxSmlGetBoardPowerInfo
BoardWaySize = c_uint
mxSmlGetBoardPowerInfo.argtypes = [DeviceId, POINTER(BoardWaySize), POINTER(MxSmlBoardWayElectricInfo)]
mxSmlGetBoardPowerInfo.restypes = c_uint

mxSmlGetClocks = mxsml.mxSmlGetClocks
clocksSize = c_uint
mxSmlGetClocks.argtypes = [DeviceId, MxSmlClockIp, POINTER(clocksSize), POINTER(c_uint)]
mxSmlGetClocks.restypes = c_uint

mxSmlGetDieClocks = mxsml.mxSmlGetDieClocks
clocksSize = c_uint
mxSmlGetDieClocks.argtypes = [DeviceId, DieId, MxSmlClockIp, POINTER(clocksSize), POINTER(c_uint)]
mxSmlGetDieClocks.restypes = c_uint

mxSmlGetPcieThroughput = mxsml.mxSmlGetPcieThroughput
mxSmlGetPcieThroughput.argtypes = [DeviceId, POINTER(MxSmlPcieThroughput)]
mxSmlGetPcieThroughput.restype = c_uint

mxSmlGetDmaBandwidth = mxsml.mxSmlGetDmaBandwidth
DmaBandwidthSize = c_uint
mxSmlGetDmaBandwidth.argtypes = [DeviceId, POINTER(MxSmlDmaEngineBandwidth), POINTER(DmaBandwidthSize)]
mxSmlGetDmaBandwidth.restype = c_uint

mxSmlGetNumberOfProcess = mxsml.mxSmlGetNumberOfProcess
mxSmlGetNumberOfProcess.argtypes = [POINTER(c_uint)]
mxSmlGetNumberOfProcess.restype = c_uint

mxSmlGetProcessInfo = mxsml.mxSmlGetProcessInfo
mxSmlGetProcessInfo.argtypes = [c_uint, POINTER(MxSmlProcessInfo)]
mxSmlGetProcessInfo.restype = c_uint

mxSmlGetProcessInfo_v2 = mxsml.mxSmlGetProcessInfo_v2
mxSmlGetProcessInfo_v2.argtypes = [c_uint, POINTER(MxSmlProcessInfo_v2)]
mxSmlGetProcessInfo_v2.restype = c_uint

mxSmlGetSingleGpuProcess = mxsml.mxSmlGetSingleGpuProcess
mxSmlGetSingleGpuProcess.argtypes = [c_uint, POINTER(c_uint), POINTER(MxSmlProcessInfo)]
mxSmlGetSingleGpuProcess.restype = c_uint

mxSmlGetSingleGpuProcess_v2 = mxsml.mxSmlGetSingleGpuProcess_v2
mxSmlGetSingleGpuProcess_v2.argtypes = [c_uint, POINTER(c_uint), POINTER(MxSmlProcessInfo_v2)]
mxSmlGetSingleGpuProcess_v2.restype = c_uint

mxSmlGetMetaXLinkBandwidth = mxsml.mxSmlGetMetaXLinkBandwidth
linkSize = c_uint
mxSmlGetMetaXLinkBandwidth.argtypes = [DeviceId, MxSmlMetaXLinkType, POINTER(linkSize), POINTER(MxSmlMetaXLinkBandwidth)]
mxSmlGetMetaXLinkBandwidth.restype = c_uint

mxSmlGetMetaXLinkTrafficStat = mxsml.mxSmlGetMetaXLinkTrafficStat
linkSize = c_uint
mxSmlGetMetaXLinkTrafficStat.argtypes = [DeviceId, MxSmlMetaXLinkType, POINTER(linkSize), POINTER(MxSmlMetaXLinkTrafficStat)]
mxSmlGetMetaXLinkTrafficStat.restype = c_uint

mxSmlGetMetaXLinkAer = mxsml.mxSmlGetMetaXLinkAer
linkSize = c_uint
mxSmlGetMetaXLinkAer.argtypes = [DeviceId, POINTER(linkSize), POINTER(MxSmlMetaXLinkAer)]
mxSmlGetMetaXLinkAer.restype = c_uint

mxSmlGetMetaXLinkInfo = mxsml.mxSmlGetMetaXLinkInfo
mxSmlGetMetaXLinkInfo.argtypes = [DeviceId, POINTER(MxSmlMetaXLinkInfo)]
mxSmlGetMetaXLinkInfo.restype = c_uint

mxSmlGetDpmIpClockInfo = mxsml.mxSmlGetDpmIpClockInfo
mxSmlGetDpmIpClockInfo.argtypes = [DeviceId, c_uint, POINTER(c_uint), POINTER(c_uint)]
mxSmlGetDpmIpClockInfo.restype = c_uint

mxSmlGetDpmIpVddInfo = mxsml.mxSmlGetDpmIpVddInfo
mxSmlGetDpmIpVddInfo.argtypes = [DeviceId, c_uint, POINTER(c_uint), POINTER(c_uint)]
mxSmlGetDpmIpVddInfo.restype = c_uint

mxSmlGetCurrentDpmIpPerfLevel = mxsml.mxSmlGetCurrentDpmIpPerfLevel
mxSmlGetCurrentDpmIpPerfLevel.argtypes = [DeviceId, c_uint, POINTER(c_uint)]
mxSmlGetCurrentDpmIpPerfLevel.restype = c_uint

mxSmlGetCurrentDieDpmIpPerfLevel = mxsml.mxSmlGetCurrentDieDpmIpPerfLevel
mxSmlGetCurrentDieDpmIpPerfLevel.argtypes = [DeviceId, DieId, c_uint, POINTER(c_uint)]
mxSmlGetCurrentDieDpmIpPerfLevel.restype = c_uint

mxSmlGetDeviceVersion = mxsml.mxSmlGetDeviceVersion
mxSmlGetDeviceVersion.argtypes = [DeviceId, c_uint, POINTER(c_char), POINTER(c_uint)]
mxSmlGetDeviceVersion.restype = c_uint

mxSmlGetDeviceDieVersion = mxsml.mxSmlGetDeviceDieVersion
mxSmlGetDeviceDieVersion.argtypes = [DeviceId, DieId, c_uint, POINTER(c_char), POINTER(c_uint)]
mxSmlGetDeviceDieVersion.restype = c_uint

mxSmlGetDeviceIpUsage = mxsml.mxSmlGetDeviceIpUsage
mxSmlGetDeviceIpUsage.argtypes = [DeviceId, c_uint, POINTER(c_int)]
mxSmlGetDeviceIpUsage.restype = c_uint

mxSmlGetDieIpUsage = mxsml.mxSmlGetDieIpUsage
mxSmlGetDieIpUsage.argtypes = [DeviceId, DieId, c_uint, POINTER(c_int)]
mxSmlGetDieIpUsage.restype = c_uint

mxSmlGetFwIpLoglevel = mxsml.mxSmlGetFwIpLoglevel
mxSmlGetFwIpLoglevel.argtypes = [DeviceId, c_uint, POINTER(c_uint)]
mxSmlGetFwIpLoglevel.restype = c_uint

mxSmlGetErrorString = mxsml.mxSmlGetErrorString
mxSmlGetErrorString.argtypes = [c_uint]
mxSmlGetErrorString.restype = c_char_p

mxSmlGetPcieInfo = mxsml.mxSmlGetPcieInfo
mxSmlGetPcieInfo.argtypes = [DeviceId, POINTER(MxSmlPcieInfo)]
mxSmlGetPcieInfo.restype = c_uint

mxSmlGetPcieMaxLinkInfo = mxsml.mxSmlGetPcieMaxLinkInfo
mxSmlGetPcieMaxLinkInfo.argtypes = [DeviceId, POINTER(MxSmlPcieInfo)]
mxSmlGetPcieMaxLinkInfo.restype = c_uint

mxSmlGetDeviceState = mxsml.mxSmlGetDeviceState
mxSmlGetDeviceState.argtypes = [DeviceId, POINTER(c_int)]
mxSmlGetDeviceState.restype = c_uint

mxSmlGetLocalAndRemoteUuid = mxsml.mxSmlGetLocalAndRemoteUuid
mxSmlGetLocalAndRemoteUuid.argtypes = [POINTER(c_char), POINTER(c_char), POINTER(c_uint)]
mxSmlGetLocalAndRemoteUuid.restype = c_uint

mxSmlGetLocalAndMultipleRemoteUuid = mxsml.mxSmlGetLocalAndMultipleRemoteUuid
mxSmlGetLocalAndMultipleRemoteUuid.argtypes = [POINTER(c_char), POINTER(POINTER(c_char)), POINTER(c_uint), POINTER(c_uint)]
mxSmlGetLocalAndMultipleRemoteUuid.restype = c_uint

mxSmlGetOpticalModuleStatus = mxsml.mxSmlGetOpticalModuleStatus
mxSmlGetOpticalModuleStatus.argtypes = [DeviceId, POINTER(MxSmlOpticalModuleStatus), POINTER(c_uint)]
mxSmlGetOpticalModuleStatus.restype = c_uint

mxSmlGetCurrentClocksThrottleReason = mxsml.mxSmlGetCurrentClocksThrottleReason
mxSmlGetCurrentClocksThrottleReason.argtypes = [DeviceId, POINTER(c_ulonglong)]
mxSmlGetCurrentClocksThrottleReason.restype = c_uint

mxSmlGetDieCurrentClocksThrottleReason = mxsml.mxSmlGetDieCurrentClocksThrottleReason
mxSmlGetDieCurrentClocksThrottleReason.argtypes = [DeviceId, DieId, POINTER(c_ulonglong)]
mxSmlGetDieCurrentClocksThrottleReason.restype = c_uint

mxSmlGetBoardPowerLimit = mxsml.mxSmlGetBoardPowerLimit
mxSmlGetBoardPowerLimit.argtypes = [DeviceId, POINTER(c_uint)]
mxSmlGetBoardPowerLimit.restype = c_uint

mxSmlGetMetaXLinkState = mxsml.mxSmlGetMetaXLinkState
mxSmlGetMetaXLinkState.argTypes = [DeviceId, POINTER(MxSmlMetaXLinkState), POINTER(c_char), POINTER(c_uint)]
mxSmlGetMetaXLinkState.restype = c_uint

mxSmlGetMetaXLinkPortState = mxsml.mxSmlGetMetaXLinkPortState
mxSmlGetMetaXLinkPortState.argTypes = [DeviceId, POINTER(MxSmlMxlkPortState), POINTER(c_uint)]
mxSmlGetMetaXLinkPortState.restype = c_uint

mxSmlGetPciMmioState = mxsml.mxSmlGetPciMmioState
mxSmlGetPciMmioState.argTypes = [DeviceId, POINTER(c_uint)]
mxSmlGetPciMmioState.restype = c_uint

mxSmlGetPciEventInfo = mxsml.mxSmlGetPciEventInfo
mxSmlGetPciEventInfo.argTypes = [DeviceId, MxSmlPciEventType, POINTER(MxSmlPciEventInfo), POINTER(c_uint)]
mxSmlGetPciEventInfo.restype = c_uint

mxSmlGetBoardSerial = mxsml.mxSmlGetBoardSerial
mxSmlGetBoardSerial.argtypes = [DeviceId, POINTER(c_char), POINTER(c_uint)]
mxSmlGetBoardSerial.restype = c_uint

mxSmlGetDeviceIsaVersion = mxsml.mxSmlGetDeviceIsaVersion
mxSmlGetDeviceIsaVersion.argTypes = [DeviceId, POINTER(c_int)]
mxSmlGetDeviceIsaVersion.restype = c_uint

mxSmlGetSgpuCount = mxsml.mxSmlGetSgpuCount
mxSmlGetSgpuCount.argtypes = [DeviceId]
mxSmlGetSgpuCount.restype = c_uint

mxSmlGetSgpuInfo = mxsml.mxSmlGetSgpuInfo
mxSmlGetSgpuInfo.argtypes = [DeviceId, SgpuId, POINTER(MxSmlSgpuInfo)]
mxSmlGetSgpuInfo.restype = c_uint

mxSmlGetSgpuAlias = mxsml.mxSmlGetSgpuAlias
mxSmlGetSgpuAlias.argtypes = [DeviceId, SgpuId, POINTER(c_char), POINTER(c_uint)]
mxSmlGetSgpuAlias.restype = c_uint

mxSmlGetSgpuMemory = mxsml.mxSmlGetSgpuMemory
mxSmlGetSgpuMemory.argtypes = [DeviceId, SgpuId, POINTER(MxSmlSgpuMemoryInfo)]
mxSmlGetSgpuMemory.restype = c_uint

mxSmlGetSgpuUsage = mxsml.mxSmlGetSgpuUsage
mxSmlGetSgpuUsage.argtypes = [DeviceId, SgpuId, POINTER(c_int)]
mxSmlGetSgpuUsage.restype = c_uint

mxSmlGetSgpuAnnotationsId = mxsml.mxSmlGetSgpuAnnotationsId
mxSmlGetSgpuAnnotationsId.argtypes = [DeviceId, SgpuId, POINTER(c_char), POINTER(c_uint)]
mxSmlGetSgpuAnnotationsId.restype = c_uint

mxSmlGetDeviceTimeslice = mxsml.mxSmlGetDeviceTimeslice
mxSmlGetDeviceTimeslice.argtypes = [DeviceId, POINTER(c_uint)]
mxSmlGetDeviceTimeslice.restype = c_uint

mxSmlSetDeviceTimeslice = mxsml.mxSmlSetDeviceTimeslice
mxSmlSetDeviceTimeslice.argtypes = [DeviceId, c_uint]
mxSmlSetDeviceTimeslice.restype = c_uint

mxSmlGetTotalEccErrors = mxsml.mxSmlGetTotalEccErrors
mxSmlGetTotalEccErrors.argtypes = [DeviceId, POINTER(MxSmlEccErrorCount)]
mxSmlGetTotalEccErrors.restype = c_uint

mxSmlGetDieTotalEccErrors = mxsml.mxSmlGetDieTotalEccErrors
mxSmlGetDieTotalEccErrors.argtypes = [DeviceId, DieId, POINTER(MxSmlEccErrorCount)]
mxSmlGetDieTotalEccErrors.restype = c_uint

mxSmlGetMetaXLinkTopo = mxsml.mxSmlGetMetaXLinkTopo
mxSmlGetMetaXLinkTopo.argtypes = [DeviceId, POINTER(MxSmlMetaXLinkTopo)]
mxSmlGetMetaXLinkTopo.restype = c_uint

mxSmlGetDieUnavailableReason = mxsml.mxSmlGetDieUnavailableReason
mxSmlGetDieUnavailableReason.argtypes = [DeviceId, DieId, POINTER(MxSmlDeviceUnavailableReasonInfo)]
mxSmlGetDieUnavailableReason.restype = c_uint

mxSmlGetEthThroughput = mxsml.mxSmlGetEthThroughput
mxSmlGetEthThroughput.argtypes = [DeviceId, POINTER(MxSmlEthThroughput)]
mxSmlGetEthThroughput.restype = c_uint

if __name__ == "__main__":
    def PrintStructure(s):
        for field in s._fields_:
            print (field[0], getattr(s, field[0]))

    ret = mxSmlInit()
    if ret != MxSmlReturn.MXSML_Success:
        print("mxsml init failed: %s" % mxSmlGetErrorString(ret).decode('ASCII'))
        exit(1)

    ret = mxSmlInitWithFlags(0)
    if ret != MxSmlReturn.MXSML_Success:
        print("mxSmlInitWithFlags failed: %s" % mxSmlGetErrorString(ret).decode('ASCII'))
        exit(1)

    size = c_uint(64)
    entrylist = []
    macaVersion = (c_char * 64)(*entrylist)
    ret = mxSmlGetMacaVersion(macaVersion, size)
    if ret != MxSmlReturn.MXSML_Success:
        print("mxSmlGetMacaVersion failed: " + mxSmlGetErrorString(ret).decode('ASCII'))
    else:
        print("mxSmlGetMacaVersion success: " + macaVersion.value.decode('ASCII'))

    deviceNum = mxSmlGetDeviceCount()
    print("mxSmlGetDeviceCount: " + str(deviceNum))

    if deviceNum < 1:
        exit(0)

    device_id = 0
    die_id = 0

    temperature = c_int(0)
    tempType = MxSmlTemperatureSensors.MXSML_Temperature_Core
    ret = mxSmlGetTemperatureInfo(device_id, tempType, temperature)
    if ret != MxSmlReturn.MXSML_Success:
        print("mxSmlGetTemperatureInfo failed: " + mxSmlGetErrorString(ret).decode('ASCII'))
    else:
        print("mxSmlGetTemperatureInfo success")
        print("mxSmlGetTemperatureInfo {}".format(temperature))

    ret = mxSmlGetDieTemperatureInfo(device_id, die_id, tempType, temperature)
    if ret != MxSmlReturn.MXSML_Success:
        print("mxSmlGetDieTemperatureInfo failed: " + mxSmlGetErrorString(ret).decode('ASCII'))
    else:
        print("mxSmlGetDieTemperatureInfo success")
        print("mxSmlGetDieTemperatureInfo {}".format(temperature))

    memory = MxSmlMemoryInfo()
    ret = mxSmlGetMemoryInfo(device_id, byref(memory))
    if ret != MxSmlReturn.MXSML_Success:
        print("mxSmlGetMemoryInfo failed: " + mxSmlGetErrorString(ret).decode('ASCII'))
    else:
        print("mxSmlGetMemoryInfo success")
        PrintStructure(memory)

    ret = mxSmlGetDieMemoryInfo(device_id, die_id, byref(memory))
    if ret != MxSmlReturn.MXSML_Success:
        print("mxSmlGetDieMemoryInfo failed: " + mxSmlGetErrorString(ret).decode('ASCII'))
    else:
        print("mxSmlGetDieMemoryInfo success")
        PrintStructure(memory)

    device_info = MxSmlDeviceInfo()
    ret = mxSmlGetDeviceInfo(device_id, byref(device_info))
    if ret != MxSmlReturn.MXSML_Success:
        print("mxSmlGetDeviceInfo failed: " + mxSmlGetErrorString(ret).decode('ASCII'))
    else:
        print("mxSmlGetDeviceInfo success: " + device_info.deviceName.decode('ASCII'))

    device_RasErrorData = MxSmlRasErrorData()
    ret = mxSmlGetRasErrorData(device_id, byref(device_RasErrorData))
    if ret != MxSmlReturn.MXSML_Success:
        print("mxSmlGetRasErrorData failed: " + mxSmlGetErrorString(ret).decode('ASCII'))
    else:
        print("mxSmlGetRasErrorData success")
        PrintStructure(device_RasErrorData)

    device_RasStatusData = MxSmlRasStatusData()
    ret = mxSmlGetRasStatusData(device_id, byref(device_RasStatusData))
    if ret != MxSmlReturn.MXSML_Success:
        print("mxSmlGetRasStatusData failed: " + mxSmlGetErrorString(ret).decode('ASCII'))
    else:
        print("mxSmlGetRasStatusData success")
        PrintStructure(device_RasStatusData)

    ret = mxSmlGetDieRasStatusData(device_id, die_id, byref(device_RasStatusData))
    if ret != MxSmlReturn.MXSML_Success:
        print("mxSmlGetDieRasStatusData failed: " + mxSmlGetErrorString(ret).decode('ASCII'))
    else:
        print("mxSmlGetDieRasStatusData success")
        PrintStructure(device_RasStatusData)

    hbmBw = MxSmlHbmBandwidth()
    ret = mxSmlGetHbmBandWidth(device_id, byref(hbmBw))
    if ret != MxSmlReturn.MXSML_Success:
        print("mxSmlGetHbmBandWidth failed: " + mxSmlGetErrorString(ret).decode('ASCII'))
    else:
        print("mxSmlGetHbmBandWidth success")
        PrintStructure(hbmBw)

    pmbusInfo = MxSmlPmbusInfo()
    pmbusUnit = MxSmlPmbusUnit.MXSML_Pmbus_Soc
    ret = mxSmlGetPmbusInfo(device_id, pmbusUnit, byref(pmbusInfo))
    if ret != MxSmlReturn.MXSML_Success:
        print("mxSmlGetPmbusInfo failed: " + mxSmlGetErrorString(ret).decode('ASCII'))
    else:
        print("mxSmlGetPmbusInfo success")
        PrintStructure(pmbusInfo)

    ret = mxSmlGetDiePmbusInfo(device_id, die_id, pmbusUnit, byref(pmbusInfo))
    if ret != MxSmlReturn.MXSML_Success:
        print("mxSmlGetDiePmbusInfo failed: " + mxSmlGetErrorString(ret).decode('ASCII'))
    else:
        print("mxSmlGetDiePmbusInfo success")
        PrintStructure(pmbusInfo)

    entryBoardInfo = []
    boardPower = (MxSmlBoardWayElectricInfo* 3)(*entryBoardInfo)
    BoardWaySize = c_uint(3)
    ret = mxSmlGetBoardPowerInfo(device_id, BoardWaySize, boardPower)
    if ret != MxSmlReturn.MXSML_Success:
        print("mxSmlGetBoardPowerInfo failed: " + mxSmlGetErrorString(ret).decode('ASCII'))
    else:
        print("mxSmlGetBoardPowerInfo success")
        i = 0
        while i < BoardWaySize.value:
            PrintStructure(boardPower[i])
            i += 1

    unit = MxSmlClockIp.MXSML_Clock_Soc
    clocksSize = c_uint(2)
    clocksMhz = (c_uint * 2)()
    ret = mxSmlGetClocks(device_id, unit, clocksSize, clocksMhz)
    if ret != MxSmlReturn.MXSML_Success:
        print("mxSmlGetClocks failed: " + mxSmlGetErrorString(ret).decode('ASCII'))
    else:
        print("mxSmlGetClocks success")
        print("MXSML_Clock_Soc:", clocksMhz[0], clocksMhz[1])

    pcieThroughput = MxSmlPcieThroughput()
    ret = mxSmlGetPcieThroughput(device_id, byref(pcieThroughput))
    if ret != MxSmlReturn.MXSML_Success:
        print("mxSmlGetPcieThroughput failed: " + mxSmlGetErrorString(ret).decode('ASCII'))
    else:
        print("mxSmlGetPcieThroughput success")
        PrintStructure(pcieThroughput)

    entrylist = []
    dmaBw = (MxSmlDmaEngineBandwidth* 5)(*entrylist)
    size = c_uint(5)
    ret = mxSmlGetDmaBandwidth(device_id, dmaBw, size)
    if ret != MxSmlReturn.MXSML_Success:
        print("mxSmlGetDmaBandwidth failed: " + mxSmlGetErrorString(ret).decode('ASCII'))
    else:
        print("mxSmlGetDmaBandwidth success")
        i = 0
        while i < size.value:
            PrintStructure(dmaBw[i])
            i += 1

    processNumber = c_uint(0)
    ret = mxSmlGetNumberOfProcess(byref(processNumber))
    if ret != MxSmlReturn.MXSML_Success:
        print("mxSmlGetNumberOfProcess failed: " + mxSmlGetErrorString(ret).decode('ASCII'))
    else:
        print("mxSmlGetNumberOfProcess success")
        print("NumberOfProcess: " + str(processNumber))

    entrylist = []
    processNumber = processNumber.value
    processInfo = (MxSmlProcessInfo*processNumber)(*entrylist)
    ret = mxSmlGetProcessInfo(processNumber, processInfo)
    if ret != MxSmlReturn.MXSML_Success:
        print("mxSmlGetProcessInfo failed: " + mxSmlGetErrorString(ret).decode('ASCII'))
    else:
        print("mxSmlGetProcessInfo success")
        i = 0
        while i < processNumber:
            PrintStructure(processInfo[i])
            i += 1

    entrylist = []
    processInfo = (MxSmlProcessInfo_v2*processNumber)(*entrylist)
    ret = mxSmlGetProcessInfo_v2(processNumber, processInfo)
    if ret != MxSmlReturn.MXSML_Success:
        print("mxSmlGetProcessInfo_v2 failed: " + mxSmlGetErrorString(ret).decode('ASCII'))
    else:
        print("mxSmlGetProcessInfo_v2 success")
        i = 0
        while i < processNumber:
            PrintStructure(processInfo[i])
            i += 1

    entrylist = []
    processNumber = c_uint(64)
    processInfo = (MxSmlProcessInfo*64)(*entrylist)
    ret = mxSmlGetSingleGpuProcess(device_id, byref(processNumber), processInfo)
    if ret != MxSmlReturn.MXSML_Success:
        print("mxSmlGetSingleGpuProcess failed: " + mxSmlGetErrorString(ret).decode('ASCII'))
    else:
        print("mxSmlGetSingleGpuProcess success, process number: " + str(processNumber))
        i = 0
        while i < processNumber.value:
            PrintStructure(processInfo[i])
            i += 1

    entrylist = []
    processNumber = c_uint(64)
    processInfo = (MxSmlProcessInfo_v2*64)(*entrylist)
    ret = mxSmlGetSingleGpuProcess_v2(device_id, byref(processNumber), processInfo)
    if ret != MxSmlReturn.MXSML_Success:
        print("mxSmlGetSingleGpuProcess_v2 failed: " + mxSmlGetErrorString(ret).decode('ASCII'))
    else:
        print("mxSmlGetSingleGpuProcess_v2 success, process number: " + str(processNumber))
        i = 0
        while i < processNumber.value:
            PrintStructure(processInfo[i])
            i += 1

    entryLinklist = []
    metaxLinkBandwidth = (MxSmlMetaXLinkBandwidth* 7)(*entryLinklist)
    metaxLinkType = MxSmlMetaXLinkType.MXSML_MetaXLink_Input
    linkSize = c_uint(7)
    ret = mxSmlGetMetaXLinkBandwidth(device_id, metaxLinkType, linkSize, metaxLinkBandwidth)
    if ret != MxSmlReturn.MXSML_Success:
        print("mxSmlGetMetaXLinkBandwidth failed: " + mxSmlGetErrorString(ret).decode('ASCII'))
    else:
        print("mxSmlGetMetaXLinkBandwidth success")
        i = 0
        while i < linkSize.value:
            PrintStructure(metaxLinkBandwidth[i])
            i += 1

    entryLinklist = []
    metaxLinkTrafficStat = (MxSmlMetaXLinkTrafficStat* 7)(*entryLinklist)
    metaxLinkType = MxSmlMetaXLinkType.MXSML_MetaXLink_Input
    linkSize = c_uint(7)
    ret = mxSmlGetMetaXLinkTrafficStat(device_id, metaxLinkType, linkSize, metaxLinkTrafficStat)
    if ret != MxSmlReturn.MXSML_Success:
        print("mxSmlGetMetaXLinkTrafficStat failed: " + mxSmlGetErrorString(ret).decode('ASCII'))
    else:
        print("mxSmlGetMetaXLinkTrafficStat success")
        i = 0
        while i < linkSize.value:
            PrintStructure(metaxLinkTrafficStat[i])
            i += 1

    entryLinklist = []
    metaxLinkAer = (MxSmlMetaXLinkAer* 7)(*entryLinklist)
    linkSize = c_uint(7)
    ret = mxSmlGetMetaXLinkAer(device_id, linkSize, metaxLinkAer)
    if ret != MxSmlReturn.MXSML_Success:
        print("mxSmlGetMetaXLinkAer failed: " + mxSmlGetErrorString(ret).decode('ASCII'))
    else:
        print("mxSmlGetMetaXLinkAer success")
        i = 0
        while i < linkSize.value:
            PrintStructure(metaxLinkAer[i])
            i += 1

    dpmIp = c_uint(2) #MC
    entrylist = []
    clockInfo = (c_uint * 12)(*entrylist)
    size = c_uint(12)
    ret = mxSmlGetDpmIpClockInfo(device_id, dpmIp, clockInfo, size)
    if ret != MxSmlReturn.MXSML_Success:
        print("mxSmlGetDpmIpClockInfo failed: " + mxSmlGetErrorString(ret).decode('ASCII'))
    else:
        print("mxSmlGetDpmIpClockInfo success")
        i = 0
        while i < size.value:
            print("mc[{}] clock {}".format(i, clockInfo[i]))
            i += 1

    dpmIp = c_uint(2) #MC
    entrylist = []
    voltageInfo = (c_uint * 12)(*entrylist)
    size = c_uint(12)
    ret = mxSmlGetDpmIpVddInfo(device_id, dpmIp, voltageInfo, size)
    if ret != MxSmlReturn.MXSML_Success:
        print("mxSmlGetDpmIpVddInfo failed: " + mxSmlGetErrorString(ret).decode('ASCII'))
    else:
        print("mxSmlGetDpmIpVddInfo success")
        i = 0
        while i < size.value:
            print("mc[{}] voltage {}".format(i, voltageInfo[i]))
            i += 1

    dpmIp = c_uint(3) #soc
    dpmIpPerfLevel = c_uint(0)
    ret = mxSmlGetCurrentDpmIpPerfLevel(device_id, dpmIp, dpmIpPerfLevel)
    if ret != MxSmlReturn.MXSML_Success:
        print("mxSmlGetCurrentDpmIpPerfLevel failed: " + mxSmlGetErrorString(ret).decode('ASCII'))
    else:
        print("mxSmlGetCurrentDpmIpPerfLevel success")
        print("soc CurrentPerfLevel {}".format(dpmIpPerfLevel))

    unit = MxSmlVersionUnit.MXSML_Version_Bios #bios
    size = c_uint(64)
    entrylist = []
    version = (c_char * 64)(*entrylist)
    ret = mxSmlGetDeviceVersion(device_id, unit, version, size)
    if ret != MxSmlReturn.MXSML_Success:
        print("mxSmlGetDeviceVersion failed: " + mxSmlGetErrorString(ret).decode('ASCII'))
    else:
        print("mxSmlGetDeviceVersion success: " + version.value.decode('ASCII'))

    ip = MxSmlUsageIp.MXSML_Usage_Vpue
    usage = c_int(0)
    ret = mxSmlGetDeviceIpUsage(device_id, ip, usage)
    if ret != MxSmlReturn.MXSML_Success:
        print("mxSmlGetDeviceIpUsage failed: " + mxSmlGetErrorString(ret).decode('ASCII'))
    else:
        print("mxSmlGetDeviceIpUsage success: " + str(usage))

    ip = MxSmlFwIp.MXSML_Fw_IpName_SMP0
    loglevel = c_uint(0)
    ret = mxSmlGetFwIpLoglevel(device_id, ip, loglevel)
    if ret != MxSmlReturn.MXSML_Success:
        print("mxSmlGetFwIpLoglevel for smp0 failed: " + mxSmlGetErrorString(ret).decode('ASCII'))
    else:
        print("mxSmlGetFwIpLoglevel for smp0 success: " + str(loglevel))

    pcieInfo = MxSmlPcieInfo()
    ret = mxSmlGetPcieInfo(device_id, byref(pcieInfo))
    if ret != MxSmlReturn.MXSML_Success:
        print("mxSmlGetPcieInfo failed: " + mxSmlGetErrorString(ret).decode('ASCII'))
    else:
        print("mxSmlGetPcieInfo success")
        PrintStructure(pcieInfo)

    ret = mxSmlGetPcieMaxLinkInfo(device_id, byref(pcieInfo))
    if ret != MxSmlReturn.MXSML_Success:
        print("mxSmlGetPcieMaxLinkInfo failed: " + mxSmlGetErrorString(ret).decode('ASCII'))
    else:
        print("mxSmlGetPcieMaxLinkInfo success")
        PrintStructure(pcieInfo)

    mxlkInfo = MxSmlMetaXLinkInfo()
    ret = mxSmlGetMetaXLinkInfo(device_id, byref(mxlkInfo))
    if ret != MxSmlReturn.MXSML_Success:
        print("mxSmlGetMetaXLinkInfo failed: " + mxSmlGetErrorString(ret).decode('ASCII'))
    else:
        print("mxSmlGetMetaXLinkInfo success")
    for idx, item in enumerate(mxlkInfo.speed):
        print("MetaXLink Port#{} -- {}".format(idx, item))

    deviceState = c_int(0)
    ret = mxSmlGetDeviceState(device_id, deviceState)
    if ret != MxSmlReturn.MXSML_Success:
        print("mxSmlGetDeviceState failed: " + mxSmlGetErrorString(ret).decode('ASCII'))
    else:
        print("mxSmlGetDeviceState success: " + str(deviceState))

    entrylist = []
    localUuid = (c_char * 64)(*entrylist)
    remoteUuid = (c_char * 64)(*entrylist)
    uuidSize = c_uint(64)
    ret = mxSmlGetLocalAndRemoteUuid(localUuid, remoteUuid, byref(uuidSize))
    if ret != MxSmlReturn.MXSML_Success:
        print("mxSmlGetLocalAndRemoteUuid failed: " + mxSmlGetErrorString(ret).decode('ASCII'))
    else:
        print("mxSmlGetLocalAndRemoteUuid success: %s %s" % (localUuid.value.decode('ASCII'), remoteUuid.value.decode('ASCII')))

    entrylist = []
    localUuid = (c_char * 64)(*entrylist)
    remoteUuid1 = (c_char * 64)(*entrylist)
    remoteUuid2 = (c_char * 64)(*entrylist)
    remotes = (POINTER(c_char)*2)(*[remoteUuid1, remoteUuid2])
    remotesSize = c_uint(2)
    uuidSize = c_uint(64)
    ret = mxSmlGetLocalAndMultipleRemoteUuid(localUuid, remotes, byref(remotesSize), byref(uuidSize))
    if ret != MxSmlReturn.MXSML_Success:
        print("mxSmlGetLocalAndMultipleRemoteUuid failed: " + mxSmlGetErrorString(ret).decode('ASCII'))
    else:
        print("mxSmlGetLocalAndMultipleRemoteUuid success: local uuid %s" % (localUuid.value.decode('ASCII')))
        print("remotesSize %d, remoteUuid1 %s, remoteUuid2 %s" % (remotesSize.value, remoteUuid1.value.decode('ASCII'),
            remoteUuid2.value.decode('ASCII')))

    size = c_uint(3)
    entrylist = []
    opticalModuleStatus = (MxSmlOpticalModuleStatus*3)(*entrylist)
    ret = mxSmlGetOpticalModuleStatus(device_id, opticalModuleStatus, byref(size))
    if ret != MxSmlReturn.MXSML_Success:
        print("mxSmlGetOpticalModuleStatus failed: " + mxSmlGetErrorString(ret).decode('ASCII'))
    else:
        print("mxSmlGetOpticalModuleStatus success")
        i = 0
        while i < size.value:
            PrintStructure(opticalModuleStatus[i])
            i += 1

    clocksThrottleReason = c_ulonglong(0)
    ret = mxSmlGetCurrentClocksThrottleReason(device_id, byref(clocksThrottleReason))
    if ret != MxSmlReturn.MXSML_Success:
        print("mxSmlGetCurrentClocksThrottleReason failed: " + mxSmlGetErrorString(ret).decode('ASCII'))
    else:
        print("mxSmlGetCurrentClocksThrottleReason success: " + str(clocksThrottleReason))

    powerLimit = c_uint(0)
    ret = mxSmlGetBoardPowerLimit(device_id, byref(powerLimit))
    if ret != MxSmlReturn.MXSML_Success:
        print("mxSmlGetBoardPowerLimit failed: " + mxSmlGetErrorString(ret).decode('ASCII'))
    else:
        print("mxSmlGetBoardPowerLimit success: " + str(powerLimit))

    mxlkStateCode = MxSmlMetaXLinkState(MxSmlMetaXLinkState.MXSML_MetaXLink_State_Enabled)
    entrylist = []
    mxlkState = (c_char * 128)(*entrylist)
    size = c_uint(128)
    ret = mxSmlGetMetaXLinkState(device_id, byref(mxlkStateCode), mxlkState, byref(size))
    if ret != MxSmlReturn.MXSML_Success:
        print("mxSmlGetMetaXLinkState failed: " + mxSmlGetErrorString(ret).decode('ASCII'))
    else:
        print("mxSmlGetMetaXLinkState success, mxlkStateCode:{} mxlkState:{}".format(mxlkStateCode, mxlkState.value.decode('ASCII')))

    entrylist = []
    mxlkPortState = (MxSmlMxlkPortState * 7)(*entrylist)
    size = c_uint(7)
    ret = mxSmlGetMetaXLinkPortState(device_id, mxlkPortState, byref(size))
    if ret != MxSmlReturn.MXSML_Success:
        print("mxSmlGetMetaXLinkPortState failed: " + mxSmlGetErrorString(ret).decode('ASCII'))
    else:
        print("mxSmlGetMetaXLinkPortState success")

    state = c_uint()
    ret = mxSmlGetPciMmioState(device_id, byref(state))
    if ret != MxSmlReturn.MXSML_Success:
        print("mxSmlGetPciMmioState failed: " + mxSmlGetErrorString(ret).decode('ASCII'))
    else:
        print("mxSmlGetPciMmioState success, state:{}".format(state))

    eventType = MxSmlPciEventType.MXSML_Pci_Event_AER_UE
    entrylist = []
    eventInfo = (MxSmlPciEventInfo*2)(*entrylist)
    size = c_uint(2)
    ret = mxSmlGetPciEventInfo(device_id, eventType, eventInfo, byref(size))
    if ret != MxSmlReturn.MXSML_Success:
        print("mxSmlGetPciEventInfo failed: " + mxSmlGetErrorString(ret).decode('ASCII'))
    else:
        print("mxSmlGetPciEventInfo success")
        i = 0
        while i < size.value:
            PrintStructure(eventInfo[i])
            i += 1

    size = c_uint(32)
    entrylist = []
    boardSerial = (c_char * 32)(*entrylist)
    ret = mxSmlGetBoardSerial(device_id, boardSerial, byref(size))
    if ret != MxSmlReturn.MXSML_Success:
        print("mxSmlGetBoardSerial failed: " + mxSmlGetErrorString(ret).decode('ASCII'))
    else:
        print("mxSmlGetBoardSerial success, baordSerial:{}".format(boardSerial.value.decode('ASCII')))

    isaVersion = c_int(0)
    ret = mxSmlGetDeviceIsaVersion(device_id, byref(isaVersion))
    if ret != MxSmlReturn.MXSML_Success:
        print("mxSmlGetDeviceIsaVersion failed: " + mxSmlGetErrorString(ret).decode('ASCII'))
    else:
        print("mxSmlGetDeviceIsaVersion success, isaVersion:{}".format(isaVersion))

    # sgpu
    sgpuNum = mxSmlGetSgpuCount(device_id)
    print("Device{} mxSmlGetSgpuCount: {}".format(device_id, sgpuNum))

    timeslice = c_uint(0)
    ret = mxSmlGetDeviceTimeslice(device_id, byref(timeslice))
    if ret != MxSmlReturn.MXSML_Success:
        print("Device{} mxSmlGetDeviceTimeslice failed: {}"
                .format(device_id, mxSmlGetErrorString(ret).decode('ASCII')))
    else:
        print("mxSmlGetDeviceTimeslice success, Device{} timeslice: {}"
                .format(device_id, timeslice))

    timeslice = 30
    ret = mxSmlSetDeviceTimeslice(device_id, timeslice)
    if ret != MxSmlReturn.MXSML_Success:
        print("Device{} mxSmlSetDeviceTimeslice failed: {}"
                .format(device_id, mxSmlGetErrorString(ret).decode('ASCII')))
    else:
        print("mxSmlSetDeviceTimeslice success, Device{} timeslice: {}"
                .format(device_id, timeslice))

    for sgpu_id in range(sgpuNum):
        sgpuInfo = MxSmlSgpuInfo()
        ret = mxSmlGetSgpuInfo(device_id, sgpu_id, byref(sgpuInfo))
        if ret != MxSmlReturn.MXSML_Success:
            print("Device{} Sgpu{} mxSmlGetSgpuInfo failed: {}"
                  .format(device_id, sgpuNum, mxSmlGetErrorString(ret).decode('ASCII')))
        else:
            print("mxSmlGetSgpuInfo success")
            PrintStructure(sgpuInfo)

        size = c_uint(32)
        entrylist = []
        alias = (c_char * 32)(*entrylist)
        ret = mxSmlGetSgpuAlias(device_id, sgpu_id, alias, byref(size))
        if ret != MxSmlReturn.MXSML_Success:
            print("Device {} Sgpu {} mxSmlGetSgpuAlias failed: {}"
                  .format(device_id, sgpu_id, mxSmlGetErrorString(ret).decode('ASCII')))
        else:
            print("mxSmlGetSgpuAlias success")
            print("Device {} Sgpu {} Alias {}"
                  .format(device_id, sgpu_id, alias.value.decode('ASCII')))

        memory = MxSmlSgpuMemoryInfo()
        ret = mxSmlGetSgpuMemory(device_id, sgpu_id, byref(memory))
        if ret != MxSmlReturn.MXSML_Success:
            print("Device {} Sgpu {} mxSmlGetSgpuMemory failed: "
                  .format(device_id, sgpu_id, mxSmlGetErrorString(ret).decode('ASCII')))
        else:
            print("mxSmlGetSgpuMemory success")
            PrintStructure(memory)

        usage = c_int(0)
        ret = mxSmlGetSgpuUsage(device_id, sgpu_id, byref(usage))
        if ret != MxSmlReturn.MXSML_Success:
            print("Device {} Sgpu {} mxSmlGetSgpuUsage failed: "
                 .format(device_id, sgpu_id, mxSmlGetErrorString(ret).decode('ASCII')))
        else:
            print("mxSmlGetSgpuUsage success")
            print("Device {} Sgpu {} usage {}".format(device_id, sgpu_id, usage))

        size = c_uint(96)
        entrylist = []
        annotations_id = (c_char * 96)(*entrylist)
        ret = mxSmlGetSgpuAnnotationsId(device_id, sgpu_id, annotations_id, byref(size))
        if ret != MxSmlReturn.MXSML_Success:
            print("Device {} Sgpu {} mxSmlGetSgpuAnnotationsId failed: "
                 .format(device_id, sgpu_id, mxSmlGetErrorString(ret).decode('ASCII')))
        else:
            print("mxSmlGetSgpuAnnotationsId success")
            print("Device {} Sgpu {} annotations_id {}"
                  .format(device_id, sgpu_id, annotations_id.value.decode('ASCII')))

    eccCounts = MxSmlEccErrorCount()
    ret = mxSmlGetTotalEccErrors(device_id, byref(eccCounts))
    if ret != MxSmlReturn.MXSML_Success:
        print("mxSmlGetTotalEccErrors failed: " + mxSmlGetErrorString(ret).decode('ASCII'))
    else:
        print("mxSmlGetTotalEccErrors success")
        print("sram CE:{}  sram UE:{}".format(eccCounts.sramCE, eccCounts.sramUE))
        print("dram CE:{}  dram UE:{}".format(eccCounts.dramCE, eccCounts.dramUE))
        print("retiredPage:{}".format(eccCounts.retiredPage))

    topoInfo = MxSmlMetaXLinkTopo()
    ret = mxSmlGetMetaXLinkTopo(device_id, byref(topoInfo))
    if ret != MxSmlReturn.MXSML_Success:
        print("mxSmlGetMetaXLinkTopo failed: " + mxSmlGetErrorString(ret).decode('ASCII'))
    else:
        print("mxSmlGetMetaXLinkTopo success")
        print("topology id:{}, socker id:{}, die id:{}".format(topoInfo.topologyId, topoInfo.socketId, topoInfo.dieId))

    unavailable_reason = MxSmlDeviceUnavailableReasonInfo()
    ret = mxSmlGetDieUnavailableReason(device_id, die_id, byref(unavailable_reason))
    if ret != MxSmlReturn.MXSML_Success:
        print("mxSmlGetDieUnavailableReason failed: " + mxSmlGetErrorString(ret).decode('ASCII'))
    else:
        print("mxSmlGetDieUnavailableReason success, code:{} "
        .format(unavailable_reason.unavailableCode, unavailable_reason.unavailableReason.decode('ASCII')))