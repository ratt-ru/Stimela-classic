FROM penthesilea/casapy
MAINTAINER sphemakh@gmail.com

RUN apt-get update && apt-get install -y \
        python-casacore \
        casarest \
        python-pyfits \
        python-tigger

ENV USER root

RUN mkdir /builds
RUN git clone https://github.com/ska-sa/pyxis /builds/pyxis
RUN git clone https://github.com/ska-sa/owlcat /builds/owlcat
RUN cd /builds/pyxis && python setup.py install
RUN cd /builds/owlcat && python setup.py install


RUN mkdir /input /output

ADD src /code

WORKDIR /code

CMD sh run.sh
