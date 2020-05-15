FROM stimela/base:1.4.6
MAINTAINER <sphemakh@gmail.com>
RUN docker-apt-install python3-casacore \
    casacore-dev \
    libcfitsio-dev \
    wcslib-dev
RUN pip install git+https://github.com/ratt-ru/shadeMS.git@auto-bounds
RUN pip install git+https://github.com/o-smirnov/datashader
RUN pip install -I numpy

# so we can use use e.g. docker build --build-arg SCABHA=git+https://github.com/ratt-ru/scabha.git@branch to
# install from a dev version, instead of a release package
ARG SCABHA=scabha
RUN pip install $SCABHA

RUN shadems -h
