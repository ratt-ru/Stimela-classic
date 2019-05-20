FROM stimela/base:1.0.1
MAINTAINER <sphemakh@gmail.com>
RUN docker-apt-install casacore-dev \
        libboost-python-dev \
        libcfitsio-dev \
        wcslib-dev
RUN pip install -U pip setuptools wheel
RUN docker-apt-install wget git-all
RUN echo whatever8
RUN git clone https://github.com/ratt-ru/CubiCal
#RUN cd CubiCal && git remote add ulricharmel https://github.com/ulricharmel/CubiCal.git && git fetch ulricharmel
#RUN cd CubiCal && git checkout ulricharmel/master
RUN cd CubiCal && git checkout pol-cal-robust-merge
RUN pip install cython numpy
RUN cd CubiCal && python setup.py gocythonize && pip install .
RUN pip install tensorflow==1.8.0
RUN pip install -I git+https://github.com/ska-sa/montblanc@ddfacet
ENV NUMBA_CACHE_DIR /tmp
