FROM stimela/base:1.0.1
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
RUN wget https://sourceforge.net/projects/wsclean/files/wsclean-2.6/wsclean-2.6.tar.bz2
RUN tar xvf wsclean-2.6.tar.bz2 && cd wsclean-2.6
RUN mkdir wsclean-2.6/build
RUN cd wsclean-2.6/build && \
    cmake -DPORTABLE=Yes .. && \
    make -j 10 && \
    make install
RUN ulimit -p 9000
