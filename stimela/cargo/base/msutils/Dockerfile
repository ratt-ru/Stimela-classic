FROM quay.io/stimela/base:1.9.0
MAINTAINER <sphemakh@gmail.com>
# casacore-dev and boost-python are needed to build python-casacore on arm64,
# where PyPI has no wheel
RUN docker-apt-install casacore-dev \
    casacore-data \
    libboost-python-dev \
    libcfitsio-dev \
    wcslib-dev
# msutils 3.x is a rewrite without the MSUtils module the cabs use
RUN pip install --break-system-packages --no-cache-dir msutils==1.2.0
RUN python3 -c "import MSUtils.msutils, MSUtils.ClassESW, MSUtils.imp_plotter, MSUtils.flag_stats"
