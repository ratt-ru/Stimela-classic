FROM quay.io/stimela/base:1.9.0
# casacore-dev and boost-python are needed to build python-casacore on arm64,
# where PyPI has no wheel. dask-ms 0.3 switches to arcae, so stay on 0.2.x.
RUN docker-apt-install casacore-dev \
    casacore-data \
    libboost-python-dev \
    libcfitsio-dev \
    wcslib-dev
RUN pip install --break-system-packages --no-cache-dir spimple==0.0.5 "dask-ms<0.3"
RUN spimple-spifit -h
RUN spimple-binterp -h
RUN spimple-imconv -h
