FROM stimela/base:0.3.1
MAINTAINER <sphemakh@gmail.com>

RUN docker-apt-install casacore-dev git python-pip
RUN docker-apt-install python-casacore
RUN pip install -U pip pkginfo
RUN pip install -I git+https://github.com/sjperkins/katdal@use-python-casacore-ms-creation#egg=katdal
