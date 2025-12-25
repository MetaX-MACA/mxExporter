MACAVER ?= "unknown"
NUM_JOB ?= 4
ARCH_L ?= amd64
REG ?= cr.metax-tech.com/cloud
DOCKERTAG = $(REG)/mx-exporter:${MACAVER}

.PHONY: all n100 mxc wheel

all: n100

n100:
	DOCKER_BUILDKIT=1 docker build \
		--build-arg ARCH="$(ARCH_L)" \
		-t $(DOCKERTAG) $(CURDIR)
	docker save $(DOCKERTAG) | gzip > mx-exporter-$(MACAVER).tar.gz
	docker push $(DOCKERTAG)

mxc:
	DOCKER_BUILDKIT=1 docker build \
		--build-arg ARCH="$(ARCH_L)" \
		-t $(DOCKERTAG) $(CURDIR)
	docker save $(DOCKERTAG) | xz -zfT$(NUM_JOB) > mx-exporter-${MACAVER}-$(ARCH_L).xz

wheel:
	python3 setup.py bdist_wheel
	mv dist/*.whl .
	-rm build mx_exporter.egg-info dist -rf
