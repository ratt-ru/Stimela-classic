FROM stimela/base:0.3.2
MAINTAINER <sphemakh@gmail.com>
RUN docker-apt-install casacore-dev \
        libboost-python-dev \
        libcfitsio3-dev \
        wcslib-dev
RUN pip install -U pip setuptools wheel
RUN pip install -U numpy
RUN pip install -I git+git://github.com/ska-sa/montblanc.git@master
