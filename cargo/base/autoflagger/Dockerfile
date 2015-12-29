FROM penthesilea/base:stable.11.15
MAINTAINER <sphemakh@gmail.com>

RUN apt-get build-dep aoflagger -y

ENV USER root
RUN mkdir -p /builds
RUN git clone git://git.code.sf.net/p/aoflagger/code  /builds/aoflagger
RUN mkdir -p /builds/aoflagger/build
RUN cd /builds/aoflagger/build && cmake .. && make && make install
