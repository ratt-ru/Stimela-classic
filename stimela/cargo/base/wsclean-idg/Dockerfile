FROM ubuntu:24.04

RUN export DEBIAN_FRONTEND=noninteractive && apt-get update && \
    apt-get install -y \
    cmake \
    g++ \
    git \
    pkg-config \
    libblas-dev \
    libboost-filesystem-dev \
    libboost-program-options-dev \
    libcfitsio-dev \
    libdeflate-dev \
    libfftw3-dev \
    libgsl-dev \
    libhdf5-dev \
    liblapack-dev \
    libopenmpi-dev \
    libpython3-dev \
    pybind11-dev \
    bison \
    flex \
    gfortran \
    python3-dev \
    python3-numpy \
    libboost-python-dev \
    libreadline-dev \
    wcslib-dev \
    wget && \
    rm -rf /var/lib/apt/lists/*

# Install the casacore measures data directly from the ASTRON site.
RUN mkdir -p /usr/share/casacore/data && \
    ln -s /usr/share/casacore /var/lib/casacore && \
    wget -qO - https://www.astron.nl/iers/WSRT_Measures.ztar | \
    tar -C /usr/share/casacore/data -xzf -

# Ubuntu 24.04's casacore is too old to support C++20.
RUN mkdir -p /external && \
    cd /external && \
    git clone --depth 1 --branch v3.8.1 https://github.com/casacore/casacore.git && \
    mkdir /external/casacore/build && \
    cd /external/casacore/build && \
    cmake .. -DBUILD_TESTING=OFF -DDATA_DIR=/usr/share/casacore/data && \
    make -j"$(nproc)" && \
    make install -j"$(nproc)" && \
    rm -rf /external/casacore

# EveryBeam and IDG are required for WSClean's IDG backend.
RUN cd /external && \
    git clone --depth 1 --branch v0.7.4 https://git.astron.nl/RD/EveryBeam.git && \
    mkdir /external/EveryBeam/build && \
    cd /external/EveryBeam/build && \
    cmake .. -DPORTABLE=ON && \
    make -j"$(nproc)" && \
    make install && \
    rm -rf /external/EveryBeam

RUN cd /external && \
    git clone --depth 1 https://git.astron.nl/RD/idg.git && \
    mkdir /external/idg/build && \
    cd /external/idg/build && \
    cmake .. -DPORTABLE=ON && \
    make -j"$(nproc)" && \
    make install && \
    rm -rf /external/idg

RUN git clone --depth 1 --branch v3.7 https://gitlab.com/aroffringa/wsclean.git /wsclean && \
    mkdir /wsclean/build && \
    cd /wsclean/build && \
    cmake .. -DCMAKE_BUILD_TYPE=Release -DPORTABLE=Yes && \
    make -j"$(nproc)" && \
    make install && \
    ldconfig && \
    cd / && \
    rm -rf /wsclean && \
    wsclean --version
