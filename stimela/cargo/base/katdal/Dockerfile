FROM stimela/base:0.2.9
MAINTAINER <sphemakh@gmail.com>

ENV PACKAGES \
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
    libcfitsio3-dev \
    wcslib-dev \
    libhdf5-serial-dev \
    libfftw3-dev \
    python-numpy \
    libboost-python-dev \
    libpython3.5-dev \
    libpython2.7-dev

# Install packages
RUN docker-apt-install $PACKAGES

# Install custom branch of casacore
RUN git clone --depth 1 https://github.com/casacore/casacore.git -b v2.3.0 /src/casacore && \
    mkdir -p /src/casacore/build && \
    cd /src/casacore/build && \
    cmake -DCMAKE_INSTALL_PREFIX:PATH=/usr .. && \
    make -j16 && \
    make install && \
    cd / && \
    rm -rf /src

# Install custom branch of python-casacore
RUN pip install git+https://github.com/casacore/python-casacore.git@master#egg=python-casacore

# Install custom branch of katdal
RUN pip  install git+https://github.com/sjperkins/katdal.git@use-python-casacore-ms-creation#egg=katdal

