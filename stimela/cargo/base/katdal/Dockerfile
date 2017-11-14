FROM kernsuite/base:3
MAINTAINER <sphemakh@gmail.com>

RUN docker-apt-install casacore-dev git python-pip
RUN docker-apt-install python-casacore
RUN pip install -I git+https://github.com/sjperkins/katdal@use-python-casacore-ms-creation
