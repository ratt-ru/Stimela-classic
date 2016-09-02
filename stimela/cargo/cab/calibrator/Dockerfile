FROM radioastro/meqtrees
MAINTAINER <sphemakh@gmail.com>

RUN mkdir -p /input /output
ADD src /code

ENV MEQTREES_CATTERY_PATH /usr/lib/python2.7/dist-packages/Cattery

RUN ulimit -c unlimited

WORKDIR /code

CMD sh run.sh
