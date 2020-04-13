FROM stimela/base:1.2.5
MAINTAINER <sphemakh@gmail.com>
RUN docker-apt-install libboost-dev \
    casacore-dev \
    python3-casacore python3-pip
RUN pip3 install -U pip setuptools pyyaml
RUN pip3 install katdal[ms,s3]
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.6 10
RUN mvftoms.py -h
RUN python --version

