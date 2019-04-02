FROM stimela/base:1.0.1
MAINTAINER <sphemakh@gmail.com>
RUN docker-apt-install cmake \	
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
    casacore-dev \
    curl
ENV CHGCENTRE_NAME chgcentre-1.6
ENV CHGCENTRE_URL https://liquidtelecom.dl.sourceforge.net/project/wsclean/chgcentre-1.6/chgcentre-1.6.tar.bz2
RUN curl -o ${CHGCENTRE_NAME}.tar.bz2 ${CHGCENTRE_URL}
RUN mkdir /builds && tar xjf ${CHGCENTRE_NAME}.tar.bz2 -C /builds
RUN mkdir /builds/chgcentre/build
RUN cd /builds/chgcentre/build && cmake ../ -DPORTABLE=True
RUN cd  /builds/chgcentre/build && make
RUN cd /builds/chgcentre/build && make install
RUN chgcentre
