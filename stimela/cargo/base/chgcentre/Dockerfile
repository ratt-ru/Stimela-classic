FROM stimela/base:1.0.1
MAINTAINER <sphemakh@gmail.com>
RUN apt-get update
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
RUN wget https://sourceforge.net/projects/wsclean/files/chgcentre-1.6/chgcentre-1.6.tar.bz2
RUN tar xvf chgcentre-1.6.tar.bz2 && cd chgcentre
RUN mkdir chgcentre/build
RUN cd chgcentre/build && \
    cmake .. && \
    make -j 10 && \
    make install
RUN ulimit -p 9000
