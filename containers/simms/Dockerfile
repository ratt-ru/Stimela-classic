FROM penthesilea/casapy

RUN apt-get update && apt-get install -y \
        python-numpy \
        python-pyfits

RUN pip install simms

ENV USER root

ADD src /code

RUN mkdir /output /input

WORKDIR /code

CMD sh run.sh
