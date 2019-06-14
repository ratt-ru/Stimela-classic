FROM stimela/base:1.0.1
MAINTAINER <sphemakh@gmail.com>
RUN docker-apt-install python-casacore \
    casacore-dev \
    python-numpy \
    python-setuptools \
    libboost-python-dev \
    libcfitsio-dev \
    wcslib-dev
ADD codex-africanus /codex
RUN pip install --upgrade pip setuptools astropy
RUN pip install /codex[complete]>=0.1.7 xarray-ms
RUN pip install crystalball>=0.1.2
RUN crystalball -h
