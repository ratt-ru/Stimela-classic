FROM radioastro/base
MAINTAINER <sphemakh@gmail.com>

RUN apt-get update && apt-get install git subversion time -ys
RUN pip install setuptools

# make sure child images have latest deb package cache
ONBUILD RUN apt-get update
