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
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.6 10
RUN pip install git+https://github.com/ratt-ru/shadeMS.git@v0.3.0
RUN pip install git+https://github.com/o-smirnov/datashader
RUN pip install -I numpy
RUN shadems -h