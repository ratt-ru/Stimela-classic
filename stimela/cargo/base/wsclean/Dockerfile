FROM kernsuite/base:dev
#until gijs updates kern2 we're going with custom build
#RUN docker-apt-install wsclean
ENV PACKAGES \
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
    libcfitsio3-dev \
    libgsl-dev \
    wcslib-dev \
    libhdf5-serial-dev \
    libfftw3-dev \
    python-numpy \
    libboost-python-dev \
    libboost-all-dev \
    libpython3.5-dev \
    libpython2.7-dev \
    liblog4cplus-dev \
    libhdf5-dev 

RUN docker-apt-install $PACKAGES && \
    mkdir -p /opt/src && \
    cd /opt/src && \
    wget https://github.com/casacore/casacore/archive/v2.3.0.tar.gz && \
    wget https://ufpr.dl.sourceforge.net/project/wsclean/wsclean-2.4/wsclean-2.4.tar.bz2 && \
    svn co --non-interactive --no-auth-cache --username lofar-guest --password lofar-guest https://svn.astron.nl/LOFAR/tags/LOFAR-Release-2_21_9 && \
    tar -xvf v2.3.0.tar.gz && \
    tar -xvf wsclean-2.4.tar.bz2 && \
    mkdir casacore-2.3.0/build && \
    mkdir wsclean-2.4/build && \
    mkdir -p LOFAR-Release-2_21_9/build/gnucxx11_opt && \
    # CASACORE
    cd casacore-2.3.0/build && \
    cmake -DCMAKE_INSTALL_PREFIX:PATH=/usr -DUSE_OPENMP=YES -DUSE_FFTW3=YES -DUSE_HDF5=YES -DCMAKE_BUILD_TYPE=Release .. && \ 
    make -j 16 && \
    make install && \
    # LOFAR STATIONS
    cd ../../LOFAR-Release-2_21_9/build/gnucxx11_opt && \
    cmake -DBUILD_PACKAGES="StationResponse" -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=/usr ../../ && \
    make -j16 && \
    make install && \
    # WSClean
    cd ../../../wsclean-2.4/build && \
    cmake -DCMAKE_INSTALL_PREFIX:PATH=/usr -DCMAKE_BUILD_TYPE=Release -DPORTABLE=Yes .. && \ 
    make -j 16 && \
    make install && \
    docker-apt-install python-yaml && \
    # Cleanup
    apt-get remove -y build-essential cmake subversion gfortran g++ && \
    rm -rf /opt/src
