FROM stimela/base:1.0.1
MAINTAINER <sphemakh@gmail.com>
RUN docker-apt-install casacore-dev \
        libboost-python-dev \
        libcfitsio-dev \
        wcslib-dev
RUN pip install -U pip setuptools wheel
RUN docker-apt-install wget git-all
RUN git clone https://github.com/ratt-ru/CubiCal
RUN pip install cython numpy
RUN cd CubiCal && python setup.py gocythonize && pip install .
RUN pip install tensorflow==1.8.0
RUN pip install -I git+https://github.com/ska-sa/montblanc
ENV NUMBA_CACHE_DIR /tmp
