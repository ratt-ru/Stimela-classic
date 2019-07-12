FROM stimela/base:1.0.1
MAINTAINER <sphemakh@gmail.com>
RUN docker-apt-install python-casacore \
    casacore-dev \
    python-numpy \
    python-setuptools \
    libboost-python-dev \
    libcfitsio-dev \
    wcslib-dev
RUN pip install --upgrade pip setuptools astropy
RUN pip install crystalball>=0.1.2
RUN crystalball -h
