FROM quay.io/stimela/base:1.9.0
# casacore-dev and boost-python are needed to build python-casacore on arm64,
# where PyPI has no wheel
RUN docker-apt-install casacore-dev \
    casacore-data \
    libboost-python-dev \
    libcfitsio-dev \
    wcslib-dev
RUN pip install --break-system-packages --no-cache-dir \
    git+https://github.com/ratt-ru/ragavi.git@master
RUN ragavi-gains -h
RUN ragavi-vis -h
RUN ragavi-vis --version
