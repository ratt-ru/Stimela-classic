FROM stimela/base
MAINTAINER <sphemakh@gmail.com>

RUN apt-get update && apt-get install -y \
    time \
    casarest \
    python-pyxis \
    python-astlib

RUN pip install owlcat meqtrees_cattery astro-kittens -U

ENV USER root
