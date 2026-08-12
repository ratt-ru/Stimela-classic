FROM quay.io/stimela/base:1.9.0

# Allow pinning a PyPI version (default: latest)
ARG DDFACET_PYPI_VERSION=""

# Install apt build/runtime dependencies needed for building from source and MPI
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y \
	cmake gcc g++ git curl build-essential \
	libfftw3-dev libopenmpi-dev libpmix-dev libpmi2-0-dev \
	python3-pip python3-dev libhdf5-dev libatlas-base-dev libgsl-dev libcurl4-openssl-dev \
	&& apt-get clean && rm -rf /var/lib/apt/lists/*

# Upgrade pip and install common build-time Python tooling
RUN python3 -m pip install --break-system-packages --upgrade pip setuptools wheel && \
	python3 -m pip install --break-system-packages --default-timeout=1000 cmake ninja numpy scipy scikit-build-core pybind11 fasteners

# Build mpi4py from source to ensure it links against the system MPI
RUN MPICC=/usr/bin/mpicc python3 -m pip install --break-system-packages --no-binary mpi4py --no-build-isolation --no-cache-dir mpi4py

# Install DDFacet from PyPI (or pinned version)
RUN if [ -n "${DDFACET_PYPI_VERSION}" ]; then \
		python3 -m pip install --break-system-packages --no-cache-dir DDFacet==${DDFACET_PYPI_VERSION}; \
	else \
		python3 -m pip install --break-system-packages --no-cache-dir DDFacet; \
	fi

# Sanity checks
RUN DDF.py --help

ENTRYPOINT []
