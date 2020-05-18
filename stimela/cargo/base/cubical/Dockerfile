FROM stimela/base:1.2.5
RUN docker-apt-install casacore-dev \
    casacore-data \
    build-essential \
    python3-pip \
    libboost-all-dev \
    wcslib-dev \
    git \
    libcfitsio-dev
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.6 10
RUN pip3 install --upgrade --force pip
RUN pip install "cubical[lsm-support]@git+https://github.com/ratt-ru/CubiCal.git@v1.5.3"
RUN gocubical --help
