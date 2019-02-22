FROM kernsuite/base:3
MAINTAINER Ben Hugo "bhugo@ska.ac.za"

# Support large mlocks
RUN echo "*        -   memlock     unlimited" > /etc/security/limits.conf
ENV DEB_SETUP_DEPENDENCIES \
    dpkg-dev \
    g++ \
    gcc \
    libc-dev \
    cmake \
    gfortran \
    git \
    wget \
    subversion

ENV DEB_DEPENCENDIES \
    python-pip \
    libfftw3-dev \
    casacore-data \
    casacore-dev \
    python-numpy \
    libfreetype6 \
    libfreetype6-dev \
    libpng12.0 \
    libpng12-dev \
    pkg-config \
    python2.7-dev \
    libboost-all-dev \
    libcfitsio3-dev \
    libhdf5-dev \
    wcslib-dev \
    libatlas-dev \
    liblapack-dev \
    python-tk \
    meqtrees* \
    tigger-lsm \
    # LOFAR Beam and including makems needed for ref image generation
    lofar \
    # Reference image generation dependencies
    make

RUN apt-get update 
RUN apt-get install -y software-properties-common 
RUN add-apt-repository -y -s ppa:kernsuite/kern-3
RUN apt-add-repository -y multiverse
RUN apt-get update
RUN apt-get install -y $DEB_SETUP_DEPENDENCIES
RUN apt-get install -y $DEB_DEPENCENDIES
RUN pip install -U "pip==9.0.3" setuptools wheel
RUN pip install -U "numpy<=1.16"
RUN pip install "ddfacet==0.3.4.1"
RUN pip install git+https://github.com/ska-sa/montblanc.git@ddfacet
RUN pip install "pymoresane >= 0.3.0"

# Set MeqTrees Cattery path to virtualenv installation directory
ENV MEQTREES_CATTERY_PATH /usr/lib/python2.7/dist-packages/Cattery/
# Execute virtual environment version of DDFacet
ENTRYPOINT ["DDF.py"]
CMD ["--help"]
