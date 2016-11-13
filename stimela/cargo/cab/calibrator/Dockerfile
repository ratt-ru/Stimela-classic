FROM stimela/meqtrees
MAINTAINER <sphemakh@gmail.com>

RUN mkdir -p /input /output
ADD src /code

RUN ulimit -c unlimited

WORKDIR /code

CMD sh run.sh
