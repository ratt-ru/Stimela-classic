FROM quay.io/stimela/base:1.8.0
MAINTAINER <sphemakh@gmail.com>
RUN docker-apt-install cmake \
    wget \
    subversion \
    build-essential \
    cmake \
    gfortran \
    g++ \
    git \
    libncurses5-dev \
    libreadline-dev \
    flex \
    bison \
    libblas-dev \
    liblapack-dev \
    libcfitsio-dev \
    libgsl-dev \
    wcslib-dev \
    libhdf5-serial-dev \
    libfftw3-dev \
    python3-numpy \
    libatlas3-base \
    libboost-python-dev \
    libboost-all-dev \
    libpython3-dev \
    liblog4cplus-dev \
    libhdf5-dev \
    casacore-dev
RUN git clone --depth 1 -b v3.6 https://gitlab.com/aroffringa/wsclean.git wscleandir
RUN mkdir wscleandir/build
RUN cd wscleandir/build && \
    cmake .. -DPORTABLE=Yes -DCMAKE_BUILD_TYPE=Release && \
    make -j 4 && \
    make install
RUN ulimit -p 11000
RUN wsclean
