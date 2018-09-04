FROM kernsuite/base:4
MAINTAINER <sphemakh@gmail.com>

RUN docker-apt-install libboost-dev \
    casacore-dev \
    python-casacore \
    git \
    python-pip

RUN pip install -U pip setuptools pyyaml
RUN pip install katdal[ms,s3]
