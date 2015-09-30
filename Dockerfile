FROM ubuntu:14.04
RUN apt-get update && apt-get install -y python

ADD . /data
WORKDIR /data
CMD python azishe.py
