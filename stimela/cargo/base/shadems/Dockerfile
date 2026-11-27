FROM quay.io/stimela/base:1.9.0
MAINTAINER <sphemakh@gmail.com>
# shadems needs numpy 2 (via dask-ms), so python-casacore comes from pip, not
# KERN (built against numpy 1.26). casacore-dev and boost-python are needed to
# build it on arm64, where PyPI has no wheel.
RUN docker-apt-install casacore-dev \
    casacore-data \
    libboost-python-dev \
    libcfitsio-dev \
    wcslib-dev
RUN pip install --break-system-packages --no-cache-dir shadems==0.5.5
RUN python3 -c "import numpy, casacore.tables; assert numpy.__version__.startswith('2.'), numpy.__version__"
RUN shadems -h
