FROM quay.io/stimela/base:1.9.0
RUN docker-apt-install build-essential \
        wcslib-dev \
        casacore-dev \
        casacore-data \
        libboost-python-dev \
        libcfitsio-dev
RUN git clone --depth 1 --branch v2.7.1 https://gitlab.com/SoFiA-Admin/SoFiA-2.git /SoFiA-2 && \
    cd /SoFiA-2 && make OMP=true && make install && \
    rm -rf /SoFiA-2
RUN pip install --break-system-packages --no-cache-dir astro-tigger-lsm astLib
RUN sofia -h
RUN python3 -c "import Tigger; from astLib.astWCS import WCS"
