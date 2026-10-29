FROM quay.io/stimela/base:1.9.0

# Allow pinning a PyPI version (default: latest)
ARG DDFACET_PYPI_VERSION=""
ENV PIP_BREAK_SYSTEM_PACKAGES=1

# Install apt build/runtime dependencies needed for building from source and MPI
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y \
	cmake gcc g++ git curl build-essential \
	libfftw3-dev libopenmpi-dev openmpi-bin libpmix-dev libpmi2-0-dev \
	python3-pip python3-dev libhdf5-dev libatlas-base-dev libgsl-dev libcurl4-openssl-dev \
	&& apt-get clean && rm -rf /var/lib/apt/lists/*

# Install common build-time Python tooling. pip, setuptools and wheel come from
# Debian and can't be upgraded in place by pip, so keep the system versions.
RUN python3 -m pip install --break-system-packages --default-timeout=1000 cmake ninja numpy scipy scikit-build-core pybind11 fasteners

# Build mpi4py from source to ensure it links against the system MPI
RUN MPICC=/usr/bin/mpicc python3 -m pip install --break-system-packages --no-binary mpi4py --no-cache-dir mpi4py

# Install DDFacet from PyPI (or pinned version)
RUN if [ -n "${DDFACET_PYPI_VERSION}" ]; then \
		python3 -m pip install --break-system-packages --no-cache-dir DDFacet==${DDFACET_PYPI_VERSION}; \
	else \
		python3 -m pip install --break-system-packages --no-cache-dir DDFacet; \
	fi

# Sanity checks
RUN mpirun --version && python3 -c "from mpi4py import MPI; print(MPI.Get_library_version())"
RUN DDF.py --help

ENTRYPOINT []
