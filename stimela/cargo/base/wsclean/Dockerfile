FROM radioastro/base
MAINTAINER <sphemakh@gmail.com>

RUN apt-get update && apt-get install -y time \
    wsclean \
    python-pyxis \
    python-scipy \
    python-astlib

RUN pip install owlcat meqtrees_cattery astro-kittens -U

ENV USER root
