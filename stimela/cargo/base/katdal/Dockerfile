FROM quay.io/stimela/base:1.9.0
MAINTAINER <sphemakh@gmail.com>
# katdal and its dependencies (python-casacore, katpoint, katsdptelstate, ...)
# come prebuilt from KERN 10 for amd64 and arm64
RUN docker-apt-install python3-katdal \
    python3-casacore \
    casacore-data
ENV NUMBA_CACHE_DIR=/tmp
RUN mvftoms.py -h
