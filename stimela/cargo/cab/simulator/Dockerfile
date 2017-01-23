FROM stimela/meqtrees:0.2.3
MAINTAINER <sphemakh@gmail.com>

RUN mkdir -p /input /output

ADD src /code
WORKDIR /output

CMD python /code/run.py
