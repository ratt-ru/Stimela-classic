FROM stimela/base:1.0.0
MAINTAINER <sphemakh@gmail.com>
RUN docker-apt-install casacore-dev \
        libboost-python-dev \
        libcfitsio3-dev \
        wcslib-dev
RUN pip install -U pip setuptools wheel
RUN pip install -U numpy
RUN pip install -I git+https://github.com/ska-sa/montblanc
RUN pip install -I git+https://github.com/ratt-ru/CubiCal
ENV NUMBA_CACHE_DIR /tmp
