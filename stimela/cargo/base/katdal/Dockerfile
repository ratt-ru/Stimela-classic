FROM stimela/base:1.0.0
MAINTAINER <sphemakh@gmail.com>

RUN docker-apt-install casacore-dev python-casacore git python-pip
RUN pip install -U pip pkginfo pyyaml
RUN pip install -I git+https://github.com/ska-sa/katdal
