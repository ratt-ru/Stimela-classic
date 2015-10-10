FROM penthesilea/base
MAINTAINER sphemakh@gmail.com

RUN apt-get update && apt-get install -y \
    casarest \
    wsclean \
    python-pyxis \
    python-tigger

RUN mkdir /builds
RUN git clone https://github.com/ska-sa/pyxis /builds/pyxis
RUN git clone https://github.com/ska-sa/owlcat /builds/owlcat
RUN cd /builds/pyxis && python setup.py install
RUN cd /builds/owlcat && python setup.py install

ENV USER root

ADD src /code

RUN mkdir /output

WORKDIR /code

CMD ./run.sh
