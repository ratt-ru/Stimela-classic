FROM stimela/meqtrees
MAINTAINER <sphemakh@gmail.com>

RUN mkdir -p /input /output

ADD src /code
WORKDIR /output

CMD python /code/run.py
