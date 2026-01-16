ARG ARCH=amd64
FROM --platform=linux/${ARCH} ubuntu:18.04

LABEL maintainer="Metax Developers <support-sw@metax-tech.com>"

RUN  apt-get update && apt-get install -y --no-install-recommends \
     python3 \
     python3-pip && \
     apt-get clean && \
     rm -rf /var/lib/apt/lists/*

RUN pip3 install --upgrade pip setuptools && pip3 install prometheus_client grpcio protobuf

COPY LICENSE /licenses

WORKDIR /opt/mxexporter/
COPY ["mx_exporter/*", "dep/*", "./mx_exporter/"]
ENTRYPOINT ["python3", "-u", "-m", "mx_exporter"]
