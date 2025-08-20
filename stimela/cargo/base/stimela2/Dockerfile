FROM kernsuite/base:9
MAINTAINER <ramaila.jat@gmail.com>
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
    python3-numpy \
    libboost-python-dev \
    libboost-all-dev \
    libpython2.7-dev \
    liblog4cplus-dev \
    libhdf5-dev \
    casacore-dev \
    wsclean

RUN docker-apt-install python3-pip
RUN pip install cult-cargo stimela quartical \
    aimfast \
    astro-tigger-lsm \
    bdsf \
    breizorro \
    casaconfig \
    casadata \
    casatasks \
    casatools

RUN docker-apt-install \
    git \
    xvfb \
    curl

RUN pip install -U "git+https://github.com/caracal-pipeline/stimela.git"
RUN pip install -U "git+https://github.com/caracal-pipeline/cult-cargo.git"

RUN ulimit -p 11000
RUN stimela --help

RUN ln -s /usr/bin/python3 /usr/bin/python
RUN mkdir -p /opt/casa/data
COPY casasiteconfig.py /opt/casa
ENV CASASITECONFIG /opt/casa/casasiteconfig.py
RUN python -m casaconfig --measurespath /opt/casa/data --update-all
RUN python -m casaconfig --measurespath /opt/casa/data --current-data
# point to CASA data
RUN mkdir -p /usr/local/share/data/
RUN ln -s /opt/casa/data /usr/local/share/data/casacore
COPY xvfb.init.d /etc/init.d/xvfb
RUN chmod 755 /etc/init.d/xvfb
RUN chmod 777 /var/run
ENV DISPLAY :99
