FROM stimela/base:1.2.5
MAINTAINER <sphemakh@gmail.com>
RUN docker-apt-install python3-casacore \
    casacore-dev \
    python3-numpy \
    python3-setuptools \
    libboost-python-dev \
    libcfitsio-dev \
    wcslib-dev \
    python3-pip    
RUN pip3 install --upgrade pip setuptools astropy pyyaml
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.6 10
RUN pip3 install crystalball>=0.2.4
RUN crystalball -h
