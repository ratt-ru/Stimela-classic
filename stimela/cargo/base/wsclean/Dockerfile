FROM quay.io/stimela/base:1.7.1
MAINTAINER <sphemakh@gmail.com>
RUN docker-apt-install cmake \
    wget \
    subversion \
    build-essential \
    cmake \
    gfortran \
    g++ \
    libncurses5-dev \
    libreadline-dev \
    flex \
    bison \
    libblas-dev \
    liblapacke-dev \
    libcfitsio-dev \
    libgsl-dev \
    wcslib-dev \
    libhdf5-serial-dev \
    libfftw3-dev \
    python-numpy \
    libboost-python-dev \
    libboost-all-dev \
    libpython2.7-dev \
    liblog4cplus-dev \
    libhdf5-dev \
    casacore-dev
RUN git clone --depth 1 -b v3.1 https://gitlab.com/aroffringa/wsclean.git wscleandir
RUN mkdir wscleandir/build
RUN cd wscleandir/build && \
    cmake .. -DPORTABLE=Yes -DCMAKE_BUILD_TYPE=Release && \
    make -j 10 && \
    make install
RUN ulimit -p 11000
RUN wsclean
