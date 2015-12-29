FROM radioastro/casapy
MAINTAINER <sphemakh@gmail.com>

ENV DEBIAN_FRONTEND noninteractive

ADD apt.sources.list /etc/apt/sources.list
RUN apt-get update 
RUN apt-get upgrade -y

RUN apt-get install -y software-properties-common python-software-properties

RUN add-apt-repository -ys ppa:radio-astro/main

RUN apt-get update && apt-get install -y \
        time \
        git \
        subversion \
        python-pip

