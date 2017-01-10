FROM stimela/simms:0.2.3
MAINTAINER <sphemakh@gmail.com>

RUN mkdir -p /output /input

ADD src /code
WORKDIR /output

CMD python /code/run.py
