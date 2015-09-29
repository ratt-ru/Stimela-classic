FROM radioastro/casapy

RUN apt-get update && apt-get install -y python-pip python-numpy
RUN pip install simms

ADD . /code
WORKDIR /code
CMD run.sh
