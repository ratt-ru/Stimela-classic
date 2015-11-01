FROM penthesilea/base
MAINTAINER <sphemakh@gmail.com>

RUN apt-get update && apt-get install -y \
        lofar \
        python-scipy \
        python-numpy \
        python-matplotlib \
        python-tigger

RUN mkdir /builds
RUN git clone https://github.com/sphemakh/sourcery.git /builds/sourcery
RUN git clone https://github.com/ska-sa/tigger.git /builds/tigger
RUN cd /builds/sourcery && python setup.py install
RUN cd /builds/tigger && python setup.py install
ENV USER root
