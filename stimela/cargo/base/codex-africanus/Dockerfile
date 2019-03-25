FROM stimela/base:1.0.1
MAINTAINER <sphemakh@gmail.com>
RUN docker-apt-install python-casacore \
    casacore-dev \
    python-numpy \
    python-setuptools \
    libboost-python-dev \
    libcfitsio-dev \
    wcslib-dev
RUN pip install pip setuptools -U
RUN pip install codex-africanus[complete]>0.1.4 xarray-ms
RUN pip install crystalball>=0.1.2
RUN crystalball -h
