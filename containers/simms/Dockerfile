FROM radioastro/casapy

ENV DEBIAN_FRONTEND noninteractive

# enable universe, multiverse,
# restricted with world wide mirrors
RUN apt-get update
RUN apt-get install -y software-properties-common python-software-properties

## add radioastro PPA
RUN add-apt-repository -y ppa:radio-astro/main
RUN apt-get update

## cleanup package cache
RUN apt-get clean

# make sure child images have latest deb
# package cache
ONBUILD RUN apt-get update

# simms dependencies
RUN apt-get install -y python-pip python-numpy python-pyrap
RUN pip install simms

ADD . /code
WORKDIR /code
CMD run.sh
