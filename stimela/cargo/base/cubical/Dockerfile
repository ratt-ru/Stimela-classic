FROM stimela/base:1.0.1
MAINTAINER <sphemakh@gmail.com>
RUN docker-apt-install casacore-dev \
        libboost-python-dev \
        libcfitsio-dev \
        wcslib-dev
ENV GIT_LFS_SKIP_SMUDGE 1
RUN pip install -U pip setuptools wheel
RUN docker-apt-install wget git-all
RUN git clone https://github.com/ratt-ru/CubiCal
WORKDIR CubiCal
RUN git checkout 1.2.3
RUN pip install ".[lsm-support]"
ENV NUMBA_CACHE_DIR /tmp
