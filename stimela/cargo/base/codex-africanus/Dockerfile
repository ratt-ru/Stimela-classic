FROM stimela/base:1.2.0
MAINTAINER <sphemakh@gmail.com>
RUN docker-apt-install python3-casacore \
    casacore-dev \
    python3-numpy \
    python3-setuptools \
    libboost-python-dev \
    libcfitsio-dev \
    wcslib-dev \
    python3-pip    
RUN pip3 install --upgrade pip setuptools astropy
RUN pip3 install crystalball>=0.2.2
RUN crystalball -h
