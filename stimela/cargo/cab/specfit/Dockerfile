FROM stimela/tigger:0.2.3
MAINTAINER <sphemakh@gmail.com>

RUN mkdir -p /input /output

ENV MEQTREES_CATTERY_PATH /usr/lib/python2.7/dist-packages/Cattery

ADD src /code

CMD python /code/run.py
