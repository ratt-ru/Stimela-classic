FROM quay.io/stimela/base:1.9.0
# gfortran and Boost.Python/NumPy are needed to build bdsf on arm64, where
# PyPI has no wheel; casacore-dev for python-casacore (via astro-tigger-lsm)
RUN docker-apt-install gfortran \
    g++ \
    python3-dev \
    libboost-python-dev \
    libboost-numpy-dev \
    casacore-dev \
    casacore-data \
    libcfitsio-dev \
    wcslib-dev
RUN pip install --break-system-packages --no-cache-dir bdsf==1.14.1 astro-tigger-lsm astLib
RUN python3 -c "import bdsf, Tigger; from astLib import astWCS"
