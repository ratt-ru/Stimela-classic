FROM stimela/base:1.0.1
MAINTAINER <sphemakh@gmail.com>
RUN docker-apt-install libboost-dev \
    casacore-dev \
    python-casacore
RUN pip install -U pip setuptools pyyaml
RUN pip install katdal[ms,s3]
