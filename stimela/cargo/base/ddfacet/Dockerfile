FROM stimela/base:0.3.2
MAINTAINER Ben Hugo "bhugo@ska.ac.za"

#Package dependencies
COPY apt.sources.list /etc/apt/sources.list

#Setup environment
ENV DDFACET_TEST_DATA_DIR /test_data
ENV DDFACET_TEST_OUTPUT_DIR /test_output

#Copy DDFacet and SkyModel into the image
ADD DDFacet /src/DDFacet/DDFacet
ADD SkyModel /src/DDFacet/SkyModel
ADD MANIFEST.in /src/DDFacet/MANIFEST.in
ADD requirements.txt /src/DDFacet/requirements.txt
ADD setup.py /src/DDFacet/setup.py
ADD setup.cfg /src/DDFacet/setup.cfg
ADD README.rst /src/DDFacet/README.rst
ADD .git /src/DDFacet/.git
ADD .gitignore /src/DDFacet/.gitignore
ADD .gitmodules /src/DDFacet/.gitmodules

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
    # LOFAR Beam and including makems needed for ref image generation
    lofar \
    # Reference image generation dependencies
    make

RUN apt-get update && \
    apt-get install -y software-properties-common && \
    add-apt-repository -y -s ppa:kernsuite/kern-3 && \
    apt-add-repository -y multiverse && \
    apt-get update && \
    apt-get install -y $DEB_SETUP_DEPENDENCIES && \
    apt-get install -y $DEB_DEPENCENDIES && \
    #Setup a virtual environment for the python packages
    pip install -U pip virtualenv setuptools wheel && \
    virtualenv --system-site-packages /ddfvenv && \
    # Install Montblanc and all other optional dependencies
    pip install -r /src/DDFacet/requirements.txt && \
    cd /src/DDFacet/ && git submodule update --init --recursive && cd / && \
    # Activate virtual environment
    . /ddfvenv/bin/activate && \
    # Finally install DDFacet
    rm -rf /src/DDFacet/DDFacet/cbuild && \
    pip install -I --force-reinstall --no-binary :all: /src/DDFacet/ && \
    # Nuke the unused & cached binaries needed for compilation, etc.
    rm -r /src/DDFacet && \
    apt-get remove -y $DEB_SETUP_DEPENDENCIES && \
    apt-get autoclean -y && \
    apt-get clean -y && \
    apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/* && \
    rm -rf /root/.cache/ && \
    rm -rf /var/cache/ && \
    rm -rf LOFAR-Release-2_21_9

# Set MeqTrees Cattery path to virtualenv installation directory
ENV MEQTREES_CATTERY_PATH /ddfvenv/lib/python2.7/site-packages/Cattery/
ENV PATH /ddfvenv/bin:$PATH
ENV LD_LIBRARY_PATH /ddfvenv/lib:$LD_LIBRARY_PATH
# Execute virtual environment version of DDFacet
ENTRYPOINT ["DDF.py"]
CMD ["--help"]
