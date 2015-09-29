FROM ubuntu:python
ADD . /data
WORKDIR /data
CMD python azishe.py
