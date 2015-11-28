FROM penthesilea/casapy:stable.11.15
MAINTAINER <sphemakh@gmail.com>

RUN apt-get update && apt-get install -y \
        python-numpy \
        python-pyfits

RUN pip install simms

ENV USER root
