FROM quay.io/stimela/base:1.9.0
MAINTAINER <sphemakh@gmail.com>
RUN docker-apt-install casacore-dev \
    casacore-data \
    libboost-python-dev \
    libcfitsio-dev \
    wcslib-dev
RUN pip install --break-system-packages --no-cache-dir tricolour==0.2.1
RUN tricolour --help
