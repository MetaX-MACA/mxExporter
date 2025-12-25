#!/bin/bash

CONTAINER_TOOL="docker"
CONTAINER_NAME=mx-exporter
IMAGE="cr.metax-tech.com/cloud/mx-exporter:latest"
HOST_PORT=8000
INTERVAL=10000
IB_MONITOR=0
POD_MONITOR=0
MOUNT_POINT="/host"
HOST_NETWORK_MODE=0
ALWAYS_RESTART_MODE=1

usage() {
    cat <<END_USAGE
Usage: sudo bash start_mxexporter.sh [options...]

Examples:
1. export GPU metrics with default config
    "sudo bash start_mxexporter.sh"
2. export GPU metrics and set the HTTP listen port to 9000
    "sudo bash start_mxexporter.sh -p=9000"

Options:
    --help|-h                         Display help message
    --container-tool=<docker|nerdctl> Specific container cmd tool, default: $CONTAINER_TOOL
    --image=<image>                   Specific image, default: "$IMAGE"
    --name|-n=<container name>        Specific container name, default: "$CONTAINER_NAME"
    --port|-p=<port>                  Specific host HTTP listen port, default: $HOST_PORT
    --interval|-i=<interval>          Specific metrics gathering interval, default: $INTERVAL, unit: ms
    --config-file|-c=<file path>      Specific metrics config file path
    --pod-monitor|-pm=<[0|1]>         Disable/Enable k8s pod resource monitoring, default: $POD_MONITOR
    --mount-point|-mp=<path>          Specific container mount path, default: "$MOUNT_POINT"
    --host-network|-hn=<[0|1]>        Disable/Enable host network mode, default: $HOST_NETWORK_MODE
    --always-restart|-ar=<[0|1]>      Disable/Enable container always restart mode, default: $ALWAYS_RESTART_MODE
END_USAGE
}

DOCKER_RUN_ARG=(--hostname=$HOSTNAME)
MXEXPORTER_ARG=

# mount MetaX GPU resources
if [ -c "/dev/mxgvm" ]; then
    DOCKER_RUN_ARG+=(--device=/dev/dri --device=/dev/mxgvm)
else
    DOCKER_RUN_ARG+=(--device=/dev/dri)
fi

while (($#))
do
    case "$1" in
    -h|--help)
        usage
        exit 0
        ;;
    --container-tool=*)
        CONTAINER_TOOL=${1##*=}
        if [ $CONTAINER_TOOL != docker ] && [ $CONTAINER_TOOL != nerdctl ]; then
            echo "Invalid container tool: '$CONTAINER_TOOL', should be one of [docker, nerdctl]"
            exit 1
        fi
        shift
        ;;
    --image=*)
        IMAGE=${1##*=}
        shift
        ;;
    --name=*|-n=*)
        CONTAINER_NAME=${1##*=}
        shift
        ;;
    --port=*|-p=*)
        HOST_PORT=${1##*=}
        MXEXPORTER_ARG="$MXEXPORTER_ARG -p $HOST_PORT"
        shift
        ;;
    --interval=*|-i=*)
        MXEXPORTER_ARG="$MXEXPORTER_ARG -i ${1##*=}"
        shift
        ;;
    --config-file=*|-c=*)
        if [ ! -f ${1##*=} ]; then
            echo "Config file not exist: '${1##*=}'"
            exit 2
        fi
        DOCKER_RUN_ARG+=(-v ${1##*=}:/work/counters.csv)
        MXEXPORTER_ARG="$MXEXPORTER_ARG -c /work/counters.csv"
        shift
        ;;
    --ib-monitor=*|-im=*)
        IB_MONITOR=${1##*=}
        shift
        ;;
    --pod-monitor=*|-pm=*)
        POD_MONITOR=${1##*=}
        shift
        ;;
    --mount-point=*|-mp=*)
        MOUNT_POINT=${1##*=}
        shift
        ;;
    --host-network=*|-hn=*)
        HOST_NETWORK_MODE=${1##*=}
        shift
        ;;
    --always-restart=*|-ar=*)
        ALWAYS_RESTART_MODE=${1##*=}
        shift
        ;;
    *)
        echo "invalid parameter, use -h|--help to get the usage"
        exit 3
        ;;
    esac
done

MXEXPORTER_ARG="$MXEXPORTER_ARG -mp $MOUNT_POINT"
DOCKER_RUN_ARG+=(-v /var/log:$MOUNT_POINT/var/log)

if [ $HOST_NETWORK_MODE -eq 1 ]; then
    DOCKER_RUN_ARG+=(--network host)
else
    DOCKER_RUN_ARG+=(-p $HOST_PORT:$HOST_PORT)
fi

if [ $IB_MONITOR -eq 1 ]; then
    MXEXPORTER_ARG="$MXEXPORTER_ARG -im 1"

    if [ $HOST_NETWORK_MODE != 1 ]; then
        DOCKER_RUN_ARG+=(-v /sys/devices:/sys/devices)
    fi
fi

if [ $POD_MONITOR -eq 1 ]; then
    DOCKER_RUN_ARG+=(-v /var/lib/kubelet/pod-resources:/var/lib/kubelet/pod-resources)
fi

if [ $ALWAYS_RESTART_MODE -eq 1 ]; then
    DOCKER_RUN_ARG+=(--restart=always)
fi

# support sgpu mode
sgpuIndex=`cat /proc/devices |grep sgpu |awk '{print $1}'`
if [ -z $sgpuIndex ]; then
    CMD=($CONTAINER_TOOL run -d --name=$CONTAINER_NAME ${DOCKER_RUN_ARG[@]} $IMAGE $MXEXPORTER_ARG)
else
    CMD=($CONTAINER_TOOL run -d --name=$CONTAINER_NAME ${DOCKER_RUN_ARG[@]} --device-cgroup-rule="c $sgpuIndex:* rmw" $IMAGE $MXEXPORTER_ARG)
fi

echo "${CMD[@]}"
"${CMD[@]}"
