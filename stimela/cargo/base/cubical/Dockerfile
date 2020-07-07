FROM stimela/base:1.6.0
RUN docker-apt-install casacore-dev \
    casacore-data \
    build-essential \
    libboost-all-dev \
    wcslib-dev \
    libcfitsio-dev
RUN pip install "cubical[lsm-support]@git+https://github.com/ratt-ru/CubiCal.git@v1.5.5" scabha
RUN gocubical --help
