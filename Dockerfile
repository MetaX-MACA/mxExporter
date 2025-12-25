ARG ARCH=amd64
FROM mxcr.io/dev/ubuntu:18.04-${ARCH} as mirror
FROM mxcr.io/hub/ubuntu:18.04-${ARCH}
MAINTAINER "Metax Developers <support-sw@metax-tech.com>"

RUN --mount=type=bind,from=mirror,source=/etc/apt/sources.list,target=/etc/apt/sources.list \
     apt-get update && apt-get install -y --no-install-recommends \
     python3 \
     python3-pip && \
     apt-get clean && \
     rm -rf /var/lib/apt/lists/*

RUN pip3 install --upgrade pip setuptools -i http://repo.metax-tech.com/r/pypi/simple \
    --trusted-host repo.metax-tech.com

RUN pip3 install prometheus_client grpcio protobuf -i http://repo.metax-tech.com/r/pypi/simple \
    --trusted-host repo.metax-tech.com

WORKDIR /opt/mxexporter/
COPY ["mx_exporter/*", "dep/*", "./mx_exporter/"]
ENTRYPOINT ["python3", "-u", "-m", "mx_exporter"]
