FROM kernsuite/base:4
MAINTAINER <sphemakh@gmail.com>

RUN docker-apt-install libboost-dev \
    casacore-dev \
    python-casacore \
    git \
    python-pip

RUN pip install -U pip setuptools pyyaml
RUN git clone https://github.com/ska-sa/katdal.git /tmp/katdal
RUN pip install  /tmp/katdal[ms,s3]
