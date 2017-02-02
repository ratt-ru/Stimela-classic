FROM radioastro/base
MAINTAINER <sphemakh@gmail.com>

RUN apt-add-repository -s ppa:radio-astro/main && \
    apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y git-core \
        libpython-dev \
        libcasacore2-dev \
        libboost-python-dev \
        libcfitsio3-dev \
        wget && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Force upgrade of pip since pip install --upgrade pip doesn't work
RUN easy_install -U pip setuptools==30.1.0

RUN pip install -I -U git+git://github.com/ska-sa/katdal.git \
    python-casacore pyyaml

RUN mkdir -p /var/kat/static && wget https://github.com/ska-sa/katdal/raw/master/blank.ms.tgz -O - | tar -C ./var/kat/static -xzvf -

