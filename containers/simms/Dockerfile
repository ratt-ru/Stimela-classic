FROM radioastro/casapy

RUN apt-get update && apt-get install -y python-pip python-numpy
RUN pip install simms

ENV USR root

ADD src /code
ADD data /data

RUN mkdir /output

WORKDIR /code

CMD ./run.sh
