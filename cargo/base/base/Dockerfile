FROM radioastro/base
MAINTAINER <sphemakh@gmail.com>

RUN add-apt-repository -ys ppa:radio-astro/main && apt-get install -y \
        time \
        git \
        subversion \
        python-pip

RUN pip install setuptools

# make sure child images have latest deb package cache
ONBUILD RUN apt-get update
