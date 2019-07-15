FROM stimela/base:1.0.1
MAINTAINER <sphemakh@gmail.com>
RUN docker-apt-install python-casacore python3-pip
ADD tricolour /tricolour
RUN pip3 install -U pip setuptools
RUN pip3 install /tricolour
