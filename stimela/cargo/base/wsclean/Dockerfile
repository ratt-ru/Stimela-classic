FROM stimela/base:1.6.0
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
RUN wget https://tenet.dl.sourceforge.net/project/wsclean/wsclean-2.9/wsclean-2.9.tar.bz2
RUN tar xvf wsclean-2.9.tar.bz2
RUN mkdir wsclean-2.9/build
RUN cd wsclean-2.9/build && \
    cmake .. -DPORTABLE=Yes -DCMAKE_BUILD_TYPE=Release && \
    make -j 10 && \
    make install
RUN ulimit -p 9000
RUN pip install scabha
RUN wsclean
