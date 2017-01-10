FROM stimela/wsclean:0.2.3
MAINTAINER <sphemakh@gmail.com>

ADD src /code

RUN mkdir -p /input /output

WORKDIR /output

CMD python /code/run.py
