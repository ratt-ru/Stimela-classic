FROM stimela/base:1.2.0
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
RUN wget https://tenet.dl.sourceforge.net/project/wsclean/wsclean-2.8/wsclean-2.8.tar.bz2
RUN tar xvf wsclean-2.8.tar.bz2
RUN mkdir wsclean-2.8/build
RUN cd wsclean-2.8/build && \
    cmake .. -DPORTABLE=Yes -DCMAKE_BUILD_TYPE=Release && \
    make -j 10 && \
    make install
RUN pip install astropy
RUN ulimit -p 9000
